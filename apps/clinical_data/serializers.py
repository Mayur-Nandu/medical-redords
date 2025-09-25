"""
Clinical Data Serializers
"""

from rest_framework import serializers
from .models import VitalSigns, LabResult, DiagnosticImaging, ClinicalNote, PreventiveCare


class VitalSignsSerializer(serializers.ModelSerializer):
    """Vital signs serializer"""
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    patient_id = serializers.CharField(source='patient.patient_id', read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    updated_by_username = serializers.CharField(source='updated_by.username', read_only=True)
    
    class Meta:
        model = VitalSigns
        fields = [
            'id', 'patient', 'patient_name', 'patient_id', 'measurement_date',
            'measurement_type', 'systolic_bp', 'diastolic_bp', 'heart_rate',
            'temperature', 'temperature_unit', 'respiratory_rate', 'oxygen_saturation',
            'weight', 'weight_unit', 'height', 'height_unit', 'bmi', 'pain_score',
            'glucose_level', 'position', 'notes', 'created_by_username',
            'updated_by_username', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'bmi', 'created_at', 'updated_at', 'created_by', 'updated_by']
    
    def create(self, validated_data):
        """Create vital signs with audit trail"""
        request = self.context.get('request')
        if request and request.user:
            validated_data['created_by'] = request.user
            validated_data['updated_by'] = request.user
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """Update vital signs with audit trail"""
        request = self.context.get('request')
        if request and request.user:
            validated_data['updated_by'] = request.user
        return super().update(instance, validated_data)


class LabResultSerializer(serializers.ModelSerializer):
    """Lab result serializer"""
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    patient_id = serializers.CharField(source='patient.patient_id', read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    updated_by_username = serializers.CharField(source='updated_by.username', read_only=True)
    
    class Meta:
        model = LabResult
        fields = [
            'id', 'patient', 'patient_name', 'patient_id', 'test_name', 'test_code',
            'test_category', 'result_value', 'result_unit', 'reference_range',
            'critical_level', 'status', 'ordered_date', 'collected_date', 'result_date',
            'lab_name', 'lab_id', 'ordering_physician', 'clinical_notes',
            'interpretation', 'follow_up_required', 'quality_control_passed',
            'repeat_test_required', 'created_by_username', 'updated_by_username',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by', 'updated_by']
    
    def create(self, validated_data):
        """Create lab result with audit trail"""
        request = self.context.get('request')
        if request and request.user:
            validated_data['created_by'] = request.user
            validated_data['updated_by'] = request.user
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """Update lab result with audit trail"""
        request = self.context.get('request')
        if request and request.user:
            validated_data['updated_by'] = request.user
        return super().update(instance, validated_data)


class DiagnosticImagingSerializer(serializers.ModelSerializer):
    """Diagnostic imaging serializer"""
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    patient_id = serializers.CharField(source='patient.patient_id', read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    updated_by_username = serializers.CharField(source='updated_by.username', read_only=True)
    
    class Meta:
        model = DiagnosticImaging
        fields = [
            'id', 'patient', 'patient_name', 'patient_id', 'imaging_type',
            'body_part', 'study_description', 'study_code', 'ordered_date',
            'performed_date', 'report_date', 'findings', 'impression',
            'recommendations', 'clinical_indication', 'contrast_used',
            'contrast_type', 'radiologist', 'radiologist_id', 'technique',
            'radiation_dose', 'radiation_unit', 'image_quality',
            'follow_up_required', 'follow_up_interval', 'created_by_username',
            'updated_by_username', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by', 'updated_by']
    
    def create(self, validated_data):
        """Create diagnostic imaging with audit trail"""
        request = self.context.get('request')
        if request and request.user:
            validated_data['created_by'] = request.user
            validated_data['updated_by'] = request.user
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """Update diagnostic imaging with audit trail"""
        request = self.context.get('request')
        if request and request.user:
            validated_data['updated_by'] = request.user
        return super().update(instance, validated_data)


class ClinicalNoteSerializer(serializers.ModelSerializer):
    """Clinical note serializer"""
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    patient_id = serializers.CharField(source='patient.patient_id', read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    updated_by_username = serializers.CharField(source='updated_by.username', read_only=True)
    
    class Meta:
        model = ClinicalNote
        fields = [
            'id', 'patient', 'patient_name', 'patient_id', 'note_type', 'title',
            'content', 'chief_complaint', 'assessment', 'plan', 'differential_diagnosis',
            'note_date', 'encounter_date', 'author', 'author_title', 'author_signature',
            'reviewed_by', 'reviewed_date', 'approved_by', 'approved_date',
            'is_draft', 'is_final', 'requires_signature', 'created_by_username',
            'updated_by_username', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by', 'updated_by']
    
    def create(self, validated_data):
        """Create clinical note with audit trail"""
        request = self.context.get('request')
        if request and request.user:
            validated_data['created_by'] = request.user
            validated_data['updated_by'] = request.user
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """Update clinical note with audit trail"""
        request = self.context.get('request')
        if request and request.user:
            validated_data['updated_by'] = request.user
        return super().update(instance, validated_data)


class PreventiveCareSerializer(serializers.ModelSerializer):
    """Preventive care serializer"""
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    patient_id = serializers.CharField(source='patient.patient_id', read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    updated_by_username = serializers.CharField(source='updated_by.username', read_only=True)
    
    class Meta:
        model = PreventiveCare
        fields = [
            'id', 'patient', 'patient_name', 'patient_id', 'care_type', 'care_name',
            'care_description', 'due_date', 'completed_date', 'next_due_date', 'status',
            'indication', 'contraindications', 'results', 'recommendations', 'provider',
            'provider_specialty', 'quality_measure_code', 'performance_period',
            'created_by_username', 'updated_by_username', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by', 'updated_by']
    
    def create(self, validated_data):
        """Create preventive care with audit trail"""
        request = self.context.get('request')
        if request and request.user:
            validated_data['created_by'] = request.user
            validated_data['updated_by'] = request.user
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """Update preventive care with audit trail"""
        request = self.context.get('request')
        if request and request.user:
            validated_data['updated_by'] = request.user
        return super().update(instance, validated_data)