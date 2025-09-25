"""
Audit Models - Comprehensive audit trail for HIPAA compliance
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
import uuid
import json


class AuditLog(models.Model):
    """
    Comprehensive audit log for all system activities
    """
    ACTION_TYPES = [
        ('CREATE', 'Create'),
        ('READ', 'Read'),
        ('UPDATE', 'Update'),
        ('DELETE', 'Delete'),
        ('LOGIN', 'Login'),
        ('LOGOUT', 'Logout'),
        ('EXPORT', 'Export'),
        ('PRINT', 'Print'),
        ('ACCESS', 'Access'),
        ('PERMISSION_DENIED', 'Permission Denied'),
        ('SECURITY_EVENT', 'Security Event'),
        ('DATA_BREACH', 'Data Breach'),
        ('CONFIGURATION_CHANGE', 'Configuration Change'),
        ('USER_MANAGEMENT', 'User Management'),
        ('SYSTEM_ERROR', 'System Error'),
    ]
    
    SEVERITY_LEVELS = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # User and Session Information
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='audit_logs')
    session_id = models.CharField(max_length=100, blank=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    
    # Action Details
    action = models.CharField(max_length=50, choices=ACTION_TYPES)
    resource_type = models.CharField(max_length=100)  # Model name or resource type
    resource_id = models.CharField(max_length=100, blank=True)  # Object ID
    resource_name = models.CharField(max_length=200, blank=True)  # Human-readable name
    
    # Content Type for generic foreign key
    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Change Details
    old_values = models.JSONField(default=dict, blank=True)
    new_values = models.JSONField(default=dict, blank=True)
    changed_fields = models.JSONField(default=list, blank=True)
    
    # Additional Information
    description = models.TextField(blank=True)
    details = models.JSONField(default=dict, blank=True)
    severity = models.CharField(max_length=10, choices=SEVERITY_LEVELS, default='MEDIUM')
    
    # Timestamps
    timestamp = models.DateTimeField(auto_now_add=True)
    duration_ms = models.IntegerField(null=True, blank=True)  # Action duration in milliseconds
    
    # Compliance Information
    hipaa_relevant = models.BooleanField(default=False)
    phi_accessed = models.BooleanField(default=False)  # Protected Health Information
    business_justification = models.TextField(blank=True)
    
    # Data Retention
    retention_until = models.DateTimeField(null=True, blank=True)
    archived = models.BooleanField(default=False)
    archived_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'audit_logs'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['action', 'timestamp']),
            models.Index(fields=['resource_type', 'timestamp']),
            models.Index(fields=['ip_address', 'timestamp']),
            models.Index(fields=['hipaa_relevant', 'timestamp']),
            models.Index(fields=['phi_accessed', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.user.username if self.user else 'System'} - {self.action} - {self.resource_type} - {self.timestamp}"
    
    def save(self, *args, **kwargs):
        """Override save to set retention period"""
        if not self.retention_until:
            # Set retention period based on HIPAA requirements (7 years)
            self.retention_until = timezone.now() + timezone.timedelta(days=2555)
        super().save(*args, **kwargs)


class DataAccessLog(models.Model):
    """
    Specific log for patient data access
    """
    ACCESS_TYPES = [
        ('VIEW', 'View'),
        ('CREATE', 'Create'),
        ('UPDATE', 'Update'),
        ('DELETE', 'Delete'),
        ('EXPORT', 'Export'),
        ('PRINT', 'Print'),
        ('SHARE', 'Share'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='data_access_logs')
    patient = models.ForeignKey('patients.Patient', on_delete=models.CASCADE, related_name='access_logs')
    
    # Access Details
    access_type = models.CharField(max_length=20, choices=ACCESS_TYPES)
    data_fields_accessed = models.JSONField(default=list)  # List of specific fields accessed
    purpose = models.CharField(max_length=200, blank=True)
    business_justification = models.TextField(blank=True)
    
    # Technical Details
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    session_id = models.CharField(max_length=100, blank=True)
    request_id = models.CharField(max_length=100, blank=True)
    
    # Timestamps
    access_start = models.DateTimeField(auto_now_add=True)
    access_end = models.DateTimeField(null=True, blank=True)
    duration_seconds = models.IntegerField(null=True, blank=True)
    
    # Compliance
    consent_verified = models.BooleanField(default=False)
    minimum_necessary = models.BooleanField(default=True)
    hipaa_compliant = models.BooleanField(default=True)
    
    # Risk Assessment
    risk_level = models.CharField(max_length=20, choices=[
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical'),
    ], default='LOW')
    
    # Additional Information
    notes = models.TextField(blank=True)
    follow_up_required = models.BooleanField(default=False)
    follow_up_date = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'data_access_logs'
        ordering = ['-access_start']
        indexes = [
            models.Index(fields=['user', 'access_start']),
            models.Index(fields=['patient', 'access_start']),
            models.Index(fields=['access_type', 'access_start']),
            models.Index(fields=['risk_level', 'access_start']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.access_type} - {self.patient.patient_id} - {self.access_start}"


class ComplianceReport(models.Model):
    """
    Compliance reports and assessments
    """
    REPORT_TYPES = [
        ('HIPAA_AUDIT', 'HIPAA Audit'),
        ('ACCESS_REVIEW', 'Access Review'),
        ('SECURITY_ASSESSMENT', 'Security Assessment'),
        ('DATA_BREACH_ANALYSIS', 'Data Breach Analysis'),
        ('USER_ACTIVITY_REVIEW', 'User Activity Review'),
        ('SYSTEM_COMPLIANCE', 'System Compliance'),
    ]
    
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('REVIEWED', 'Reviewed'),
        ('APPROVED', 'Approved'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Report Information
    report_type = models.CharField(max_length=30, choices=REPORT_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    
    # Report Period
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    generated_at = models.DateTimeField(auto_now_add=True)
    generated_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='generated_reports')
    
    # Report Content
    findings = models.JSONField(default=dict)
    recommendations = models.JSONField(default=list)
    compliance_score = models.IntegerField(null=True, blank=True)
    risk_assessment = models.JSONField(default=dict)
    
    # Review Information
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_reports')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_notes = models.TextField(blank=True)
    
    # Approval
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_reports')
    approved_at = models.DateTimeField(null=True, blank=True)
    approval_notes = models.TextField(blank=True)
    
    # Follow-up
    follow_up_required = models.BooleanField(default=False)
    follow_up_date = models.DateTimeField(null=True, blank=True)
    follow_up_actions = models.JSONField(default=list)
    
    class Meta:
        db_table = 'compliance_reports'
        ordering = ['-generated_at']
    
    def __str__(self):
        return f"{self.get_report_type_display()} - {self.title} - {self.generated_at}"


class DataRetentionPolicy(models.Model):
    """
    Data retention policies for different types of data
    """
    DATA_TYPES = [
        ('PATIENT_DEMOGRAPHICS', 'Patient Demographics'),
        ('MEDICAL_HISTORY', 'Medical History'),
        ('CLINICAL_DATA', 'Clinical Data'),
        ('AUDIT_LOGS', 'Audit Logs'),
        ('SECURITY_EVENTS', 'Security Events'),
        ('USER_SESSIONS', 'User Sessions'),
        ('BACKUP_DATA', 'Backup Data'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Policy Information
    data_type = models.CharField(max_length=30, choices=DATA_TYPES, unique=True)
    retention_period_years = models.IntegerField()
    retention_period_days = models.IntegerField(null=True, blank=True)
    auto_delete = models.BooleanField(default=False)
    
    # Legal Requirements
    legal_basis = models.TextField()
    regulatory_requirements = models.JSONField(default=list)
    exceptions = models.JSONField(default=list)
    
    # Implementation
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='created_retention_policies')
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='updated_retention_policies')
    
    # Monitoring
    last_cleanup = models.DateTimeField(null=True, blank=True)
    records_cleaned = models.IntegerField(default=0)
    next_cleanup = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'data_retention_policies'
        ordering = ['data_type']
    
    def __str__(self):
        return f"{self.get_data_type_display()} - {self.retention_period_years} years"


class AuditTrail(models.Model):
    """
    Detailed audit trail for specific objects
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Object Information
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Change Information
    field_name = models.CharField(max_length=100)
    old_value = models.TextField(blank=True)
    new_value = models.TextField(blank=True)
    change_type = models.CharField(max_length=20, choices=[
        ('CREATE', 'Create'),
        ('UPDATE', 'Update'),
        ('DELETE', 'Delete'),
    ])
    
    # User Information
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField()
    
    # Additional Information
    reason = models.CharField(max_length=200, blank=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'audit_trails'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['content_type', 'object_id', 'timestamp']),
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['field_name', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.content_object} - {self.field_name} - {self.change_type} - {self.timestamp}"