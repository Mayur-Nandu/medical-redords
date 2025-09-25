"""
Medical History Serializers
"""

from rest_framework import serializers
from .models import MedicalHistory, Medication, Allergy, Immunization, SocialHistory


class MedicalHistorySerializer(serializers.ModelSerializer):
    """Medical history serializer"""
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    patient_id = serializers.CharField(source='patient.patient_id', read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    updated_by_username = serializers.CharField(source='updated_by.username', read_only=True)
    
    class Meta:
        model = MedicalHistory
        fields = [
            'id', 'patient', 'patient_name', 'patient_id', 'visit_date', 'visit_type',
            'chief_complaint', 'hpi_duration', 'hpi_location', 'hpi_quality',
            'hpi_severity', 'hpi_timing', 'hpi_context', 'hpi_modifying_factors',
            'hpi_associated_symptoms', 'past_medical_history', 'past_surgeries',
            'past_hospitalizations', 'past_trauma', 'family_history',
            'family_cancer_history', 'family_heart_disease', 'family_diabetes',
            'family_hypertension', 'family_mental_health', 'family_other',
            'smoking_status', 'smoking_pack_years', 'alcohol_use', 'drug_use',
            'occupation', 'education_level', 'marital_status', 'living_situation',
            'travel_history', 'constitutional_symptoms', 'eyes_ears_nose_throat',
            'cardiovascular', 'respiratory', 'gastrointestinal', 'genitourinary',
            'musculoskeletal', 'neurological', 'psychiatric', 'endocrine',
            'hematologic', 'skin', 'completeness_score', 'reliability_score',
            'data_source', 'is_active', 'created_by_username', 'updated_by_username',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by', 'updated_by']
    
    def create(self, validated_data):
        """Create medical history with audit trail"""
        request = self.context.get('request')
        if request and request.user:
            validated_data['created_by'] = request.user
            validated_data['updated_by'] = request.user
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """Update medical history with audit trail"""
        request = self.context.get('request')
        if request and request.user:
            validated_data['updated_by'] = request.user
        return super().update(instance, validated_data)


class MedicationSerializer(serializers.ModelSerializer):
    """Medication serializer"""
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    patient_id = serializers.CharField(source='patient.patient_id', read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    updated_by_username = serializers.CharField(source='updated_by.username', read_only=True)
    
    class Meta:
        model = Medication
        fields = [
            'id', 'patient', 'patient_name', 'patient_id', 'medical_history',
            'name', 'generic_name', 'medication_type', 'dosage', 'frequency',
            'route', 'start_date', 'end_date', 'is_current', 'prescribed_by',
            'pharmacy', 'indication', 'side_effects', 'effectiveness',
            'compliance_rate', 'compliance_notes', 'created_by_username',
            'updated_by_username', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by', 'updated_by']
    
    def create(self, validated_data):
        """Create medication with audit trail"""
        request = self.context.get('request')
        if request and request.user:
            validated_data['created_by'] = request.user
            validated_data['updated_by'] = request.user
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """Update medication with audit trail"""
        request = self.context.get('request')
        if request and request.user:
            validated_data['updated_by'] = request.user
        return super().update(instance, validated_data)


class AllergySerializer(serializers.ModelSerializer):
    """Allergy serializer"""
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    patient_id = serializers.CharField(source='patient.patient_id', read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    updated_by_username = serializers.CharField(source='updated_by.username', read_only=True)
    
    class Meta:
        model = Allergy
        fields = [
            'id', 'patient', 'patient_name', 'patient_id', 'medical_history',
            'allergen', 'allergy_type', 'severity', 'reaction_description',
            'onset_date', 'last_reaction_date', 'symptoms', 'treatment_required',
            'treatment_description', 'confirmed_by_testing', 'testing_method',
            'cross_reactive_allergens', 'avoidance_instructions', 'is_active',
            'created_by_username', 'updated_by_username', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by', 'updated_by']
    
    def create(self, validated_data):
        """Create allergy with audit trail"""
        request = self.context.get('request')
        if request and request.user:
            validated_data['created_by'] = request.user
            validated_data['updated_by'] = request.user
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """Update allergy with audit trail"""
        request = self.context.get('request')
        if request and request.user:
            validated_data['updated_by'] = request.user
        return super().update(instance, validated_data)


class ImmunizationSerializer(serializers.ModelSerializer):
    """Immunization serializer"""
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    patient_id = serializers.CharField(source='patient.patient_id', read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    updated_by_username = serializers.CharField(source='updated_by.username', read_only=True)
    
    class Meta:
        model = Immunization
        fields = [
            'id', 'patient', 'patient_name', 'patient_id', 'medical_history',
            'vaccine_name', 'vaccine_code', 'manufacturer', 'lot_number',
            'administration_date', 'expiration_date', 'administered_by',
            'administration_site', 'route', 'dosage', 'series_number',
            'total_series_doses', 'is_complete', 'adverse_reactions',
            'contraindications', 'created_by_username', 'updated_by_username',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by', 'updated_by']
    
    def create(self, validated_data):
        """Create immunization with audit trail"""
        request = self.context.get('request')
        if request and request.user:
            validated_data['created_by'] = request.user
            validated_data['updated_by'] = request.user
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """Update immunization with audit trail"""
        request = self.context.get('request')
        if request and request.user:
            validated_data['updated_by'] = request.user
        return super().update(instance, validated_data)


class SocialHistorySerializer(serializers.ModelSerializer):
    """Social history serializer"""
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    patient_id = serializers.CharField(source='patient.patient_id', read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    updated_by_username = serializers.CharField(source='updated_by.username', read_only=True)
    
    class Meta:
        model = SocialHistory
        fields = [
            'id', 'patient', 'patient_name', 'patient_id', 'medical_history',
            'smoking_status', 'smoking_start_age', 'smoking_stop_age',
            'cigarettes_per_day', 'pack_years', 'secondhand_smoke_exposure',
            'alcohol_use', 'drinks_per_week', 'alcohol_type', 'alcohol_related_problems',
            'drug_use', 'drug_types', 'injection_drug_use', 'drug_treatment_history',
            'sexual_activity', 'sexual_orientation', 'number_of_partners',
            'safe_sex_practices', 'std_history', 'current_occupation',
            'occupational_hazards', 'work_stress_level', 'living_arrangement',
            'housing_type', 'financial_stress', 'social_support', 'recent_travel',
            'travel_destinations', 'travel_dates', 'travel_vaccinations',
            'exercise_frequency', 'diet_type', 'dietary_restrictions', 'stress_level',
            'mental_health_history', 'counseling_history', 'created_by_username',
            'updated_by_username', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by', 'updated_by']
    
    def create(self, validated_data):
        """Create social history with audit trail"""
        request = self.context.get('request')
        if request and request.user:
            validated_data['created_by'] = request.user
            validated_data['updated_by'] = request.user
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """Update social history with audit trail"""
        request = self.context.get('request')
        if request and request.user:
            validated_data['updated_by'] = request.user
        return super().update(instance, validated_data)