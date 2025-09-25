"""
Clinical Data Models - Vital signs, lab results, and clinical observations
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from apps.security.models import EncryptedField
from apps.patients.models import Patient
import uuid


class VitalSigns(models.Model):
    """
    Patient vital signs measurements
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='vital_signs')
    
    # Measurement Details
    measurement_date = models.DateTimeField(default=timezone.now)
    measurement_type = models.CharField(max_length=50, choices=[
        ('ROUTINE', 'Routine'),
        ('EMERGENCY', 'Emergency'),
        ('PRE_OPERATIVE', 'Pre-operative'),
        ('POST_OPERATIVE', 'Post-operative'),
        ('MONITORING', 'Continuous Monitoring'),
    ])
    
    # Vital Signs
    systolic_bp = models.IntegerField(
        validators=[MinValueValidator(50), MaxValueValidator(300)],
        null=True, blank=True
    )
    diastolic_bp = models.IntegerField(
        validators=[MinValueValidator(30), MaxValueValidator(200)],
        null=True, blank=True
    )
    heart_rate = models.IntegerField(
        validators=[MinValueValidator(30), MaxValueValidator(300)],
        null=True, blank=True
    )
    temperature = models.DecimalField(
        max_digits=4, decimal_places=1,
        validators=[MinValueValidator(90.0), MaxValueValidator(110.0)],
        null=True, blank=True
    )
    temperature_unit = models.CharField(max_length=2, choices=[
        ('F', 'Fahrenheit'),
        ('C', 'Celsius'),
    ], default='F')
    respiratory_rate = models.IntegerField(
        validators=[MinValueValidator(5), MaxValueValidator(60)],
        null=True, blank=True
    )
    oxygen_saturation = models.IntegerField(
        validators=[MinValueValidator(70), MaxValueValidator(100)],
        null=True, blank=True
    )
    weight = models.DecimalField(
        max_digits=6, decimal_places=2,
        validators=[MinValueValidator(0.1), MaxValueValidator(1000.0)],
        null=True, blank=True
    )
    weight_unit = models.CharField(max_length=2, choices=[
        ('LB', 'Pounds'),
        ('KG', 'Kilograms'),
    ], default='LB')
    height = models.DecimalField(
        max_digits=5, decimal_places=2,
        validators=[MinValueValidator(10.0), MaxValueValidator(300.0)],
        null=True, blank=True
    )
    height_unit = models.CharField(max_length=2, choices=[
        ('IN', 'Inches'),
        ('CM', 'Centimeters'),
    ], default='IN')
    
    # Calculated Values
    bmi = models.DecimalField(
        max_digits=5, decimal_places=2,
        validators=[MinValueValidator(10.0), MaxValueValidator(100.0)],
        null=True, blank=True
    )
    
    # Additional Measurements
    pain_score = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        null=True, blank=True
    )
    glucose_level = models.IntegerField(
        validators=[MinValueValidator(20), MaxValueValidator(1000)],
        null=True, blank=True
    )
    
    # Context
    position = models.CharField(max_length=20, choices=[
        ('SITTING', 'Sitting'),
        ('STANDING', 'Standing'),
        ('LYING', 'Lying'),
        ('WALKING', 'Walking'),
    ], default='SITTING')
    notes = EncryptedField(blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='created_vital_signs')
    updated_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='updated_vital_signs')
    
    class Meta:
        db_table = 'vital_signs'
        ordering = ['-measurement_date']
        indexes = [
            models.Index(fields=['patient', 'measurement_date']),
            models.Index(fields=['measurement_type', 'measurement_date']),
        ]
    
    def __str__(self):
        return f"{self.patient.patient_id} - {self.measurement_date.strftime('%Y-%m-%d %H:%M')}"
    
    def save(self, *args, **kwargs):
        """Calculate BMI on save"""
        if self.weight and self.height:
            # Convert to metric if needed
            weight_kg = self.weight
            height_m = self.height
            
            if self.weight_unit == 'LB':
                weight_kg = self.weight * 0.453592
            if self.height_unit == 'IN':
                height_m = self.height * 0.0254
            
            if height_m > 0:
                self.bmi = weight_kg / (height_m ** 2)
        
        super().save(*args, **kwargs)


class LabResult(models.Model):
    """
    Laboratory test results
    """
    RESULT_STATUS = [
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
        ('ERROR', 'Error'),
    ]
    
    CRITICAL_LEVELS = [
        ('NORMAL', 'Normal'),
        ('HIGH', 'High'),
        ('LOW', 'Low'),
        ('CRITICAL_HIGH', 'Critical High'),
        ('CRITICAL_LOW', 'Critical Low'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='lab_results')
    
    # Test Information
    test_name = EncryptedField(max_length=200)
    test_code = models.CharField(max_length=20, blank=True)  # LOINC code
    test_category = models.CharField(max_length=50, choices=[
        ('HEMATOLOGY', 'Hematology'),
        ('CHEMISTRY', 'Chemistry'),
        ('MICROBIOLOGY', 'Microbiology'),
        ('IMMUNOLOGY', 'Immunology'),
        ('ENDOCRINOLOGY', 'Endocrinology'),
        ('TOXICOLOGY', 'Toxicology'),
        ('OTHER', 'Other'),
    ])
    
    # Results
    result_value = EncryptedField(max_length=200)
    result_unit = models.CharField(max_length=20, blank=True)
    reference_range = models.CharField(max_length=100, blank=True)
    critical_level = models.CharField(max_length=20, choices=CRITICAL_LEVELS, default='NORMAL')
    status = models.CharField(max_length=20, choices=RESULT_STATUS, default='PENDING')
    
    # Timing
    ordered_date = models.DateTimeField()
    collected_date = models.DateTimeField(null=True, blank=True)
    result_date = models.DateTimeField(null=True, blank=True)
    
    # Laboratory Information
    lab_name = EncryptedField(max_length=200, blank=True)
    lab_id = models.CharField(max_length=50, blank=True)
    ordering_physician = EncryptedField(max_length=200, blank=True)
    
    # Clinical Context
    clinical_notes = EncryptedField(blank=True)
    interpretation = EncryptedField(blank=True)
    follow_up_required = models.BooleanField(default=False)
    
    # Quality Control
    quality_control_passed = models.BooleanField(default=True)
    repeat_test_required = models.BooleanField(default=False)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='created_lab_results')
    updated_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='updated_lab_results')
    
    class Meta:
        db_table = 'lab_results'
        ordering = ['-result_date', '-ordered_date']
        indexes = [
            models.Index(fields=['patient', 'result_date']),
            models.Index(fields=['test_category', 'result_date']),
            models.Index(fields=['critical_level', 'result_date']),
        ]
    
    def __str__(self):
        return f"{self.patient.patient_id} - {self.test_name} - {self.result_date}"


class DiagnosticImaging(models.Model):
    """
    Diagnostic imaging results
    """
    IMAGING_TYPES = [
        ('XRAY', 'X-Ray'),
        ('CT', 'Computed Tomography'),
        ('MRI', 'Magnetic Resonance Imaging'),
        ('ULTRASOUND', 'Ultrasound'),
        ('MAMMOGRAPHY', 'Mammography'),
        ('NUCLEAR', 'Nuclear Medicine'),
        ('PET', 'Positron Emission Tomography'),
        ('OTHER', 'Other'),
    ]
    
    BODY_PARTS = [
        ('HEAD', 'Head'),
        ('NECK', 'Neck'),
        ('CHEST', 'Chest'),
        ('ABDOMEN', 'Abdomen'),
        ('PELVIS', 'Pelvis'),
        ('SPINE', 'Spine'),
        ('EXTREMITIES', 'Extremities'),
        ('OTHER', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='diagnostic_imaging')
    
    # Imaging Details
    imaging_type = models.CharField(max_length=20, choices=IMAGING_TYPES)
    body_part = models.CharField(max_length=20, choices=BODY_PARTS)
    study_description = EncryptedField(max_length=300)
    study_code = models.CharField(max_length=20, blank=True)  # CPT code
    
    # Timing
    ordered_date = models.DateTimeField()
    performed_date = models.DateTimeField(null=True, blank=True)
    report_date = models.DateTimeField(null=True, blank=True)
    
    # Results
    findings = EncryptedField(blank=True)
    impression = EncryptedField(blank=True)
    recommendations = EncryptedField(blank=True)
    
    # Clinical Information
    clinical_indication = EncryptedField(blank=True)
    contrast_used = models.BooleanField(default=False)
    contrast_type = models.CharField(max_length=100, blank=True)
    
    # Radiologist Information
    radiologist = EncryptedField(max_length=200, blank=True)
    radiologist_id = models.CharField(max_length=50, blank=True)
    
    # Technical Details
    technique = EncryptedField(blank=True)
    radiation_dose = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    radiation_unit = models.CharField(max_length=10, blank=True)
    
    # Quality and Follow-up
    image_quality = models.CharField(max_length=20, choices=[
        ('EXCELLENT', 'Excellent'),
        ('GOOD', 'Good'),
        ('FAIR', 'Fair'),
        ('POOR', 'Poor'),
    ], default='GOOD')
    follow_up_required = models.BooleanField(default=False)
    follow_up_interval = models.CharField(max_length=50, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='created_diagnostic_imaging')
    updated_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='updated_diagnostic_imaging')
    
    class Meta:
        db_table = 'diagnostic_imaging'
        ordering = ['-performed_date', '-ordered_date']
        indexes = [
            models.Index(fields=['patient', 'performed_date']),
            models.Index(fields=['imaging_type', 'performed_date']),
            models.Index(fields=['body_part', 'performed_date']),
        ]
    
    def __str__(self):
        return f"{self.patient.patient_id} - {self.imaging_type} - {self.body_part} - {self.performed_date}"


class ClinicalNote(models.Model):
    """
    Clinical notes and observations
    """
    NOTE_TYPES = [
        ('PROGRESS', 'Progress Note'),
        ('CONSULTATION', 'Consultation'),
        ('DISCHARGE', 'Discharge Summary'),
        ('ADMISSION', 'Admission Note'),
        ('PROCEDURE', 'Procedure Note'),
        ('EMERGENCY', 'Emergency Note'),
        ('TELEPHONE', 'Telephone Note'),
        ('OTHER', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='clinical_notes')
    
    # Note Information
    note_type = models.CharField(max_length=20, choices=NOTE_TYPES)
    title = EncryptedField(max_length=200)
    content = EncryptedField()
    
    # Clinical Context
    chief_complaint = EncryptedField(blank=True)
    assessment = EncryptedField(blank=True)
    plan = EncryptedField(blank=True)
    differential_diagnosis = EncryptedField(blank=True)
    
    # Timing
    note_date = models.DateTimeField(default=timezone.now)
    encounter_date = models.DateTimeField(null=True, blank=True)
    
    # Author Information
    author = EncryptedField(max_length=200)
    author_title = models.CharField(max_length=100, blank=True)
    author_signature = EncryptedField(blank=True)
    
    # Review and Approval
    reviewed_by = EncryptedField(max_length=200, blank=True)
    reviewed_date = models.DateTimeField(null=True, blank=True)
    approved_by = EncryptedField(max_length=200, blank=True)
    approved_date = models.DateTimeField(null=True, blank=True)
    
    # Status
    is_draft = models.BooleanField(default=False)
    is_final = models.BooleanField(default=False)
    requires_signature = models.BooleanField(default=False)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='created_clinical_notes')
    updated_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='updated_clinical_notes')
    
    class Meta:
        db_table = 'clinical_notes'
        ordering = ['-note_date']
        indexes = [
            models.Index(fields=['patient', 'note_date']),
            models.Index(fields=['note_type', 'note_date']),
            models.Index(fields=['is_final', 'note_date']),
        ]
    
    def __str__(self):
        return f"{self.patient.patient_id} - {self.note_type} - {self.note_date.strftime('%Y-%m-%d')}"


class PreventiveCare(models.Model):
    """
    Preventive care tracking
    """
    CARE_TYPES = [
        ('SCREENING', 'Screening'),
        ('VACCINATION', 'Vaccination'),
        ('COUNSELING', 'Counseling'),
        ('RISK_ASSESSMENT', 'Risk Assessment'),
        ('FOLLOW_UP', 'Follow-up'),
    ]
    
    STATUS_CHOICES = [
        ('DUE', 'Due'),
        ('OVERDUE', 'Overdue'),
        ('COMPLETED', 'Completed'),
        ('DECLINED', 'Declined'),
        ('NOT_APPLICABLE', 'Not Applicable'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='preventive_care')
    
    # Care Information
    care_type = models.CharField(max_length=20, choices=CARE_TYPES)
    care_name = EncryptedField(max_length=200)
    care_description = EncryptedField(blank=True)
    
    # Scheduling
    due_date = models.DateField()
    completed_date = models.DateField(null=True, blank=True)
    next_due_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DUE')
    
    # Clinical Details
    indication = EncryptedField(blank=True)
    contraindications = EncryptedField(blank=True)
    results = EncryptedField(blank=True)
    recommendations = EncryptedField(blank=True)
    
    # Provider Information
    provider = EncryptedField(max_length=200, blank=True)
    provider_specialty = models.CharField(max_length=100, blank=True)
    
    # Quality Measures
    quality_measure_code = models.CharField(max_length=20, blank=True)
    performance_period = models.CharField(max_length=20, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='created_preventive_care')
    updated_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='updated_preventive_care')
    
    class Meta:
        db_table = 'preventive_care'
        ordering = ['due_date']
        indexes = [
            models.Index(fields=['patient', 'due_date']),
            models.Index(fields=['care_type', 'due_date']),
            models.Index(fields=['status', 'due_date']),
        ]
    
    def __str__(self):
        return f"{self.patient.patient_id} - {self.care_name} - {self.due_date}"