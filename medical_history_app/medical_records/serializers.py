"""
Serializers for medical records API endpoints.
"""
from rest_framework import serializers
from .models import (
    MedicalHistory, PastMedicalHistory, FamilyHistory, SocialHistory,
    Medication, Allergy, ReviewOfSystems
)


class PastMedicalHistorySerializer(serializers.ModelSerializer):
    """Serializer for PastMedicalHistory model."""
    condition_name = serializers.CharField(write_only=True)
    description = serializers.CharField(write_only=True, required=False, allow_blank=True)
    treating_physician = serializers.CharField(write_only=True, required=False, allow_blank=True)
    
    class Meta:
        model = PastMedicalHistory
        fields = [
            'id', 'condition_type', 'condition_name', 'description',
            'onset_date', 'resolution_date', 'status', 'treating_physician',
            'icd10_code', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class FamilyHistorySerializer(serializers.ModelSerializer):
    """Serializer for FamilyHistory model."""
    relative_name = serializers.CharField(write_only=True, required=False, allow_blank=True)
    condition_name = serializers.CharField(write_only=True)
    cause_of_death = serializers.CharField(write_only=True, required=False, allow_blank=True)
    notes = serializers.CharField(write_only=True, required=False, allow_blank=True)
    
    class Meta:
        model = FamilyHistory
        fields = [
            'id', 'relationship', 'relative_name', 'condition_name',
            'age_at_diagnosis', 'age_at_death', 'cause_of_death',
            'notes', 'icd10_code', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class SocialHistorySerializer(serializers.ModelSerializer):
    """Serializer for SocialHistory model."""
    alcohol_type = serializers.CharField(write_only=True, required=False, allow_blank=True)
    drug_details = serializers.CharField(write_only=True, required=False, allow_blank=True)
    occupation = serializers.CharField(write_only=True, required=False, allow_blank=True)
    work_environment = serializers.CharField(write_only=True, required=False, allow_blank=True)
    occupational_hazards = serializers.CharField(write_only=True, required=False, allow_blank=True)
    diet_description = serializers.CharField(write_only=True, required=False, allow_blank=True)
    recent_travel = serializers.CharField(write_only=True, required=False, allow_blank=True)
    living_situation = serializers.CharField(write_only=True, required=False, allow_blank=True)
    notes = serializers.CharField(write_only=True, required=False, allow_blank=True)
    
    class Meta:
        model = SocialHistory
        fields = [
            'id', 'smoking_status', 'packs_per_day', 'years_smoked', 'quit_date',
            'alcohol_status', 'drinks_per_week', 'alcohol_type',
            'drug_status', 'drug_details',
            'occupation', 'work_environment', 'occupational_hazards',
            'exercise_frequency', 'diet_description', 'sleep_hours', 'stress_level',
            'recent_travel', 'living_situation', 'notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class MedicationSerializer(serializers.ModelSerializer):
    """Serializer for Medication model."""
    medication_name = serializers.CharField(write_only=True)
    generic_name = serializers.CharField(write_only=True, required=False, allow_blank=True)
    strength = serializers.CharField(write_only=True, required=False, allow_blank=True)
    dosage = serializers.CharField(write_only=True, required=False, allow_blank=True)
    prescribing_physician = serializers.CharField(write_only=True, required=False, allow_blank=True)
    indication = serializers.CharField(write_only=True, required=False, allow_blank=True)
    notes = serializers.CharField(write_only=True, required=False, allow_blank=True)
    
    class Meta:
        model = Medication
        fields = [
            'id', 'medication_name', 'generic_name', 'medication_type',
            'strength', 'dosage_form', 'dosage', 'frequency', 'route',
            'start_date', 'end_date', 'status', 'prescribing_physician',
            'indication', 'notes', 'rxnorm_code',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class AllergySerializer(serializers.ModelSerializer):
    """Serializer for Allergy model."""
    allergen = serializers.CharField(write_only=True)
    reaction = serializers.CharField(write_only=True)
    notes = serializers.CharField(write_only=True, required=False, allow_blank=True)
    
    class Meta:
        model = Allergy
        fields = [
            'id', 'allergen', 'allergy_type', 'severity', 'reaction',
            'onset_date', 'notes', 'verified',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ReviewOfSystemsSerializer(serializers.ModelSerializer):
    """Serializer for ReviewOfSystems model."""
    constitutional_notes = serializers.CharField(write_only=True, required=False, allow_blank=True)
    cardiovascular_notes = serializers.CharField(write_only=True, required=False, allow_blank=True)
    respiratory_notes = serializers.CharField(write_only=True, required=False, allow_blank=True)
    gastrointestinal_notes = serializers.CharField(write_only=True, required=False, allow_blank=True)
    genitourinary_notes = serializers.CharField(write_only=True, required=False, allow_blank=True)
    neurological_notes = serializers.CharField(write_only=True, required=False, allow_blank=True)
    musculoskeletal_notes = serializers.CharField(write_only=True, required=False, allow_blank=True)
    endocrine_notes = serializers.CharField(write_only=True, required=False, allow_blank=True)
    hematologic_notes = serializers.CharField(write_only=True, required=False, allow_blank=True)
    psychiatric_notes = serializers.CharField(write_only=True, required=False, allow_blank=True)
    
    class Meta:
        model = ReviewOfSystems
        fields = [
            'id', 'encounter_date',
            'constitutional_status', 'constitutional_notes',
            'cardiovascular_status', 'cardiovascular_notes',
            'respiratory_status', 'respiratory_notes',
            'gastrointestinal_status', 'gastrointestinal_notes',
            'genitourinary_status', 'genitourinary_notes',
            'neurological_status', 'neurological_notes',
            'musculoskeletal_status', 'musculoskeletal_notes',
            'endocrine_status', 'endocrine_notes',
            'hematologic_status', 'hematologic_notes',
            'psychiatric_status', 'psychiatric_notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class MedicalHistorySerializer(serializers.ModelSerializer):
    """Comprehensive serializer for MedicalHistory model."""
    chief_complaint = serializers.CharField(write_only=True, required=False, allow_blank=True)
    history_of_present_illness = serializers.CharField(write_only=True, required=False, allow_blank=True)
    
    # Related data
    past_medical_history = PastMedicalHistorySerializer(many=True, read_only=True)
    family_history = FamilyHistorySerializer(many=True, read_only=True)
    social_history = SocialHistorySerializer(read_only=True)
    medications = MedicationSerializer(many=True, read_only=True)
    allergies = AllergySerializer(many=True, read_only=True)
    review_of_systems = ReviewOfSystemsSerializer(many=True, read_only=True)
    
    # Patient info
    patient_name = serializers.CharField(source='patient.get_full_name', read_only=True)
    patient_mrn = serializers.CharField(source='patient.medical_record_number', read_only=True)
    
    class Meta:
        model = MedicalHistory
        fields = [
            'id', 'patient', 'patient_name', 'patient_mrn',
            'chief_complaint', 'history_of_present_illness',
            'past_medical_history', 'family_history', 'social_history',
            'medications', 'allergies', 'review_of_systems',
            'last_updated_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']