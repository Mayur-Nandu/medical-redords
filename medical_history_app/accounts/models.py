"""
User models for role-based access control in medical history application.
"""
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from core.models import TimestampedModel, Address, PhoneNumber
import uuid


class User(AbstractUser):
    """
    Extended user model with healthcare-specific roles and permissions.
    """
    USER_ROLES = [
        ('physician', 'Physician'),
        ('nurse', 'Nurse'),
        ('medical_assistant', 'Medical Assistant'),
        ('admin', 'Administrator'),
        ('patient', 'Patient'),
        ('lab_technician', 'Lab Technician'),
        ('radiologist', 'Radiologist'),
        ('pharmacist', 'Pharmacist'),
        ('it_admin', 'IT Administrator'),
    ]
    
    SPECIALTY_CHOICES = [
        ('family_medicine', 'Family Medicine'),
        ('internal_medicine', 'Internal Medicine'),
        ('pediatrics', 'Pediatrics'),
        ('cardiology', 'Cardiology'),
        ('dermatology', 'Dermatology'),
        ('emergency_medicine', 'Emergency Medicine'),
        ('orthopedics', 'Orthopedics'),
        ('psychiatry', 'Psychiatry'),
        ('radiology', 'Radiology'),
        ('surgery', 'Surgery'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.CharField(max_length=20, choices=USER_ROLES, default='patient')
    specialty = models.CharField(max_length=30, choices=SPECIALTY_CHOICES, blank=True, null=True)
    license_number = models.CharField(max_length=50, blank=True, null=True)
    npi_number = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        validators=[RegexValidator(r'^\d{10}$', 'NPI must be 10 digits')]
    )
    organization = models.ForeignKey(
        'Organization',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='users'
    )
    is_verified = models.BooleanField(default=False)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    failed_login_attempts = models.PositiveIntegerField(default=0)
    account_locked_until = models.DateTimeField(null=True, blank=True)
    password_changed_at = models.DateTimeField(auto_now_add=True)
    terms_accepted_at = models.DateTimeField(null=True, blank=True)
    privacy_policy_accepted_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'accounts_user'
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"
    
    @property
    def is_healthcare_provider(self):
        """Check if user is a healthcare provider."""
        provider_roles = ['physician', 'nurse', 'medical_assistant', 'lab_technician', 
                         'radiologist', 'pharmacist']
        return self.role in provider_roles
    
    @property
    def can_access_patient_data(self):
        """Check if user can access patient data."""
        return self.is_healthcare_provider or self.role == 'admin'
    
    @property
    def can_modify_medical_records(self):
        """Check if user can modify medical records."""
        authorized_roles = ['physician', 'nurse', 'medical_assistant']
        return self.role in authorized_roles
    
    def get_permissions_for_patient(self, patient):
        """Get specific permissions for a patient."""
        # Patients can only access their own data
        if self.role == 'patient':
            return {
                'can_view': hasattr(self, 'patient_profile') and self.patient_profile == patient,
                'can_edit': hasattr(self, 'patient_profile') and self.patient_profile == patient,
                'can_delete': False,
            }
        
        # Healthcare providers have broader access
        if self.is_healthcare_provider:
            return {
                'can_view': True,
                'can_edit': self.can_modify_medical_records,
                'can_delete': False,
            }
        
        # Admins have full access
        if self.role == 'admin':
            return {
                'can_view': True,
                'can_edit': True,
                'can_delete': True,
            }
        
        # Default: no access
        return {
            'can_view': False,
            'can_edit': False,
            'can_delete': False,
        }


class Organization(TimestampedModel):
    """
    Healthcare organizations (hospitals, clinics, practices).
    """
    ORGANIZATION_TYPES = [
        ('hospital', 'Hospital'),
        ('clinic', 'Clinic'),
        ('private_practice', 'Private Practice'),
        ('urgent_care', 'Urgent Care'),
        ('laboratory', 'Laboratory'),
        ('pharmacy', 'Pharmacy'),
        ('imaging_center', 'Imaging Center'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    organization_type = models.CharField(max_length=20, choices=ORGANIZATION_TYPES)
    tax_id = models.CharField(max_length=20, unique=True)
    npi_number = models.CharField(
        max_length=10,
        unique=True,
        validators=[RegexValidator(r'^\d{10}$', 'NPI must be 10 digits')]
    )
    address = models.ForeignKey(Address, on_delete=models.PROTECT)
    phone_numbers = models.ManyToManyField(PhoneNumber, blank=True)
    email = models.EmailField()
    website = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'accounts_organization'
    
    def __str__(self):
        return f"{self.name} ({self.get_organization_type_display()})"


class UserProfile(TimestampedModel):
    """
    Extended user profile information.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    middle_name = models.CharField(max_length=30, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.ForeignKey(Address, on_delete=models.PROTECT, null=True, blank=True)
    phone_numbers = models.ManyToManyField(PhoneNumber, blank=True)
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True)
    emergency_contact_relationship = models.CharField(max_length=50, blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    timezone = models.CharField(max_length=50, default='UTC')
    language_preference = models.CharField(max_length=10, default='en')
    
    class Meta:
        db_table = 'accounts_user_profile'
    
    def __str__(self):
        return f"Profile for {self.user.get_full_name()}"


class UserSession(TimestampedModel):
    """
    Track user sessions for security and audit purposes.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    session_key = models.CharField(max_length=40, unique=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    is_active = models.BooleanField(default=True)
    login_at = models.DateTimeField(auto_now_add=True)
    logout_at = models.DateTimeField(null=True, blank=True)
    last_activity = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'accounts_user_session'
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['session_key']),
        ]
    
    def __str__(self):
        return f"Session for {self.user.username} from {self.ip_address}"


class PasswordHistory(TimestampedModel):
    """
    Track password history to prevent reuse.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_history')
    password_hash = models.CharField(max_length=128)
    
    class Meta:
        db_table = 'accounts_password_history'
        indexes = [
            models.Index(fields=['user', 'created_at']),
        ]
    
    def __str__(self):
        return f"Password history for {self.user.username}"


class AccessLog(TimestampedModel):
    """
    Log all access attempts for security auditing.
    """
    ACCESS_TYPES = [
        ('login_success', 'Successful Login'),
        ('login_failed', 'Failed Login'),
        ('logout', 'Logout'),
        ('password_change', 'Password Change'),
        ('account_locked', 'Account Locked'),
        ('account_unlocked', 'Account Unlocked'),
        ('permission_denied', 'Permission Denied'),
        ('data_access', 'Data Access'),
        ('data_modification', 'Data Modification'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='access_logs', null=True)
    access_type = models.CharField(max_length=20, choices=ACCESS_TYPES)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    details = models.JSONField(default=dict)
    
    class Meta:
        db_table = 'accounts_access_log'
        indexes = [
            models.Index(fields=['user', 'access_type']),
            models.Index(fields=['created_at']),
            models.Index(fields=['ip_address']),
        ]
    
    def __str__(self):
        user_str = self.user.username if self.user else "Anonymous"
        return f"{self.get_access_type_display()} - {user_str} at {self.created_at}"