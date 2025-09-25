"""
Serializers for patients API endpoints.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from core.models import Address, PhoneNumber
from .models import Patient, PatientIdentifier, PatientNote, PatientConsent
from datetime import date

User = get_user_model()


class AddressSerializer(serializers.ModelSerializer):
    """
    Serializer for Address model.
    """
    class Meta:
        model = Address
        fields = [
            'id', 'street_address_1', 'street_address_2', 'city',
            'state', 'postal_code', 'country'
        ]
        read_only_fields = ['id']


class PhoneNumberSerializer(serializers.ModelSerializer):
    """
    Serializer for PhoneNumber model.
    """
    class Meta:
        model = PhoneNumber
        fields = ['id', 'phone_number', 'phone_type', 'is_primary']
        read_only_fields = ['id']


class PatientIdentifierSerializer(serializers.ModelSerializer):
    """
    Serializer for PatientIdentifier model.
    """
    identifier_value = serializers.CharField(write_only=True)
    
    class Meta:
        model = PatientIdentifier
        fields = [
            'id', 'identifier_type', 'identifier_value', 'issuing_authority',
            'issue_date', 'expiration_date'
        ]
        read_only_fields = ['id']
    
    def create(self, validated_data):
        identifier_value = validated_data.pop('identifier_value')
        instance = PatientIdentifier.objects.create(**validated_data)
        instance.identifier_value = identifier_value
        instance.save()
        return instance
    
    def update(self, instance, validated_data):
        if 'identifier_value' in validated_data:
            instance.identifier_value = validated_data.pop('identifier_value')
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class PatientNoteSerializer(serializers.ModelSerializer):
    """
    Serializer for PatientNote model.
    """
    content = serializers.CharField(write_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = PatientNote
        fields = [
            'id', 'note_type', 'title', 'content', 'is_alert',
            'alert_expiry', 'created_at', 'created_by_name'
        ]
        read_only_fields = ['id', 'created_at']
    
    def create(self, validated_data):
        content = validated_data.pop('content')
        instance = PatientNote.objects.create(**validated_data)
        instance.content = content
        instance.save()
        return instance
    
    def update(self, instance, validated_data):
        if 'content' in validated_data:
            instance.content = validated_data.pop('content')
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class PatientConsentSerializer(serializers.ModelSerializer):
    """
    Serializer for PatientConsent model.
    """
    witness_name = serializers.CharField(source='witness.get_full_name', read_only=True)
    
    class Meta:
        model = PatientConsent
        fields = [
            'id', 'consent_type', 'is_granted', 'consent_date',
            'expiry_date', 'witness', 'witness_name', 'notes'
        ]
        read_only_fields = ['id']


class PatientSerializer(serializers.ModelSerializer):
    """
    Comprehensive serializer for Patient model with permission-based field filtering.
    """
    # Encrypted fields
    first_name = serializers.CharField(write_only=True)
    last_name = serializers.CharField(write_only=True)
    middle_name = serializers.CharField(write_only=True, required=False, allow_blank=True)
    date_of_birth = serializers.DateField(write_only=True)
    ssn = serializers.CharField(write_only=True, required=False, allow_blank=True)
    email = serializers.EmailField(write_only=True, required=False, allow_blank=True)
    primary_insurance = serializers.CharField(write_only=True, required=False, allow_blank=True)
    secondary_insurance = serializers.CharField(write_only=True, required=False, allow_blank=True)
    emergency_contact_name = serializers.CharField(write_only=True, required=False, allow_blank=True)
    emergency_contact_phone = serializers.CharField(write_only=True, required=False, allow_blank=True)
    
    # Read-only computed fields
    full_name = serializers.SerializerMethodField()
    age = serializers.SerializerMethodField()
    ssn_last_four = serializers.SerializerMethodField()
    
    # Related fields
    primary_address = AddressSerializer(read_only=True)
    phone_numbers = PhoneNumberSerializer(many=True, read_only=True)
    identifiers = PatientIdentifierSerializer(many=True, read_only=True)
    notes = PatientNoteSerializer(many=True, read_only=True)
    consents = PatientConsentSerializer(many=True, read_only=True)
    primary_physician_name = serializers.CharField(
        source='primary_physician.get_full_name', read_only=True
    )
    
    class Meta:
        model = Patient
        fields = [
            'id', 'medical_record_number', 'first_name', 'last_name', 'middle_name',
            'full_name', 'date_of_birth', 'age', 'ssn', 'ssn_last_four',
            'gender', 'ethnicity', 'race', 'marital_status',
            'primary_address', 'phone_numbers', 'email',
            'preferred_language', 'religion',
            'primary_insurance', 'secondary_insurance',
            'emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relationship',
            'primary_physician', 'primary_physician_name',
            'identifiers', 'notes', 'consents',
            'photo', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'medical_record_number', 'full_name', 'age', 'ssn_last_four',
            'created_at', 'updated_at'
        ]
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    
    def get_age(self, obj):
        return obj.get_age()
    
    def get_ssn_last_four(self, obj):
        return obj.ssn_last_four
    
    def validate_date_of_birth(self, value):
        """
        Validate date of birth is not in the future.
        """
        if value > date.today():
            raise serializers.ValidationError("Date of birth cannot be in the future.")
        return value
    
    def validate_ssn(self, value):
        """
        Validate SSN format.
        """
        if value:
            # Remove any non-digit characters
            clean_ssn = ''.join(filter(str.isdigit, value))
            if len(clean_ssn) != 9:
                raise serializers.ValidationError("SSN must be 9 digits.")
        return value
    
    def create(self, validated_data):
        """
        Create patient with encrypted fields.
        """
        # Extract encrypted fields
        encrypted_fields = {}
        for field in ['first_name', 'last_name', 'middle_name', 'date_of_birth', 
                     'ssn', 'email', 'primary_insurance', 'secondary_insurance',
                     'emergency_contact_name', 'emergency_contact_phone']:
            if field in validated_data:
                encrypted_fields[field] = validated_data.pop(field)
        
        # Create patient instance
        patient = Patient.objects.create(**validated_data)
        
        # Set encrypted fields
        for field, value in encrypted_fields.items():
            setattr(patient, field, value)
        
        patient.save()
        return patient
    
    def update(self, instance, validated_data):
        """
        Update patient with encrypted fields.
        """
        # Extract encrypted fields
        encrypted_fields = {}
        for field in ['first_name', 'last_name', 'middle_name', 'date_of_birth',
                     'ssn', 'email', 'primary_insurance', 'secondary_insurance',
                     'emergency_contact_name', 'emergency_contact_phone']:
            if field in validated_data:
                encrypted_fields[field] = validated_data.pop(field)
        
        # Update regular fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # Update encrypted fields
        for field, value in encrypted_fields.items():
            setattr(instance, field, value)
        
        instance.save()
        return instance
    
    def to_representation(self, instance):
        """
        Filter sensitive data based on user permissions.
        """
        data = super().to_representation(instance)
        request = self.context.get('request')
        
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            user = request.user
            permissions = user.get_permissions_for_patient(instance)
            
            # If user can't view this patient, return limited data
            if not permissions['can_view']:
                return {
                    'id': data['id'],
                    'medical_record_number': data['medical_record_number'],
                    'message': 'Access denied to patient data'
                }
            
            # Filter sensitive fields for non-healthcare providers
            if user.role == 'patient' and user.patient_profile != instance:
                sensitive_fields = [
                    'ssn_last_four', 'primary_insurance', 'secondary_insurance',
                    'notes', 'identifiers'
                ]
                for field in sensitive_fields:
                    data.pop(field, None)
        
        return data


class PatientSearchSerializer(serializers.Serializer):
    """
    Serializer for patient search parameters.
    """
    query = serializers.CharField(required=False, allow_blank=True)
    medical_record_number = serializers.CharField(required=False, allow_blank=True)
    date_of_birth = serializers.DateField(required=False)
    gender = serializers.ChoiceField(choices=Patient.GENDER_CHOICES, required=False)
    primary_physician = serializers.UUIDField(required=False)
    is_active = serializers.BooleanField(required=False, default=True)
    
    def validate(self, data):
        """
        Ensure at least one search parameter is provided.
        """
        if not any(data.values()):
            raise serializers.ValidationError("At least one search parameter must be provided.")
        return data


class PatientSummarySerializer(serializers.ModelSerializer):
    """
    Lightweight patient serializer for lists and summaries.
    """
    full_name = serializers.SerializerMethodField()
    age = serializers.SerializerMethodField()
    primary_physician_name = serializers.CharField(
        source='primary_physician.get_full_name', read_only=True
    )
    
    class Meta:
        model = Patient
        fields = [
            'id', 'medical_record_number', 'full_name', 'age', 'gender',
            'primary_physician_name', 'is_active'
        ]
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    
    def get_age(self, obj):
        return obj.get_age()