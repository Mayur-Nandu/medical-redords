"""
Patient Serializers for API
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Patient, PatientPhoto, PatientConsent, PatientAccessLog, PatientRelationship


class PatientSerializer(serializers.ModelSerializer):
    """Patient serializer with HIPAA-compliant field handling"""
    full_name = serializers.ReadOnlyField()
    age = serializers.ReadOnlyField()
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    updated_by_username = serializers.CharField(source='updated_by.username', read_only=True)
    
    class Meta:
        model = Patient
        fields = [
            'id', 'patient_id', 'first_name', 'last_name', 'middle_name', 'date_of_birth',
            'gender', 'ethnicity', 'race', 'address_line1', 'address_line2', 'city', 'state',
            'postal_code', 'country', 'phone_primary', 'phone_secondary', 'email',
            'emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relationship',
            'insurance_primary', 'insurance_primary_id', 'insurance_secondary', 'insurance_secondary_id',
            'preferred_language', 'religion', 'marital_status', 'full_name', 'age',
            'is_active', 'consent_given', 'consent_date', 'data_retention_until',
            'created_by_username', 'updated_by_username', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by', 'updated_by']
    
    def create(self, validated_data):
        """Create patient with audit trail"""
        request = self.context.get('request')
        if request and request.user:
            validated_data['created_by'] = request.user
            validated_data['updated_by'] = request.user
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """Update patient with audit trail"""
        request = self.context.get('request')
        if request and request.user:
            validated_data['updated_by'] = request.user
        return super().update(instance, validated_data)


class PatientListSerializer(serializers.ModelSerializer):
    """Simplified patient serializer for list views"""
    full_name = serializers.ReadOnlyField()
    age = serializers.ReadOnlyField()
    
    class Meta:
        model = Patient
        fields = [
            'id', 'patient_id', 'full_name', 'date_of_birth', 'age', 'gender',
            'phone_primary', 'email', 'is_active', 'created_at'
        ]


class PatientPhotoSerializer(serializers.ModelSerializer):
    """Patient photo serializer"""
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = PatientPhoto
        fields = ['id', 'patient', 'photo', 'photo_hash', 'created_by_username', 'created_at']
        read_only_fields = ['id', 'created_at', 'created_by']
    
    def create(self, validated_data):
        request = self.context.get('request')
        if request and request.user:
            validated_data['created_by'] = request.user
        return super().create(validated_data)


class PatientConsentSerializer(serializers.ModelSerializer):
    """Patient consent serializer"""
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    
    class Meta:
        model = PatientConsent
        fields = [
            'id', 'patient', 'patient_name', 'consent_type', 'consent_given',
            'consent_date', 'consent_expires', 'consent_text', 'witness_name',
            'witness_signature', 'created_by_username'
        ]
        read_only_fields = ['id', 'consent_date', 'created_by']
    
    def create(self, validated_data):
        request = self.context.get('request')
        if request and request.user:
            validated_data['created_by'] = request.user
        return super().create(validated_data)


class PatientAccessLogSerializer(serializers.ModelSerializer):
    """Patient access log serializer"""
    user_username = serializers.CharField(source='user.username', read_only=True)
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    
    class Meta:
        model = PatientAccessLog
        fields = [
            'id', 'patient', 'patient_name', 'user', 'user_username', 'access_type',
            'timestamp', 'ip_address', 'user_agent', 'reason', 'data_accessed'
        ]
        read_only_fields = ['id', 'timestamp']


class PatientRelationshipSerializer(serializers.ModelSerializer):
    """Patient relationship serializer"""
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    related_patient_name = serializers.CharField(source='related_patient.full_name', read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = PatientRelationship
        fields = [
            'id', 'patient', 'patient_name', 'related_patient', 'related_patient_name',
            'relationship_type', 'is_primary', 'notes', 'created_by_username', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'created_by']
    
    def create(self, validated_data):
        request = self.context.get('request')
        if request and request.user:
            validated_data['created_by'] = request.user
        return super().create(validated_data)