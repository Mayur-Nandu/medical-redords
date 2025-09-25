"""
Patient models for demographics and basic information management.
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from core.models import AuditableModel, Address, PhoneNumber, DataSource
from core.encryption import encrypt_field, decrypt_field
import uuid
from datetime import date

User = get_user_model()


class Patient(AuditableModel):
    """
    Core patient model with encrypted sensitive information.
    """
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
        ('U', 'Unknown'),
    ]
    
    ETHNICITY_CHOICES = [
        ('hispanic_latino', 'Hispanic or Latino'),
        ('not_hispanic_latino', 'Not Hispanic or Latino'),
        ('unknown', 'Unknown'),
        ('declined', 'Declined to Answer'),
    ]
    
    RACE_CHOICES = [
        ('american_indian', 'American Indian or Alaska Native'),
        ('asian', 'Asian'),
        ('black', 'Black or African American'),
        ('pacific_islander', 'Native Hawaiian or Other Pacific Islander'),
        ('white', 'White'),
        ('other', 'Other'),
        ('unknown', 'Unknown'),
        ('declined', 'Declined to Answer'),
    ]
    
    MARITAL_STATUS_CHOICES = [
        ('single', 'Single'),
        ('married', 'Married'),
        ('divorced', 'Divorced'),
        ('widowed', 'Widowed'),
        ('separated', 'Separated'),
        ('domestic_partner', 'Domestic Partner'),
        ('unknown', 'Unknown'),
    ]
    
    # Basic Demographics (Encrypted)
    medical_record_number = models.CharField(max_length=50, unique=True)
    first_name_encrypted = models.TextField()  # Encrypted
    last_name_encrypted = models.TextField()   # Encrypted
    middle_name_encrypted = models.TextField(blank=True)  # Encrypted
    date_of_birth_encrypted = models.TextField()  # Encrypted
    ssn_encrypted = models.TextField(blank=True)  # Encrypted - Last 4 digits
    
    # Non-encrypted demographics
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    ethnicity = models.CharField(max_length=20, choices=ETHNICITY_CHOICES, blank=True)
    race = models.CharField(max_length=20, choices=RACE_CHOICES, blank=True)
    marital_status = models.CharField(max_length=20, choices=MARITAL_STATUS_CHOICES, blank=True)
    
    # Contact Information
    primary_address = models.ForeignKey(
        Address,
        on_delete=models.PROTECT,
        related_name='primary_patients',
        null=True,
        blank=True
    )
    phone_numbers = models.ManyToManyField(PhoneNumber, blank=True)
    email_encrypted = models.TextField(blank=True)  # Encrypted
    
    # Preferences
    preferred_language = models.CharField(max_length=50, default='English')
    religion = models.CharField(max_length=100, blank=True)
    
    # Insurance Information (Encrypted)
    primary_insurance_encrypted = models.TextField(blank=True)  # Encrypted
    secondary_insurance_encrypted = models.TextField(blank=True)  # Encrypted
    
    # Emergency Contact (Encrypted)
    emergency_contact_name_encrypted = models.TextField(blank=True)  # Encrypted
    emergency_contact_phone_encrypted = models.TextField(blank=True)  # Encrypted
    emergency_contact_relationship = models.CharField(max_length=50, blank=True)
    
    # Medical Information
    primary_physician = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='primary_patients',
        null=True,
        blank=True,
        limit_choices_to={'role': 'physician'}
    )
    
    # System fields
    user_account = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='patient_profile'
    )
    photo = models.ImageField(upload_to='patient_photos/', blank=True, null=True)
    
    class Meta:
        db_table = 'patients_patient'
        indexes = [
            models.Index(fields=['medical_record_number']),
            models.Index(fields=['created_at']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.get_full_name()} (MRN: {self.medical_record_number})"
    
    # Property methods for encrypted fields
    @property
    def first_name(self):
        return decrypt_field(self.first_name_encrypted) if self.first_name_encrypted else ''
    
    @first_name.setter
    def first_name(self, value):
        self.first_name_encrypted = encrypt_field(value) if value else ''
    
    @property
    def last_name(self):
        return decrypt_field(self.last_name_encrypted) if self.last_name_encrypted else ''
    
    @last_name.setter
    def last_name(self, value):
        self.last_name_encrypted = encrypt_field(value) if value else ''
    
    @property
    def middle_name(self):
        return decrypt_field(self.middle_name_encrypted) if self.middle_name_encrypted else ''
    
    @middle_name.setter
    def middle_name(self, value):
        self.middle_name_encrypted = encrypt_field(value) if value else ''
    
    @property
    def date_of_birth(self):
        if self.date_of_birth_encrypted:
            dob_str = decrypt_field(self.date_of_birth_encrypted)
            try:
                return date.fromisoformat(dob_str)
            except ValueError:
                return None
        return None
    
    @date_of_birth.setter
    def date_of_birth(self, value):
        if value:
            if isinstance(value, date):
                self.date_of_birth_encrypted = encrypt_field(value.isoformat())
            else:
                self.date_of_birth_encrypted = encrypt_field(str(value))
        else:
            self.date_of_birth_encrypted = ''
    
    @property
    def ssn_last_four(self):
        if self.ssn_encrypted:
            ssn = decrypt_field(self.ssn_encrypted)
            return ssn[-4:] if len(ssn) >= 4 else ssn
        return ''
    
    @property
    def ssn(self):
        return decrypt_field(self.ssn_encrypted) if self.ssn_encrypted else ''
    
    @ssn.setter
    def ssn(self, value):
        # Only store last 4 digits for HIPAA compliance
        if value:
            clean_ssn = ''.join(filter(str.isdigit, str(value)))
            self.ssn_encrypted = encrypt_field(clean_ssn[-4:]) if len(clean_ssn) >= 4 else encrypt_field(clean_ssn)
        else:
            self.ssn_encrypted = ''
    
    @property
    def email(self):
        return decrypt_field(self.email_encrypted) if self.email_encrypted else ''
    
    @email.setter
    def email(self, value):
        self.email_encrypted = encrypt_field(value) if value else ''
    
    @property
    def primary_insurance(self):
        return decrypt_field(self.primary_insurance_encrypted) if self.primary_insurance_encrypted else ''
    
    @primary_insurance.setter
    def primary_insurance(self, value):
        self.primary_insurance_encrypted = encrypt_field(value) if value else ''
    
    @property
    def secondary_insurance(self):
        return decrypt_field(self.secondary_insurance_encrypted) if self.secondary_insurance_encrypted else ''
    
    @secondary_insurance.setter
    def secondary_insurance(self, value):
        self.secondary_insurance_encrypted = encrypt_field(value) if value else ''
    
    @property
    def emergency_contact_name(self):
        return decrypt_field(self.emergency_contact_name_encrypted) if self.emergency_contact_name_encrypted else ''
    
    @emergency_contact_name.setter
    def emergency_contact_name(self, value):
        self.emergency_contact_name_encrypted = encrypt_field(value) if value else ''
    
    @property
    def emergency_contact_phone(self):
        return decrypt_field(self.emergency_contact_phone_encrypted) if self.emergency_contact_phone_encrypted else ''
    
    @emergency_contact_phone.setter
    def emergency_contact_phone(self, value):
        self.emergency_contact_phone_encrypted = encrypt_field(value) if value else ''
    
    def get_full_name(self):
        """Return patient's full name."""
        parts = [self.first_name, self.middle_name, self.last_name]
        return ' '.join(filter(None, parts))
    
    def get_age(self):
        """Calculate patient's age."""
        if self.date_of_birth:
            today = date.today()
            return today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
        return None
    
    def save(self, *args, **kwargs):
        """Override save to generate MRN if not provided."""
        if not self.medical_record_number:
            self.medical_record_number = self._generate_mrn()
        super().save(*args, **kwargs)
    
    def _generate_mrn(self):
        """Generate unique medical record number."""
        import random
        import string
        
        while True:
            # Generate MRN in format: MRN-YYYYMMDD-XXXX
            today = date.today()
            date_part = today.strftime('%Y%m%d')
            random_part = ''.join(random.choices(string.digits, k=4))
            mrn = f"MRN-{date_part}-{random_part}"
            
            if not Patient.objects.filter(medical_record_number=mrn).exists():
                return mrn


class PatientIdentifier(AuditableModel):
    """
    Alternative patient identifiers (driver's license, passport, etc.).
    """
    IDENTIFIER_TYPES = [
        ('drivers_license', "Driver's License"),
        ('passport', 'Passport'),
        ('state_id', 'State ID'),
        ('military_id', 'Military ID'),
        ('other', 'Other'),
    ]
    
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='identifiers'
    )
    identifier_type = models.CharField(max_length=20, choices=IDENTIFIER_TYPES)
    identifier_value_encrypted = models.TextField()  # Encrypted
    issuing_authority = models.CharField(max_length=100)
    issue_date = models.DateField(null=True, blank=True)
    expiration_date = models.DateField(null=True, blank=True)
    data_source = models.ForeignKey(
        DataSource,
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )
    
    class Meta:
        db_table = 'patients_patient_identifier'
        unique_together = ['patient', 'identifier_type']
    
    @property
    def identifier_value(self):
        return decrypt_field(self.identifier_value_encrypted) if self.identifier_value_encrypted else ''
    
    @identifier_value.setter
    def identifier_value(self, value):
        self.identifier_value_encrypted = encrypt_field(value) if value else ''
    
    def __str__(self):
        return f"{self.patient.get_full_name()} - {self.get_identifier_type_display()}"


class PatientNote(AuditableModel):
    """
    General notes about the patient.
    """
    NOTE_TYPES = [
        ('general', 'General Note'),
        ('alert', 'Alert/Warning'),
        ('admin', 'Administrative Note'),
        ('clinical', 'Clinical Note'),
        ('social', 'Social Note'),
    ]
    
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='notes'
    )
    note_type = models.CharField(max_length=20, choices=NOTE_TYPES, default='general')
    title = models.CharField(max_length=255)
    content_encrypted = models.TextField()  # Encrypted
    is_alert = models.BooleanField(default=False)  # High-priority alerts
    alert_expiry = models.DateTimeField(null=True, blank=True)
    data_source = models.ForeignKey(
        DataSource,
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )
    
    class Meta:
        db_table = 'patients_patient_note'
        indexes = [
            models.Index(fields=['patient', 'note_type']),
            models.Index(fields=['is_alert', 'alert_expiry']),
        ]
    
    @property
    def content(self):
        return decrypt_field(self.content_encrypted) if self.content_encrypted else ''
    
    @content.setter
    def content(self, value):
        self.content_encrypted = encrypt_field(value) if value else ''
    
    def __str__(self):
        return f"{self.patient.get_full_name()} - {self.title}"


class PatientConsent(AuditableModel):
    """
    Patient consent records for various purposes.
    """
    CONSENT_TYPES = [
        ('treatment', 'Treatment Consent'),
        ('data_sharing', 'Data Sharing Consent'),
        ('research', 'Research Participation'),
        ('photography', 'Photography Consent'),
        ('billing', 'Billing and Insurance'),
        ('hipaa', 'HIPAA Authorization'),
        ('telehealth', 'Telehealth Consent'),
    ]
    
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='consents'
    )
    consent_type = models.CharField(max_length=20, choices=CONSENT_TYPES)
    is_granted = models.BooleanField()
    consent_date = models.DateTimeField()
    expiry_date = models.DateTimeField(null=True, blank=True)
    witness = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='witnessed_consents',
        null=True,
        blank=True
    )
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'patients_patient_consent'
        unique_together = ['patient', 'consent_type']
        indexes = [
            models.Index(fields=['patient', 'consent_type']),
            models.Index(fields=['expiry_date']),
        ]
    
    def __str__(self):
        status = "Granted" if self.is_granted else "Denied"
        return f"{self.patient.get_full_name()} - {self.get_consent_type_display()} ({status})"