"""
Security Models - HIPAA compliance and encryption
"""

from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import json
from django.core.exceptions import ValidationError


class EncryptedField(models.TextField):
    """
    Custom field for encrypting sensitive data at rest
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def from_db_value(self, value, expression, connection):
        """Decrypt value when reading from database"""
        if value is None:
            return value
        return self._decrypt(value)
    
    def to_python(self, value):
        """Convert value to Python object"""
        if isinstance(value, str):
            return value
        if value is None:
            return value
        return str(value)
    
    def get_prep_value(self, value):
        """Encrypt value before saving to database"""
        if value is None:
            return value
        return self._encrypt(str(value))
    
    def _get_encryption_key(self):
        """Get encryption key from settings"""
        key = getattr(settings, 'HIPAA_SETTINGS', {}).get('ENCRYPTION_KEY')
        if not key:
            raise ValidationError("Encryption key not configured")
        
        # Derive key from password using PBKDF2
        password = key.encode()
        salt = b'medical_history_salt'  # In production, use random salt per record
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        return key
    
    def _encrypt(self, value):
        """Encrypt a value"""
        if not value:
            return value
        
        key = self._get_encryption_key()
        f = Fernet(key)
        encrypted_value = f.encrypt(value.encode())
        return base64.urlsafe_b64encode(encrypted_value).decode()
    
    def _decrypt(self, value):
        """Decrypt a value"""
        if not value:
            return value
        
        try:
            key = self._get_encryption_key()
            f = Fernet(key)
            encrypted_value = base64.urlsafe_b64decode(value.encode())
            decrypted_value = f.decrypt(encrypted_value)
            return decrypted_value.decode()
        except Exception as e:
            # Log the error but don't expose it to prevent information leakage
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Decryption error: {str(e)}")
            return None


class UserSession(models.Model):
    """
    Track user sessions for security monitoring
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    session_key = models.CharField(max_length=40, unique=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    logout_reason = models.CharField(max_length=50, blank=True)
    
    class Meta:
        db_table = 'user_sessions'
        ordering = ['-last_activity']
    
    def __str__(self):
        return f"{self.user.username} - {self.session_key}"


class SecurityEvent(models.Model):
    """
    Log security events for monitoring and compliance
    """
    EVENT_TYPES = [
        ('LOGIN_SUCCESS', 'Successful Login'),
        ('LOGIN_FAILED', 'Failed Login'),
        ('LOGOUT', 'Logout'),
        ('PASSWORD_CHANGE', 'Password Changed'),
        ('PERMISSION_DENIED', 'Permission Denied'),
        ('DATA_ACCESS', 'Data Access'),
        ('DATA_MODIFICATION', 'Data Modification'),
        ('ENCRYPTION_ERROR', 'Encryption Error'),
        ('SUSPICIOUS_ACTIVITY', 'Suspicious Activity'),
        ('SYSTEM_ERROR', 'System Error'),
    ]
    
    SEVERITY_LEVELS = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical'),
    ]
    
    event_type = models.CharField(max_length=30, choices=EVENT_TYPES)
    severity = models.CharField(max_length=10, choices=SEVERITY_LEVELS, default='MEDIUM')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    description = models.TextField()
    details = models.JSONField(default=dict)
    timestamp = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False)
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='resolved_events')
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolution_notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'security_events'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['event_type', 'timestamp']),
            models.Index(fields=['severity', 'timestamp']),
            models.Index(fields=['user', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.get_event_type_display()} - {self.timestamp}"


class DataAccessRequest(models.Model):
    """
    Track requests for patient data access
    """
    REQUEST_TYPES = [
        ('TREATMENT', 'Treatment'),
        ('PAYMENT', 'Payment'),
        ('HEALTHCARE_OPERATIONS', 'Healthcare Operations'),
        ('RESEARCH', 'Research'),
        ('LEGAL', 'Legal'),
        ('EMERGENCY', 'Emergency'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('DENIED', 'Denied'),
        ('EXPIRED', 'Expired'),
    ]
    
    requester = models.ForeignKey(User, on_delete=models.CASCADE, related_name='data_requests')
    patient = models.ForeignKey('patients.Patient', on_delete=models.CASCADE, related_name='access_requests')
    request_type = models.CharField(max_length=30, choices=REQUEST_TYPES)
    purpose = models.TextField()
    data_requested = models.JSONField(default=list)  # List of data fields requested
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    requested_at = models.DateTimeField(auto_now_add=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_requests')
    approved_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField()
    access_granted_at = models.DateTimeField(null=True, blank=True)
    access_revoked_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'data_access_requests'
        ordering = ['-requested_at']
    
    def __str__(self):
        return f"{self.requester.username} - {self.patient.patient_id} - {self.get_status_display()}"


class EncryptionKey(models.Model):
    """
    Manage encryption keys for data security
    """
    key_name = models.CharField(max_length=100, unique=True)
    key_value = models.TextField()  # Encrypted key
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)
    is_active = models.BooleanField(default=True)
    rotation_date = models.DateTimeField()
    
    class Meta:
        db_table = 'encryption_keys'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.key_name} - {self.created_at}"


class HIPAAComplianceLog(models.Model):
    """
    Track HIPAA compliance activities
    """
    ACTIVITY_TYPES = [
        ('DATA_BREACH', 'Data Breach'),
        ('UNAUTHORIZED_ACCESS', 'Unauthorized Access'),
        ('ENCRYPTION_FAILURE', 'Encryption Failure'),
        ('AUDIT_REVIEW', 'Audit Review'),
        ('TRAINING_COMPLETED', 'Training Completed'),
        ('POLICY_UPDATE', 'Policy Update'),
        ('RISK_ASSESSMENT', 'Risk Assessment'),
    ]
    
    activity_type = models.CharField(max_length=30, choices=ACTIVITY_TYPES)
    description = models.TextField()
    affected_patients = models.JSONField(default=list)  # List of patient IDs affected
    severity = models.CharField(max_length=10, choices=SecurityEvent.SEVERITY_LEVELS)
    reported_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reported_incidents')
    reported_at = models.DateTimeField(auto_now_add=True)
    investigated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='investigated_incidents')
    investigation_notes = models.TextField(blank=True)
    resolution = models.TextField(blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    follow_up_required = models.BooleanField(default=False)
    follow_up_date = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'hipaa_compliance_logs'
        ordering = ['-reported_at']
    
    def __str__(self):
        return f"{self.get_activity_type_display()} - {self.reported_at}"