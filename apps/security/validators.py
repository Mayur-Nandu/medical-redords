"""
Security validators for HIPAA compliance
"""

from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import CommonPasswordValidator
import re
import string


class HIPAAPasswordValidator:
    """
    HIPAA-compliant password validator
    """
    
    def __init__(self):
        self.min_length = 12
        self.require_uppercase = True
        self.require_lowercase = True
        self.require_numbers = True
        self.require_special_chars = True
        self.special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    
    def validate(self, password, user=None):
        """Validate password meets HIPAA requirements"""
        errors = []
        
        # Check minimum length
        if len(password) < self.min_length:
            errors.append(
                ValidationError(
                    f"Password must be at least {self.min_length} characters long.",
                    code='password_too_short',
                )
            )
        
        # Check for uppercase letters
        if self.require_uppercase and not any(c.isupper() for c in password):
            errors.append(
                ValidationError(
                    "Password must contain at least one uppercase letter.",
                    code='password_no_upper',
                )
            )
        
        # Check for lowercase letters
        if self.require_lowercase and not any(c.islower() for c in password):
            errors.append(
                ValidationError(
                    "Password must contain at least one lowercase letter.",
                    code='password_no_lower',
                )
            )
        
        # Check for numbers
        if self.require_numbers and not any(c.isdigit() for c in password):
            errors.append(
                ValidationError(
                    "Password must contain at least one number.",
                    code='password_no_number',
                )
            )
        
        # Check for special characters
        if self.require_special_chars and not any(c in self.special_chars for c in password):
            errors.append(
                ValidationError(
                    f"Password must contain at least one special character: {self.special_chars}",
                    code='password_no_special',
                )
            )
        
        # Check for common patterns
        if self._has_common_patterns(password):
            errors.append(
                ValidationError(
                    "Password contains common patterns that are not allowed.",
                    code='password_common_pattern',
                )
            )
        
        # Check for user information
        if user and self._contains_user_info(password, user):
            errors.append(
                ValidationError(
                    "Password cannot contain your username or personal information.",
                    code='password_user_info',
                )
            )
        
        if errors:
            raise ValidationError(errors)
    
    def get_help_text(self):
        """Return help text for password requirements"""
        return (
            f"Password must be at least {self.min_length} characters long and contain "
            f"at least one uppercase letter, one lowercase letter, one number, and one "
            f"special character ({self.special_chars}). Password cannot contain common "
            f"patterns or personal information."
        )
    
    def _has_common_patterns(self, password):
        """Check for common password patterns"""
        # Check for sequential characters
        sequential_patterns = [
            '123456', 'abcdef', 'qwerty', 'asdfgh', 'zxcvbn',
            'password', 'admin', 'user', 'login', 'welcome'
        ]
        
        password_lower = password.lower()
        for pattern in sequential_patterns:
            if pattern in password_lower:
                return True
        
        # Check for repeated characters
        if len(set(password)) < len(password) * 0.6:  # Less than 60% unique characters
            return True
        
        return False
    
    def _contains_user_info(self, password, user):
        """Check if password contains user information"""
        password_lower = password.lower()
        
        # Check username
        if user.username.lower() in password_lower:
            return True
        
        # Check email
        if user.email and user.email.lower() in password_lower:
            return True
        
        # Check first/last name
        if hasattr(user, 'first_name') and user.first_name:
            if user.first_name.lower() in password_lower:
                return True
        
        if hasattr(user, 'last_name') and user.last_name:
            if user.last_name.lower() in password_lower:
                return True
        
        return False


class DataClassificationValidator:
    """
    Validator for data classification and sensitivity levels
    """
    
    SENSITIVITY_LEVELS = [
        ('PUBLIC', 'Public'),
        ('INTERNAL', 'Internal'),
        ('CONFIDENTIAL', 'Confidential'),
        ('RESTRICTED', 'Restricted'),
    ]
    
    @classmethod
    def validate_patient_data(cls, data):
        """Validate patient data classification"""
        # All patient data is considered RESTRICTED under HIPAA
        return 'RESTRICTED'
    
    @classmethod
    def validate_medical_history(cls, data):
        """Validate medical history data classification"""
        # Medical history is RESTRICTED
        return 'RESTRICTED'
    
    @classmethod
    def validate_clinical_data(cls, data):
        """Validate clinical data classification"""
        # Clinical data is RESTRICTED
        return 'RESTRICTED'


class EncryptionValidator:
    """
    Validator for encryption requirements
    """
    
    @classmethod
    def validate_encryption_key(cls, key):
        """Validate encryption key strength"""
        if not key:
            raise ValidationError("Encryption key is required")
        
        if len(key) < 32:
            raise ValidationError("Encryption key must be at least 32 characters long")
        
        # Check for sufficient entropy
        if cls._calculate_entropy(key) < 4.0:
            raise ValidationError("Encryption key has insufficient entropy")
    
    @classmethod
    def _calculate_entropy(cls, key):
        """Calculate entropy of encryption key"""
        import math
        from collections import Counter
        
        # Count character frequencies
        counts = Counter(key)
        length = len(key)
        
        # Calculate entropy
        entropy = 0
        for count in counts.values():
            probability = count / length
            entropy -= probability * math.log2(probability)
        
        return entropy


class AccessControlValidator:
    """
    Validator for access control requirements
    """
    
    @classmethod
    def validate_user_permissions(cls, user, resource_type, action):
        """Validate user permissions for resource access"""
        required_permissions = {
            'patient': {
                'view': 'patients.view_patient',
                'create': 'patients.add_patient',
                'update': 'patients.change_patient',
                'delete': 'patients.delete_patient',
            },
            'medical_history': {
                'view': 'medical_history.view_medical_history',
                'create': 'medical_history.add_medical_history',
                'update': 'medical_history.change_medical_history',
                'delete': 'medical_history.delete_medical_history',
            },
            'clinical_data': {
                'view': 'clinical_data.view_clinical_data',
                'create': 'clinical_data.add_clinical_data',
                'update': 'clinical_data.change_clinical_data',
                'delete': 'clinical_data.delete_clinical_data',
            },
        }
        
        if resource_type not in required_permissions:
            raise ValidationError(f"Unknown resource type: {resource_type}")
        
        if action not in required_permissions[resource_type]:
            raise ValidationError(f"Unknown action: {action}")
        
        required_permission = required_permissions[resource_type][action]
        
        if not user.has_perm(required_permission):
            raise ValidationError(
                f"User does not have permission to {action} {resource_type}"
            )
    
    @classmethod
    def validate_data_access_request(cls, requester, patient, purpose):
        """Validate data access request"""
        if not requester.is_authenticated:
            raise ValidationError("User must be authenticated")
        
        if not requester.is_active:
            raise ValidationError("User account must be active")
        
        # Check if user has any patient access permissions
        if not (requester.has_perm('patients.view_patient') or 
                requester.has_perm('patients.view_all_patients')):
            raise ValidationError("User does not have patient data access permissions")
        
        # Validate purpose
        valid_purposes = [
            'TREATMENT', 'PAYMENT', 'HEALTHCARE_OPERATIONS',
            'RESEARCH', 'LEGAL', 'EMERGENCY'
        ]
        
        if purpose not in valid_purposes:
            raise ValidationError(f"Invalid purpose: {purpose}")
        
        return True