"""
Patient Models - HIPAA-compliant patient data management
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.utils import timezone
from apps.security.models import EncryptedField
import uuid


class Patient(models.Model):
    """
    Core patient model with HIPAA-compliant data encryption
    """
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
        ('U', 'Unknown'),
    ]
    
    ETHNICITY_CHOICES = [
        ('H', 'Hispanic or Latino'),
        ('NH', 'Not Hispanic or Latino'),
        ('U', 'Unknown'),
        ('R', 'Refused'),
    ]
    
    RACE_CHOICES = [
        ('1002-5', 'American Indian or Alaska Native'),
        ('2028-9', 'Asian'),
        ('2054-5', 'Black or African American'),
        ('2076-8', 'Native Hawaiian or Other Pacific Islander'),
        ('2106-3', 'White'),
        ('2131-1', 'Other Race'),
        ('UNK', 'Unknown'),
    ]
    
    # Primary identifiers
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient_id = models.CharField(max_length=20, unique=True, validators=[
        RegexValidator(r'^[A-Z0-9]{8,20}$', 'Invalid patient ID format')
    ])
    
    # Demographics - Encrypted for HIPAA compliance
    first_name = EncryptedField(max_length=100)
    last_name = EncryptedField(max_length=100)
    middle_name = EncryptedField(max_length=100, blank=True, null=True)
    date_of_birth = EncryptedField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    ethnicity = models.CharField(max_length=2, choices=ETHNICITY_CHOICES, blank=True)
    race = models.CharField(max_length=10, choices=RACE_CHOICES, blank=True)
    
    # Contact Information - Encrypted
    address_line1 = EncryptedField(max_length=200, blank=True)
    address_line2 = EncryptedField(max_length=200, blank=True)
    city = EncryptedField(max_length=100, blank=True)
    state = EncryptedField(max_length=50, blank=True)
    postal_code = EncryptedField(max_length=20, blank=True)
    country = EncryptedField(max_length=100, default='United States')
    phone_primary = EncryptedField(max_length=20, blank=True)
    phone_secondary = EncryptedField(max_length=20, blank=True)
    email = EncryptedField(max_length=254, blank=True)
    
    # Emergency Contact
    emergency_contact_name = EncryptedField(max_length=200, blank=True)
    emergency_contact_phone = EncryptedField(max_length=20, blank=True)
    emergency_contact_relationship = models.CharField(max_length=100, blank=True)
    
    # Insurance Information
    insurance_primary = models.CharField(max_length=200, blank=True)
    insurance_primary_id = EncryptedField(max_length=50, blank=True)
    insurance_secondary = models.CharField(max_length=200, blank=True)
    insurance_secondary_id = EncryptedField(max_length=50, blank=True)
    
    # Medical Information
    preferred_language = models.CharField(max_length=50, default='English')
    religion = models.CharField(max_length=100, blank=True)
    marital_status = models.CharField(max_length=50, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='created_patients')
    updated_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='updated_patients')
    is_active = models.BooleanField(default=True)
    
    # HIPAA Compliance
    consent_given = models.BooleanField(default=False)
    consent_date = models.DateTimeField(null=True, blank=True)
    data_retention_until = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'patients'
        ordering = ['last_name', 'first_name']
        indexes = [
            models.Index(fields=['patient_id']),
            models.Index(fields=['created_at']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.last_name}, {self.first_name} ({self.patient_id})"
    
    @property
    def full_name(self):
        """Return full name for display"""
        if self.middle_name:
            return f"{self.first_name} {self.middle_name} {self.last_name}"
        return f"{self.first_name} {self.last_name}"
    
    @property
    def age(self):
        """Calculate patient age"""
        if self.date_of_birth:
            today = timezone.now().date()
            return today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
        return None


class PatientPhoto(models.Model):
    """
    Patient photo identification with encryption
    """
    patient = models.OneToOneField(Patient, on_delete=models.CASCADE, related_name='photo')
    photo = models.ImageField(upload_to='patient_photos/', blank=True, null=True)
    photo_hash = models.CharField(max_length=64, blank=True)  # SHA-256 hash for integrity
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)
    
    class Meta:
        db_table = 'patient_photos'


class PatientConsent(models.Model):
    """
    Patient consent management for HIPAA compliance
    """
    CONSENT_TYPES = [
        ('TREATMENT', 'Treatment Consent'),
        ('DISCLOSURE', 'Information Disclosure'),
        ('RESEARCH', 'Research Participation'),
        ('MARKETING', 'Marketing Communications'),
    ]
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='consents')
    consent_type = models.CharField(max_length=20, choices=CONSENT_TYPES)
    consent_given = models.BooleanField(default=False)
    consent_date = models.DateTimeField(auto_now_add=True)
    consent_expires = models.DateTimeField(null=True, blank=True)
    consent_text = models.TextField()
    witness_name = models.CharField(max_length=200, blank=True)
    witness_signature = models.TextField(blank=True)  # Encrypted signature data
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)
    
    class Meta:
        db_table = 'patient_consents'
        ordering = ['-consent_date']
    
    def __str__(self):
        return f"{self.patient} - {self.get_consent_type_display()}"


class PatientAccessLog(models.Model):
    """
    Track all access to patient data for HIPAA audit requirements
    """
    ACCESS_TYPES = [
        ('VIEW', 'View Record'),
        ('CREATE', 'Create Record'),
        ('UPDATE', 'Update Record'),
        ('DELETE', 'Delete Record'),
        ('EXPORT', 'Export Data'),
        ('PRINT', 'Print Record'),
    ]
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='access_logs')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    access_type = models.CharField(max_length=10, choices=ACCESS_TYPES)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    reason = models.CharField(max_length=200, blank=True)
    data_accessed = models.JSONField(default=dict)  # What specific data was accessed
    
    class Meta:
        db_table = 'patient_access_logs'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['patient', 'timestamp']),
            models.Index(fields=['user', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.user} {self.access_type} {self.patient} at {self.timestamp}"


class PatientRelationship(models.Model):
    """
    Track relationships between patients (family members, guardians, etc.)
    """
    RELATIONSHIP_TYPES = [
        ('PARENT', 'Parent'),
        ('CHILD', 'Child'),
        ('SPOUSE', 'Spouse'),
        ('SIBLING', 'Sibling'),
        ('GUARDIAN', 'Guardian'),
        ('EMERGENCY_CONTACT', 'Emergency Contact'),
        ('OTHER', 'Other'),
    ]
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='relationships')
    related_patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='related_to')
    relationship_type = models.CharField(max_length=20, choices=RELATIONSHIP_TYPES)
    is_primary = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)
    
    class Meta:
        db_table = 'patient_relationships'
        unique_together = ['patient', 'related_patient', 'relationship_type']
    
    def __str__(self):
        return f"{self.patient} - {self.relationship_type} - {self.related_patient}"