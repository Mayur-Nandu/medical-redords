"""
Core models and abstract base classes for the medical history application.
"""
from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid


class TimestampedModel(models.Model):
    """
    Abstract base class with timestamp fields for audit trail.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True


class AuditableModel(TimestampedModel):
    """
    Abstract base class with full audit capabilities.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='%(class)s_created',
        null=True,
        blank=True
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='%(class)s_updated',
        null=True,
        blank=True
    )
    version = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        abstract = True
    
    def save(self, *args, **kwargs):
        """
        Override save to increment version on updates.
        """
        if self.pk:
            self.version += 1
        super().save(*args, **kwargs)


class DataSource(models.Model):
    """
    Tracks the source of medical data for reliability scoring.
    """
    SOURCE_TYPES = [
        ('patient_interview', 'Patient Interview'),
        ('previous_records', 'Previous Medical Records'),
        ('family_report', 'Family Member Report'),
        ('physician_examination', 'Physician Examination'),
        ('lab_results', 'Laboratory Results'),
        ('imaging_results', 'Imaging Results'),
        ('pharmacy_records', 'Pharmacy Records'),
        ('insurance_claims', 'Insurance Claims'),
        ('other', 'Other'),
    ]
    
    RELIABILITY_SCORES = [
        (1, 'Unreliable'),
        (2, 'Low Reliability'),
        (3, 'Moderate Reliability'),
        (4, 'High Reliability'),
        (5, 'Verified'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    source_type = models.CharField(max_length=50, choices=SOURCE_TYPES)
    reliability_score = models.IntegerField(choices=RELIABILITY_SCORES, default=3)
    description = models.TextField(blank=True)
    date_obtained = models.DateTimeField(default=timezone.now)
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )
    
    class Meta:
        db_table = 'core_data_source'
    
    def __str__(self):
        return f"{self.get_source_type_display()} - {self.get_reliability_score_display()}"


class MedicalCode(models.Model):
    """
    Standard medical codes (ICD-10, CPT, SNOMED CT, etc.).
    """
    CODE_SYSTEMS = [
        ('icd10', 'ICD-10'),
        ('icd11', 'ICD-11'),
        ('cpt', 'CPT'),
        ('snomed', 'SNOMED CT'),
        ('loinc', 'LOINC'),
        ('rxnorm', 'RxNorm'),
        ('ndc', 'NDC'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code_system = models.CharField(max_length=20, choices=CODE_SYSTEMS)
    code = models.CharField(max_length=50)
    display_name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'core_medical_code'
        unique_together = ['code_system', 'code']
        indexes = [
            models.Index(fields=['code_system', 'code']),
            models.Index(fields=['display_name']),
        ]
    
    def __str__(self):
        return f"{self.code_system.upper()}: {self.code} - {self.display_name}"


class Address(AuditableModel):
    """
    Standardized address model with validation.
    """
    street_address_1 = models.CharField(max_length=255)
    street_address_2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=50)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=50, default='United States')
    
    class Meta:
        db_table = 'core_address'
        verbose_name_plural = 'Addresses'
    
    def __str__(self):
        parts = [
            self.street_address_1,
            self.street_address_2,
            f"{self.city}, {self.state} {self.postal_code}",
            self.country if self.country != 'United States' else None
        ]
        return ', '.join(filter(None, parts))


class PhoneNumber(AuditableModel):
    """
    Phone number model with type classification.
    """
    PHONE_TYPES = [
        ('home', 'Home'),
        ('work', 'Work'),
        ('mobile', 'Mobile'),
        ('emergency', 'Emergency'),
        ('other', 'Other'),
    ]
    
    phone_number = models.CharField(max_length=20)
    phone_type = models.CharField(max_length=20, choices=PHONE_TYPES, default='home')
    is_primary = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'core_phone_number'
    
    def __str__(self):
        return f"{self.phone_number} ({self.get_phone_type_display()})"