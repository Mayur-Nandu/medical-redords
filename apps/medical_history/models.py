"""
Medical History Models - Comprehensive patient medical history management
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from apps.security.models import EncryptedField
from apps.patients.models import Patient
import uuid


class MedicalHistory(models.Model):
    """
    Core medical history record for a patient
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='medical_histories')
    
    # Visit Information
    visit_date = models.DateTimeField(default=timezone.now)
    visit_type = models.CharField(max_length=50, choices=[
        ('INITIAL', 'Initial Visit'),
        ('FOLLOW_UP', 'Follow-up Visit'),
        ('EMERGENCY', 'Emergency Visit'),
        ('CONSULTATION', 'Consultation'),
        ('ANNUAL', 'Annual Checkup'),
    ])
    chief_complaint = EncryptedField(max_length=500)
    
    # History of Present Illness
    hpi_duration = models.CharField(max_length=100, blank=True)  # e.g., "3 days", "2 weeks"
    hpi_location = EncryptedField(max_length=200, blank=True)
    hpi_quality = EncryptedField(max_length=200, blank=True)
    hpi_severity = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        null=True, blank=True
    )
    hpi_timing = EncryptedField(max_length=200, blank=True)
    hpi_context = EncryptedField(max_length=500, blank=True)
    hpi_modifying_factors = EncryptedField(max_length=500, blank=True)
    hpi_associated_symptoms = EncryptedField(max_length=500, blank=True)
    
    # Past Medical History
    past_medical_history = EncryptedField(blank=True)
    past_surgeries = EncryptedField(blank=True)
    past_hospitalizations = EncryptedField(blank=True)
    past_trauma = EncryptedField(blank=True)
    
    # Family History
    family_history = EncryptedField(blank=True)
    family_cancer_history = models.BooleanField(default=False)
    family_heart_disease = models.BooleanField(default=False)
    family_diabetes = models.BooleanField(default=False)
    family_hypertension = models.BooleanField(default=False)
    family_mental_health = models.BooleanField(default=False)
    family_other = EncryptedField(blank=True)
    
    # Social History
    smoking_status = models.CharField(max_length=20, choices=[
        ('NEVER', 'Never Smoked'),
        ('FORMER', 'Former Smoker'),
        ('CURRENT', 'Current Smoker'),
        ('UNKNOWN', 'Unknown'),
    ], default='UNKNOWN')
    smoking_pack_years = models.FloatField(null=True, blank=True)
    alcohol_use = models.CharField(max_length=20, choices=[
        ('NONE', 'None'),
        ('OCCASIONAL', 'Occasional'),
        ('REGULAR', 'Regular'),
        ('HEAVY', 'Heavy'),
        ('UNKNOWN', 'Unknown'),
    ], default='UNKNOWN')
    drug_use = models.CharField(max_length=20, choices=[
        ('NONE', 'None'),
        ('RECREATIONAL', 'Recreational'),
        ('PRESCRIPTION', 'Prescription'),
        ('ILLICIT', 'Illicit'),
        ('UNKNOWN', 'Unknown'),
    ], default='UNKNOWN')
    occupation = EncryptedField(max_length=200, blank=True)
    education_level = models.CharField(max_length=50, blank=True)
    marital_status = models.CharField(max_length=20, blank=True)
    living_situation = EncryptedField(max_length=200, blank=True)
    travel_history = EncryptedField(blank=True)
    
    # Review of Systems
    constitutional_symptoms = EncryptedField(blank=True)
    eyes_ears_nose_throat = EncryptedField(blank=True)
    cardiovascular = EncryptedField(blank=True)
    respiratory = EncryptedField(blank=True)
    gastrointestinal = EncryptedField(blank=True)
    genitourinary = EncryptedField(blank=True)
    musculoskeletal = EncryptedField(blank=True)
    neurological = EncryptedField(blank=True)
    psychiatric = EncryptedField(blank=True)
    endocrine = EncryptedField(blank=True)
    hematologic = EncryptedField(blank=True)
    skin = EncryptedField(blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='created_medical_histories')
    updated_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='updated_medical_histories')
    is_active = models.BooleanField(default=True)
    
    # Data Quality
    completeness_score = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=0
    )
    reliability_score = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=0
    )
    data_source = models.CharField(max_length=50, choices=[
        ('PATIENT_INTERVIEW', 'Patient Interview'),
        ('FAMILY_REPORT', 'Family Report'),
        ('PREVIOUS_RECORDS', 'Previous Records'),
        ('EMERGENCY_CONTACT', 'Emergency Contact'),
        ('OTHER', 'Other'),
    ], default='PATIENT_INTERVIEW')
    
    class Meta:
        db_table = 'medical_histories'
        ordering = ['-visit_date']
        indexes = [
            models.Index(fields=['patient', 'visit_date']),
            models.Index(fields=['created_at']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.patient.patient_id} - {self.visit_date.strftime('%Y-%m-%d')} - {self.chief_complaint[:50]}"


class Medication(models.Model):
    """
    Patient medications
    """
    MEDICATION_TYPES = [
        ('PRESCRIPTION', 'Prescription'),
        ('OTC', 'Over-the-Counter'),
        ('SUPPLEMENT', 'Supplement'),
        ('HERBAL', 'Herbal'),
        ('OTHER', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='medications')
    medical_history = models.ForeignKey(MedicalHistory, on_delete=models.CASCADE, related_name='medications', null=True, blank=True)
    
    # Medication Details
    name = EncryptedField(max_length=200)
    generic_name = EncryptedField(max_length=200, blank=True)
    medication_type = models.CharField(max_length=20, choices=MEDICATION_TYPES)
    dosage = EncryptedField(max_length=100, blank=True)
    frequency = EncryptedField(max_length=100, blank=True)
    route = models.CharField(max_length=50, blank=True)  # oral, topical, injection, etc.
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    is_current = models.BooleanField(default=True)
    
    # Prescriber Information
    prescribed_by = EncryptedField(max_length=200, blank=True)
    pharmacy = EncryptedField(max_length=200, blank=True)
    
    # Medication Details
    indication = EncryptedField(max_length=300, blank=True)
    side_effects = EncryptedField(blank=True)
    effectiveness = models.CharField(max_length=20, choices=[
        ('EXCELLENT', 'Excellent'),
        ('GOOD', 'Good'),
        ('FAIR', 'Fair'),
        ('POOR', 'Poor'),
        ('UNKNOWN', 'Unknown'),
    ], default='UNKNOWN')
    
    # Compliance
    compliance_rate = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        null=True, blank=True
    )
    compliance_notes = EncryptedField(blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='created_medications')
    updated_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='updated_medications')
    
    class Meta:
        db_table = 'medications'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.patient.patient_id} - {self.name}"


class Allergy(models.Model):
    """
    Patient allergies and adverse reactions
    """
    ALLERGY_TYPES = [
        ('DRUG', 'Drug Allergy'),
        ('FOOD', 'Food Allergy'),
        ('ENVIRONMENTAL', 'Environmental Allergy'),
        ('CONTACT', 'Contact Allergy'),
        ('OTHER', 'Other'),
    ]
    
    SEVERITY_LEVELS = [
        ('MILD', 'Mild'),
        ('MODERATE', 'Moderate'),
        ('SEVERE', 'Severe'),
        ('LIFE_THREATENING', 'Life-threatening'),
        ('UNKNOWN', 'Unknown'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='allergies')
    medical_history = models.ForeignKey(MedicalHistory, on_delete=models.CASCADE, related_name='allergies', null=True, blank=True)
    
    # Allergy Details
    allergen = EncryptedField(max_length=200)
    allergy_type = models.CharField(max_length=20, choices=ALLERGY_TYPES)
    severity = models.CharField(max_length=20, choices=SEVERITY_LEVELS, default='UNKNOWN')
    reaction_description = EncryptedField(blank=True)
    onset_date = models.DateField(null=True, blank=True)
    last_reaction_date = models.DateField(null=True, blank=True)
    
    # Clinical Details
    symptoms = EncryptedField(blank=True)
    treatment_required = models.BooleanField(default=False)
    treatment_description = EncryptedField(blank=True)
    confirmed_by_testing = models.BooleanField(default=False)
    testing_method = EncryptedField(max_length=200, blank=True)
    
    # Cross-reactivity
    cross_reactive_allergens = EncryptedField(blank=True)
    avoidance_instructions = EncryptedField(blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='created_allergies')
    updated_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='updated_allergies')
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'allergies'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.patient.patient_id} - {self.allergen} ({self.severity})"


class Immunization(models.Model):
    """
    Patient immunization records
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='immunizations')
    medical_history = models.ForeignKey(MedicalHistory, on_delete=models.CASCADE, related_name='immunizations', null=True, blank=True)
    
    # Immunization Details
    vaccine_name = EncryptedField(max_length=200)
    vaccine_code = models.CharField(max_length=20, blank=True)  # CVX code
    manufacturer = EncryptedField(max_length=200, blank=True)
    lot_number = EncryptedField(max_length=100, blank=True)
    administration_date = models.DateField()
    expiration_date = models.DateField(null=True, blank=True)
    
    # Administration Details
    administered_by = EncryptedField(max_length=200, blank=True)
    administration_site = EncryptedField(max_length=100, blank=True)
    route = models.CharField(max_length=50, blank=True)
    dosage = EncryptedField(max_length=100, blank=True)
    
    # Series Information
    series_number = models.IntegerField(null=True, blank=True)
    total_series_doses = models.IntegerField(null=True, blank=True)
    is_complete = models.BooleanField(default=False)
    
    # Reactions
    adverse_reactions = EncryptedField(blank=True)
    contraindications = EncryptedField(blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='created_immunizations')
    updated_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='updated_immunizations')
    
    class Meta:
        db_table = 'immunizations'
        ordering = ['-administration_date']
    
    def __str__(self):
        return f"{self.patient.patient_id} - {self.vaccine_name} - {self.administration_date}"


class SocialHistory(models.Model):
    """
    Detailed social history information
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='social_histories')
    medical_history = models.ForeignKey(MedicalHistory, on_delete=models.CASCADE, related_name='social_histories', null=True, blank=True)
    
    # Smoking History
    smoking_status = models.CharField(max_length=20, choices=[
        ('NEVER', 'Never Smoked'),
        ('FORMER', 'Former Smoker'),
        ('CURRENT', 'Current Smoker'),
        ('UNKNOWN', 'Unknown'),
    ], default='UNKNOWN')
    smoking_start_age = models.IntegerField(null=True, blank=True)
    smoking_stop_age = models.IntegerField(null=True, blank=True)
    cigarettes_per_day = models.IntegerField(null=True, blank=True)
    pack_years = models.FloatField(null=True, blank=True)
    secondhand_smoke_exposure = models.BooleanField(default=False)
    
    # Alcohol History
    alcohol_use = models.CharField(max_length=20, choices=[
        ('NONE', 'None'),
        ('OCCASIONAL', 'Occasional'),
        ('REGULAR', 'Regular'),
        ('HEAVY', 'Heavy'),
        ('UNKNOWN', 'Unknown'),
    ], default='UNKNOWN')
    drinks_per_week = models.IntegerField(null=True, blank=True)
    alcohol_type = EncryptedField(max_length=200, blank=True)
    alcohol_related_problems = models.BooleanField(default=False)
    
    # Drug Use History
    drug_use = models.CharField(max_length=20, choices=[
        ('NONE', 'None'),
        ('RECREATIONAL', 'Recreational'),
        ('PRESCRIPTION', 'Prescription'),
        ('ILLICIT', 'Illicit'),
        ('UNKNOWN', 'Unknown'),
    ], default='UNKNOWN')
    drug_types = EncryptedField(blank=True)
    injection_drug_use = models.BooleanField(default=False)
    drug_treatment_history = EncryptedField(blank=True)
    
    # Sexual History
    sexual_activity = models.CharField(max_length=20, choices=[
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive'),
        ('UNKNOWN', 'Unknown'),
    ], default='UNKNOWN')
    sexual_orientation = models.CharField(max_length=50, blank=True)
    number_of_partners = models.IntegerField(null=True, blank=True)
    safe_sex_practices = models.BooleanField(default=False)
    std_history = EncryptedField(blank=True)
    
    # Occupational History
    current_occupation = EncryptedField(max_length=200, blank=True)
    occupational_hazards = EncryptedField(blank=True)
    work_stress_level = models.CharField(max_length=20, choices=[
        ('LOW', 'Low'),
        ('MODERATE', 'Moderate'),
        ('HIGH', 'High'),
        ('UNKNOWN', 'Unknown'),
    ], default='UNKNOWN')
    
    # Living Situation
    living_arrangement = EncryptedField(max_length=200, blank=True)
    housing_type = models.CharField(max_length=50, blank=True)
    financial_stress = models.BooleanField(default=False)
    social_support = models.CharField(max_length=20, choices=[
        ('EXCELLENT', 'Excellent'),
        ('GOOD', 'Good'),
        ('FAIR', 'Fair'),
        ('POOR', 'Poor'),
        ('UNKNOWN', 'Unknown'),
    ], default='UNKNOWN')
    
    # Travel History
    recent_travel = models.BooleanField(default=False)
    travel_destinations = EncryptedField(blank=True)
    travel_dates = EncryptedField(blank=True)
    travel_vaccinations = EncryptedField(blank=True)
    
    # Exercise and Diet
    exercise_frequency = models.CharField(max_length=20, choices=[
        ('DAILY', 'Daily'),
        ('WEEKLY', 'Weekly'),
        ('MONTHLY', 'Monthly'),
        ('RARELY', 'Rarely'),
        ('NEVER', 'Never'),
        ('UNKNOWN', 'Unknown'),
    ], default='UNKNOWN')
    diet_type = EncryptedField(max_length=200, blank=True)
    dietary_restrictions = EncryptedField(blank=True)
    
    # Mental Health
    stress_level = models.CharField(max_length=20, choices=[
        ('LOW', 'Low'),
        ('MODERATE', 'Moderate'),
        ('HIGH', 'High'),
        ('UNKNOWN', 'Unknown'),
    ], default='UNKNOWN')
    mental_health_history = EncryptedField(blank=True)
    counseling_history = EncryptedField(blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='created_social_histories')
    updated_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='updated_social_histories')
    
    class Meta:
        db_table = 'social_histories'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.patient.patient_id} - Social History - {self.created_at.strftime('%Y-%m-%d')}"