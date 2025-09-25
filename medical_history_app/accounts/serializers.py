"""
Serializers for accounts API endpoints.
"""
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User, Organization, UserProfile


class OrganizationSerializer(serializers.ModelSerializer):
    """
    Serializer for Organization model.
    """
    class Meta:
        model = Organization
        fields = ['id', 'name', 'organization_type', 'npi_number', 'email', 'website']
        read_only_fields = ['id']


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for UserProfile model.
    """
    class Meta:
        model = UserProfile
        fields = [
            'middle_name', 'date_of_birth', 'emergency_contact_name',
            'emergency_contact_phone', 'emergency_contact_relationship',
            'timezone', 'language_preference'
        ]


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model with role-based field filtering.
    """
    profile = UserProfileSerializer(read_only=True)
    organization = OrganizationSerializer(read_only=True)
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'full_name',
            'role', 'specialty', 'license_number', 'npi_number', 'organization',
            'is_verified', 'date_joined', 'last_login', 'profile'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login', 'is_verified']
        extra_kwargs = {
            'npi_number': {'write_only': True},
            'license_number': {'write_only': True},
        }
    
    def to_representation(self, instance):
        """
        Filter sensitive fields based on user permissions.
        """
        data = super().to_representation(instance)
        request = self.context.get('request')
        
        if request and request.user:
            # Patients can only see their own sensitive information
            if request.user.role == 'patient' and request.user != instance:
                sensitive_fields = ['email', 'npi_number', 'license_number', 'profile']
                for field in sensitive_fields:
                    data.pop(field, None)
            
            # Non-admin users cannot see certain admin-only fields
            if request.user.role != 'admin':
                admin_only_fields = ['is_verified']
                for field in admin_only_fields:
                    data.pop(field, None)
        
        return data


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    """
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    terms_accepted = serializers.BooleanField(write_only=True)
    privacy_policy_accepted = serializers.BooleanField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'role', 'specialty',
            'license_number', 'npi_number', 'organization',
            'terms_accepted', 'privacy_policy_accepted'
        ]
    
    def validate(self, attrs):
        """
        Validate password confirmation and required fields.
        """
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match.")
        
        if not attrs.get('terms_accepted'):
            raise serializers.ValidationError("You must accept the terms of service.")
        
        if not attrs.get('privacy_policy_accepted'):
            raise serializers.ValidationError("You must accept the privacy policy.")
        
        # Validate role-specific requirements
        role = attrs.get('role')
        if role in ['physician', 'nurse', 'medical_assistant']:
            if not attrs.get('license_number'):
                raise serializers.ValidationError("License number is required for healthcare providers.")
        
        if role == 'physician':
            if not attrs.get('npi_number'):
                raise serializers.ValidationError("NPI number is required for physicians.")
        
        return attrs
    
    def create(self, validated_data):
        """
        Create user with validated data.
        """
        # Remove non-model fields
        validated_data.pop('password_confirm')
        terms_accepted = validated_data.pop('terms_accepted')
        privacy_policy_accepted = validated_data.pop('privacy_policy_accepted')
        
        # Create user
        user = User.objects.create_user(**validated_data)
        
        # Set acceptance timestamps
        from django.utils import timezone
        if terms_accepted:
            user.terms_accepted_at = timezone.now()
        if privacy_policy_accepted:
            user.privacy_policy_accepted_at = timezone.now()
        
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    """
    Serializer for user authentication.
    """
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        """
        Validate user credentials.
        """
        username = attrs.get('username')
        password = attrs.get('password')
        
        if username and password:
            user = authenticate(
                request=self.context.get('request'),
                username=username,
                password=password
            )
            
            if not user:
                raise serializers.ValidationError('Invalid credentials.')
            
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled.')
            
            # Check if account is locked
            from django.utils import timezone
            if user.account_locked_until and user.account_locked_until > timezone.now():
                raise serializers.ValidationError('Account is temporarily locked.')
            
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError('Must include username and password.')


class PasswordChangeSerializer(serializers.Serializer):
    """
    Serializer for password change.
    """
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        """
        Validate password change request.
        """
        user = self.context['request'].user
        
        # Check old password
        if not user.check_password(attrs['old_password']):
            raise serializers.ValidationError({'old_password': 'Incorrect password.'})
        
        # Check new password confirmation
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("New passwords don't match.")
        
        # Check password history (prevent reuse of last 5 passwords)
        from .models import PasswordHistory
        from django.contrib.auth.hashers import check_password
        
        recent_passwords = PasswordHistory.objects.filter(
            user=user
        ).order_by('-created_at')[:5]
        
        for password_history in recent_passwords:
            if check_password(attrs['new_password'], password_history.password_hash):
                raise serializers.ValidationError(
                    "You cannot reuse one of your last 5 passwords."
                )
        
        return attrs