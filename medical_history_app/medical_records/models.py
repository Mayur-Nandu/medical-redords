"""
Medical records models for comprehensive medical history management.
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from core.models import AuditableModel, DataSource, MedicalCode
from core.encryption import encrypt_field, decrypt_field
from patients.models import Patient
import uuid

User = get_user_model()


class MedicalHistory(AuditableModel):
    """
    Comprehensive medical history for a patient.
    """
    patient = models.OneToOneField(
        Patient,
        on_delete=models.CASCADE,
        related_name='medical_history'
    )
    chief_complaint_encrypted = models.TextField(blank=True)  # Encrypted
    history_of_present_illness_encrypted = models.TextField(blank=True)  # Encrypted
    last_updated_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='updated_medical_histories',
        null=True,
        blank=True
    )
    
    class Meta:
        db_table = 'medical_records_medical_history'
        verbose_name_plural = 'Medical Histories'
    
    @property
    def chief_complaint(self):
        return decrypt_field(self.chief_complaint_encrypted) if self.chief_complaint_encrypted else ''
    
    @chief_complaint.setter
    def chief_complaint(self, value):
        self.chief_complaint_encrypted = encrypt_field(value) if value else ''
    
    @property
    def history_of_present_illness(self):
        return decrypt_field(self.history_of_present_illness_encrypted) if self.history_of_present_illness_encrypted else ''
    
    @history_of_present_illness.setter
    def history_of_present_illness(self, value):
        self.history_of_present_illness_encrypted = encrypt_field(value) if value else ''
    
    def __str__(self):
        return f"Medical History - {self.patient.get_full_name()}"


class PastMedicalHistory(AuditableModel):
    """
    Past medical conditions, surgeries, and hospitalizations.
    """
    CONDITION_TYPES = [
        ('condition', 'Medical Condition'),
        ('surgery', 'Surgery'),
        ('hospitalization', 'Hospitalization'),
        ('injury', 'Injury'),
        ('mental_health', 'Mental Health'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('resolved', 'Resolved'),
        ('chronic', 'Chronic'),
        ('in_remission', 'In Remission'),
        ('unknown', 'Unknown'),
    ]
    
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='past_medical_history'
    )
    condition_type = models.CharField(max_length=20, choices=CONDITION_TYPES)
    condition_name_encrypted = models.TextField()  # Encrypted
    description_encrypted = models.TextField(blank=True)  # Encrypted
    icd10_code = models.ForeignKey(
        MedicalCode,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        limit_choices_to={'code_system': 'icd10'}
    )
    onset_date = models.DateField(null=True, blank=True)
    resolution_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    treating_physician_encrypted = models.TextField(blank=True)  # Encrypted
    data_source = models.ForeignKey(
        DataSource,
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )
    
    class Meta:
        db_table = 'medical_records_past_medical_history'
        indexes = [
            models.Index(fields=['patient', 'condition_type']),
            models.Index(fields=['onset_date']),
            models.Index(fields=['status']),
        ]
    
    @property
    def condition_name(self):
        return decrypt_field(self.condition_name_encrypted) if self.condition_name_encrypted else ''
    
    @condition_name.setter
    def condition_name(self, value):
        self.condition_name_encrypted = encrypt_field(value) if value else ''
    
    @property
    def description(self):
        return decrypt_field(self.description_encrypted) if self.description_encrypted else ''
    
    @description.setter
    def description(self, value):
        self.description_encrypted = encrypt_field(value) if value else ''
    
    @property
    def treating_physician(self):
        return decrypt_field(self.treating_physician_encrypted) if self.treating_physician_encrypted else ''
    
    @treating_physician.setter
    def treating_physician(self, value):
        self.treating_physician_encrypted = encrypt_field(value) if value else ''
    
    def __str__(self):
        return f"{self.patient.get_full_name()} - {self.condition_name}"


class FamilyHistory(AuditableModel):
    """
    Family medical history including hereditary conditions.
    """
    RELATIONSHIP_CHOICES = [
        ('mother', 'Mother'),
        ('father', 'Father'),
        ('sister', 'Sister'),
        ('brother', 'Brother'),
        ('maternal_grandmother', 'Maternal Grandmother'),
        ('maternal_grandfather', 'Maternal Grandfather'),
        ('paternal_grandmother', 'Paternal Grandmother'),
        ('paternal_grandfather', 'Paternal Grandfather'),
        ('aunt', 'Aunt'),
        ('uncle', 'Uncle'),
        ('cousin', 'Cousin'),
        ('child', 'Child'),
        ('other', 'Other'),
    ]
    
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='family_history'
    )
    relationship = models.CharField(max_length=30, choices=RELATIONSHIP_CHOICES)
    relative_name_encrypted = models.TextField(blank=True)  # Encrypted
    condition_name_encrypted = models.TextField()  # Encrypted
    age_at_diagnosis = models.PositiveIntegerField(null=True, blank=True)
    age_at_death = models.PositiveIntegerField(null=True, blank=True)
    cause_of_death_encrypted = models.TextField(blank=True)  # Encrypted
    notes_encrypted = models.TextField(blank=True)  # Encrypted
    icd10_code = models.ForeignKey(
        MedicalCode,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        limit_choices_to={'code_system': 'icd10'}
    )
    data_source = models.ForeignKey(
        DataSource,
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )
    
    class Meta:
        db_table = 'medical_records_family_history'
        indexes = [
            models.Index(fields=['patient', 'relationship']),
            models.Index(fields=['condition_name_encrypted']),
        ]
    
    @property
    def relative_name(self):
        return decrypt_field(self.relative_name_encrypted) if self.relative_name_encrypted else ''
    
    @relative_name.setter
    def relative_name(self, value):
        self.relative_name_encrypted = encrypt_field(value) if value else ''
    
    @property
    def condition_name(self):
        return decrypt_field(self.condition_name_encrypted) if self.condition_name_encrypted else ''
    
    @condition_name.setter
    def condition_name(self, value):
        self.condition_name_encrypted = encrypt_field(value) if value else ''
    
    @property
    def cause_of_death(self):
        return decrypt_field(self.cause_of_death_encrypted) if self.cause_of_death_encrypted else ''
    
    @cause_of_death.setter
    def cause_of_death(self, value):
        self.cause_of_death_encrypted = encrypt_field(value) if value else ''
    
    @property
    def notes(self):
        return decrypt_field(self.notes_encrypted) if self.notes_encrypted else ''
    
    @notes.setter
    def notes(self, value):
        self.notes_encrypted = encrypt_field(value) if value else ''
    
    def __str__(self):
        return f"{self.patient.get_full_name()} - {self.get_relationship_display()}: {self.condition_name}"


class SocialHistory(AuditableModel):
    """
    Social history including lifestyle factors.
    """
    SMOKING_STATUS_CHOICES = [
        ('never', 'Never Smoker'),
        ('current', 'Current Smoker'),
        ('former', 'Former Smoker'),
        ('unknown', 'Unknown'),
    ]
    
    ALCOHOL_STATUS_CHOICES = [
        ('never', 'Never'),
        ('occasional', 'Occasional'),
        ('moderate', 'Moderate'),
        ('heavy', 'Heavy'),
        ('former', 'Former User'),
        ('unknown', 'Unknown'),
    ]
    
    DRUG_STATUS_CHOICES = [
        ('never', 'Never'),
        ('current', 'Current User'),
        ('former', 'Former User'),
        ('unknown', 'Unknown'),
    ]
    
    patient = models.OneToOneField(
        Patient,
        on_delete=models.CASCADE,
        related_name='social_history'
    )
    
    # Smoking History
    smoking_status = models.CharField(max_length=20, choices=SMOKING_STATUS_CHOICES, default='unknown')
    packs_per_day = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    years_smoked = models.PositiveIntegerField(null=True, blank=True)
    quit_date = models.DateField(null=True, blank=True)
    
    # Alcohol History
    alcohol_status = models.CharField(max_length=20, choices=ALCOHOL_STATUS_CHOICES, default='unknown')
    drinks_per_week = models.PositiveIntegerField(null=True, blank=True)
    alcohol_type_encrypted = models.TextField(blank=True)  # Encrypted
    
    # Drug History
    drug_status = models.CharField(max_length=20, choices=DRUG_STATUS_CHOICES, default='unknown')
    drug_details_encrypted = models.TextField(blank=True)  # Encrypted
    
    # Occupation and Environment
    occupation_encrypted = models.TextField(blank=True)  # Encrypted
    work_environment_encrypted = models.TextField(blank=True)  # Encrypted
    occupational_hazards_encrypted = models.TextField(blank=True)  # Encrypted
    
    # Lifestyle
    exercise_frequency = models.CharField(max_length=100, blank=True)
    diet_description_encrypted = models.TextField(blank=True)  # Encrypted
    sleep_hours = models.PositiveIntegerField(null=True, blank=True)
    stress_level = models.PositiveIntegerField(null=True, blank=True)  # 1-10 scale
    
    # Travel and Living Situation
    recent_travel_encrypted = models.TextField(blank=True)  # Encrypted
    living_situation_encrypted = models.TextField(blank=True)  # Encrypted
    
    # Other
    notes_encrypted = models.TextField(blank=True)  # Encrypted
    data_source = models.ForeignKey(
        DataSource,
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )
    
    class Meta:
        db_table = 'medical_records_social_history'
    
    # Property methods for encrypted fields
    @property
    def alcohol_type(self):
        return decrypt_field(self.alcohol_type_encrypted) if self.alcohol_type_encrypted else ''
    
    @alcohol_type.setter
    def alcohol_type(self, value):
        self.alcohol_type_encrypted = encrypt_field(value) if value else ''
    
    @property
    def drug_details(self):
        return decrypt_field(self.drug_details_encrypted) if self.drug_details_encrypted else ''
    
    @drug_details.setter
    def drug_details(self, value):
        self.drug_details_encrypted = encrypt_field(value) if value else ''
    
    @property
    def occupation(self):
        return decrypt_field(self.occupation_encrypted) if self.occupation_encrypted else ''
    
    @occupation.setter
    def occupation(self, value):
        self.occupation_encrypted = encrypt_field(value) if value else ''
    
    @property
    def work_environment(self):
        return decrypt_field(self.work_environment_encrypted) if self.work_environment_encrypted else ''
    
    @work_environment.setter
    def work_environment(self, value):
        self.work_environment_encrypted = encrypt_field(value) if value else ''
    
    @property
    def occupational_hazards(self):
        return decrypt_field(self.occupational_hazards_encrypted) if self.occupational_hazards_encrypted else ''
    
    @occupational_hazards.setter
    def occupational_hazards(self, value):
        self.occupational_hazards_encrypted = encrypt_field(value) if value else ''
    
    @property
    def diet_description(self):
        return decrypt_field(self.diet_description_encrypted) if self.diet_description_encrypted else ''
    
    @diet_description.setter
    def diet_description(self, value):
        self.diet_description_encrypted = encrypt_field(value) if value else ''
    
    @property
    def recent_travel(self):
        return decrypt_field(self.recent_travel_encrypted) if self.recent_travel_encrypted else ''
    
    @recent_travel.setter
    def recent_travel(self, value):
        self.recent_travel_encrypted = encrypt_field(value) if value else ''
    
    @property
    def living_situation(self):
        return decrypt_field(self.living_situation_encrypted) if self.living_situation_encrypted else ''
    
    @living_situation.setter
    def living_situation(self, value):
        self.living_situation_encrypted = encrypt_field(value) if value else ''
    
    @property
    def notes(self):
        return decrypt_field(self.notes_encrypted) if self.notes_encrypted else ''
    
    @notes.setter
    def notes(self, value):
        self.notes_encrypted = encrypt_field(value) if value else ''
    
    def __str__(self):
        return f"Social History - {self.patient.get_full_name()}"


class Medication(AuditableModel):
    """
    Current and past medications.
    """
    MEDICATION_TYPES = [
        ('prescription', 'Prescription'),
        ('otc', 'Over-the-Counter'),
        ('supplement', 'Supplement'),
        ('herbal', 'Herbal'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('discontinued', 'Discontinued'),
        ('completed', 'Completed'),
        ('on_hold', 'On Hold'),
    ]
    
    FREQUENCY_CHOICES = [
        ('once_daily', 'Once Daily'),
        ('twice_daily', 'Twice Daily'),
        ('three_times_daily', 'Three Times Daily'),
        ('four_times_daily', 'Four Times Daily'),
        ('as_needed', 'As Needed'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('other', 'Other'),
    ]
    
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='medications'
    )
    medication_name_encrypted = models.TextField()  # Encrypted
    generic_name_encrypted = models.TextField(blank=True)  # Encrypted
    medication_type = models.CharField(max_length=20, choices=MEDICATION_TYPES, default='prescription')
    strength_encrypted = models.TextField(blank=True)  # Encrypted
    dosage_form = models.CharField(max_length=50, blank=True)  # tablet, capsule, liquid, etc.
    dosage_encrypted = models.TextField(blank=True)  # Encrypted
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, blank=True)
    route = models.CharField(max_length=50, blank=True)  # oral, topical, injection, etc.
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    prescribing_physician_encrypted = models.TextField(blank=True)  # Encrypted
    indication_encrypted = models.TextField(blank=True)  # Encrypted - Why prescribed
    notes_encrypted = models.TextField(blank=True)  # Encrypted
    rxnorm_code = models.ForeignKey(
        MedicalCode,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        limit_choices_to={'code_system': 'rxnorm'}
    )
    data_source = models.ForeignKey(
        DataSource,
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )
    
    class Meta:
        db_table = 'medical_records_medication'
        indexes = [
            models.Index(fields=['patient', 'status']),
            models.Index(fields=['start_date']),
            models.Index(fields=['medication_name_encrypted']),
        ]
    
    # Property methods for encrypted fields
    @property
    def medication_name(self):
        return decrypt_field(self.medication_name_encrypted) if self.medication_name_encrypted else ''
    
    @medication_name.setter
    def medication_name(self, value):
        self.medication_name_encrypted = encrypt_field(value) if value else ''
    
    @property
    def generic_name(self):
        return decrypt_field(self.generic_name_encrypted) if self.generic_name_encrypted else ''
    
    @generic_name.setter
    def generic_name(self, value):
        self.generic_name_encrypted = encrypt_field(value) if value else ''
    
    @property
    def strength(self):
        return decrypt_field(self.strength_encrypted) if self.strength_encrypted else ''
    
    @strength.setter
    def strength(self, value):
        self.strength_encrypted = encrypt_field(value) if value else ''
    
    @property
    def dosage(self):
        return decrypt_field(self.dosage_encrypted) if self.dosage_encrypted else ''
    
    @dosage.setter
    def dosage(self, value):
        self.dosage_encrypted = encrypt_field(value) if value else ''
    
    @property
    def prescribing_physician(self):
        return decrypt_field(self.prescribing_physician_encrypted) if self.prescribing_physician_encrypted else ''
    
    @prescribing_physician.setter
    def prescribing_physician(self, value):
        self.prescribing_physician_encrypted = encrypt_field(value) if value else ''
    
    @property
    def indication(self):
        return decrypt_field(self.indication_encrypted) if self.indication_encrypted else ''
    
    @indication.setter
    def indication(self, value):
        self.indication_encrypted = encrypt_field(value) if value else ''
    
    @property
    def notes(self):
        return decrypt_field(self.notes_encrypted) if self.notes_encrypted else ''
    
    @notes.setter
    def notes(self, value):
        self.notes_encrypted = encrypt_field(value) if value else ''
    
    def __str__(self):
        return f"{self.patient.get_full_name()} - {self.medication_name}"


class Allergy(AuditableModel):
    """
    Patient allergies and adverse reactions.
    """
    ALLERGY_TYPES = [
        ('drug', 'Drug Allergy'),
        ('food', 'Food Allergy'),
        ('environmental', 'Environmental Allergy'),
        ('contact', 'Contact Allergy'),
        ('other', 'Other'),
    ]
    
    SEVERITY_LEVELS = [
        ('mild', 'Mild'),
        ('moderate', 'Moderate'),
        ('severe', 'Severe'),
        ('life_threatening', 'Life Threatening'),
        ('unknown', 'Unknown'),
    ]
    
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='allergies'
    )
    allergen_encrypted = models.TextField()  # Encrypted
    allergy_type = models.CharField(max_length=20, choices=ALLERGY_TYPES)
    severity = models.CharField(max_length=20, choices=SEVERITY_LEVELS, default='unknown')
    reaction_encrypted = models.TextField()  # Encrypted
    onset_date = models.DateField(null=True, blank=True)
    notes_encrypted = models.TextField(blank=True)  # Encrypted
    verified = models.BooleanField(default=False)
    data_source = models.ForeignKey(
        DataSource,
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )
    
    class Meta:
        db_table = 'medical_records_allergy'
        indexes = [
            models.Index(fields=['patient', 'allergy_type']),
            models.Index(fields=['severity']),
            models.Index(fields=['allergen_encrypted']),
        ]
    
    @property
    def allergen(self):
        return decrypt_field(self.allergen_encrypted) if self.allergen_encrypted else ''
    
    @allergen.setter
    def allergen(self, value):
        self.allergen_encrypted = encrypt_field(value) if value else ''
    
    @property
    def reaction(self):
        return decrypt_field(self.reaction_encrypted) if self.reaction_encrypted else ''
    
    @reaction.setter
    def reaction(self, value):
        self.reaction_encrypted = encrypt_field(value) if value else ''
    
    @property
    def notes(self):
        return decrypt_field(self.notes_encrypted) if self.notes_encrypted else ''
    
    @notes.setter
    def notes(self, value):
        self.notes_encrypted = encrypt_field(value) if value else ''
    
    def __str__(self):
        return f"{self.patient.get_full_name()} - {self.allergen} ({self.get_severity_display()})"


class ReviewOfSystems(AuditableModel):
    """
    Systematic review of systems by body system.
    """
    SYSTEM_STATUS_CHOICES = [
        ('negative', 'Negative'),
        ('positive', 'Positive'),
        ('not_assessed', 'Not Assessed'),
        ('unable_to_assess', 'Unable to Assess'),
    ]
    
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='review_of_systems'
    )
    encounter_date = models.DateField(default=timezone.now)
    
    # Constitutional
    constitutional_status = models.CharField(max_length=20, choices=SYSTEM_STATUS_CHOICES, default='not_assessed')
    constitutional_notes_encrypted = models.TextField(blank=True)  # Encrypted
    
    # Cardiovascular
    cardiovascular_status = models.CharField(max_length=20, choices=SYSTEM_STATUS_CHOICES, default='not_assessed')
    cardiovascular_notes_encrypted = models.TextField(blank=True)  # Encrypted
    
    # Respiratory
    respiratory_status = models.CharField(max_length=20, choices=SYSTEM_STATUS_CHOICES, default='not_assessed')
    respiratory_notes_encrypted = models.TextField(blank=True)  # Encrypted
    
    # Gastrointestinal
    gastrointestinal_status = models.CharField(max_length=20, choices=SYSTEM_STATUS_CHOICES, default='not_assessed')
    gastrointestinal_notes_encrypted = models.TextField(blank=True)  # Encrypted
    
    # Genitourinary
    genitourinary_status = models.CharField(max_length=20, choices=SYSTEM_STATUS_CHOICES, default='not_assessed')
    genitourinary_notes_encrypted = models.TextField(blank=True)  # Encrypted
    
    # Neurological
    neurological_status = models.CharField(max_length=20, choices=SYSTEM_STATUS_CHOICES, default='not_assessed')
    neurological_notes_encrypted = models.TextField(blank=True)  # Encrypted
    
    # Musculoskeletal
    musculoskeletal_status = models.CharField(max_length=20, choices=SYSTEM_STATUS_CHOICES, default='not_assessed')
    musculoskeletal_notes_encrypted = models.TextField(blank=True)  # Encrypted
    
    # Endocrine
    endocrine_status = models.CharField(max_length=20, choices=SYSTEM_STATUS_CHOICES, default='not_assessed')
    endocrine_notes_encrypted = models.TextField(blank=True)  # Encrypted
    
    # Hematologic/Lymphatic
    hematologic_status = models.CharField(max_length=20, choices=SYSTEM_STATUS_CHOICES, default='not_assessed')
    hematologic_notes_encrypted = models.TextField(blank=True)  # Encrypted
    
    # Psychiatric
    psychiatric_status = models.CharField(max_length=20, choices=SYSTEM_STATUS_CHOICES, default='not_assessed')
    psychiatric_notes_encrypted = models.TextField(blank=True)  # Encrypted
    
    data_source = models.ForeignKey(
        DataSource,
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )
    
    class Meta:
        db_table = 'medical_records_review_of_systems'
        indexes = [
            models.Index(fields=['patient', 'encounter_date']),
        ]
    
    # Property methods for encrypted notes fields
    def _get_encrypted_notes(self, field_name):
        field_value = getattr(self, f"{field_name}_notes_encrypted", "")
        return decrypt_field(field_value) if field_value else ''
    
    def _set_encrypted_notes(self, field_name, value):
        setattr(self, f"{field_name}_notes_encrypted", encrypt_field(value) if value else '')
    
    @property
    def constitutional_notes(self):
        return self._get_encrypted_notes('constitutional')
    
    @constitutional_notes.setter
    def constitutional_notes(self, value):
        self._set_encrypted_notes('constitutional', value)
    
    # Similar properties for other systems...
    # (Adding all would make this very long, but the pattern is the same)
    
    def __str__(self):
        return f"ROS - {self.patient.get_full_name()} ({self.encounter_date})"