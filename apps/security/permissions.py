"""
HIPAA-compliant permissions for medical data access
"""

from rest_framework import permissions
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from .models import SecurityEvent, DataAccessRequest


class HIPAAPermission(permissions.BasePermission):
    """
    HIPAA-compliant permission class for medical data access
    """
    
    def has_permission(self, request, view):
        """Check if user has permission to access the resource"""
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Check if user account is active
        if not request.user.is_active:
            self._log_security_event(
                request, 'PERMISSION_DENIED', 
                f"Inactive user {request.user.username} attempted access"
            )
            return False
        
        # Check session timeout
        if self._is_session_expired(request):
            self._log_security_event(
                request, 'PERMISSION_DENIED',
                f"Expired session for user {request.user.username}"
            )
            return False
        
        # Check for suspicious activity
        if self._detect_suspicious_activity(request):
            self._log_security_event(
                request, 'SUSPICIOUS_ACTIVITY',
                f"Suspicious activity detected for user {request.user.username}",
                severity='HIGH'
            )
            return False
        
        return True
    
    def has_object_permission(self, request, view, obj):
        """Check if user has permission to access specific object"""
        if not self.has_permission(request, view):
            return False
        
        # For patient data, check if user has access to this specific patient
        if hasattr(obj, 'patient') or obj.__class__.__name__ == 'Patient':
            patient = obj if obj.__class__.__name__ == 'Patient' else obj.patient
            return self._has_patient_access(request, patient)
        
        # For other objects, check standard permissions
        return self._check_object_permissions(request, obj)
    
    def _has_patient_access(self, request, patient):
        """Check if user has access to specific patient data"""
        user = request.user
        
        # Check if user has global patient access permission
        if user.has_perm('patients.view_all_patients'):
            return True
        
        # Check if user created or updated this patient
        if hasattr(patient, 'created_by') and patient.created_by == user:
            return True
        
        if hasattr(patient, 'updated_by') and patient.updated_by == user:
            return True
        
        # Check for active data access request
        if self._has_active_data_access_request(request, patient):
            return True
        
        # Log unauthorized access attempt
        self._log_security_event(
            request, 'PERMISSION_DENIED',
            f"User {user.username} attempted unauthorized access to patient {patient.patient_id}",
            severity='HIGH'
        )
        
        return False
    
    def _has_active_data_access_request(self, request, patient):
        """Check if user has active data access request for patient"""
        from datetime import datetime
        
        active_request = DataAccessRequest.objects.filter(
            requester=request.user,
            patient=patient,
            status='APPROVED',
            expires_at__gt=datetime.now(),
            access_revoked_at__isnull=True
        ).exists()
        
        return active_request
    
    def _check_object_permissions(self, request, obj):
        """Check standard object permissions"""
        # Implement role-based access control
        user = request.user
        
        # Admin users have full access
        if user.is_superuser:
            return True
        
        # Check specific permissions based on object type
        if hasattr(obj, 'created_by') and obj.created_by == user:
            return True
        
        if hasattr(obj, 'user') and obj.user == user:
            return True
        
        return False
    
    def _is_session_expired(self, request):
        """Check if user session has expired"""
        from django.conf import settings
        from datetime import timedelta
        
        session_timeout = getattr(settings, 'HIPAA_SETTINGS', {}).get('SESSION_TIMEOUT_MINUTES', 30)
        session_timeout_delta = timedelta(minutes=session_timeout)
        
        if 'last_activity' in request.session:
            from django.utils import timezone
            last_activity = request.session['last_activity']
            if timezone.now() - last_activity > session_timeout_delta:
                return True
        
        return False
    
    def _detect_suspicious_activity(self, request):
        """Detect suspicious activity patterns"""
        from datetime import timedelta
        from django.utils import timezone
        
        user = request.user
        now = timezone.now()
        one_hour_ago = now - timedelta(hours=1)
        
        # Check for multiple failed login attempts
        failed_logins = SecurityEvent.objects.filter(
            user=user,
            event_type='LOGIN_FAILED',
            timestamp__gte=one_hour_ago
        ).count()
        
        if failed_logins >= 5:
            return True
        
        # Check for unusual access patterns
        # This is a simplified example - in production, use more sophisticated algorithms
        recent_access = SecurityEvent.objects.filter(
            user=user,
            event_type='DATA_ACCESS',
            timestamp__gte=one_hour_ago
        ).count()
        
        if recent_access > 100:  # More than 100 data accesses in an hour
            return True
        
        return False
    
    def _log_security_event(self, request, event_type, description, severity='MEDIUM'):
        """Log security events"""
        SecurityEvent.objects.create(
            event_type=event_type,
            severity=severity,
            user=request.user if request.user.is_authenticated else None,
            ip_address=self._get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            description=description
        )
    
    def _get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class PatientDataPermission(permissions.BasePermission):
    """
    Specific permissions for patient data access
    """
    
    def has_permission(self, request, view):
        """Check if user can access patient data"""
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Check if user has patient data access permission
        return (
            request.user.has_perm('patients.view_patient') or
            request.user.has_perm('patients.view_all_patients')
        )
    
    def has_object_permission(self, request, view, obj):
        """Check if user can access specific patient data"""
        if not self.has_permission(request, view):
            return False
        
        # Check if user has access to this specific patient
        if hasattr(obj, 'patient'):
            patient = obj.patient
        elif obj.__class__.__name__ == 'Patient':
            patient = obj
        else:
            return False
        
        # Check patient access permissions
        user = request.user
        
        # Global access
        if user.has_perm('patients.view_all_patients'):
            return True
        
        # Creator/updater access
        if hasattr(patient, 'created_by') and patient.created_by == user:
            return True
        
        if hasattr(patient, 'updated_by') and patient.updated_by == user:
            return True
        
        return False


class AuditPermission(permissions.BasePermission):
    """
    Permissions for audit log access
    """
    
    def has_permission(self, request, view):
        """Check if user can access audit logs"""
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Only admin users and audit staff can access audit logs
        return (
            request.user.is_superuser or
            request.user.has_perm('audit.view_audit_log') or
            request.user.groups.filter(name='Audit Staff').exists()
        )