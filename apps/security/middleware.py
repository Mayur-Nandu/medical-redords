"""
Security middleware for HIPAA compliance
"""

from django.utils.deprecation import MiddlewareMixin
from django.utils import timezone
from django.contrib.auth.models import User
from .models import SecurityEvent, UserSession
from .permissions import HIPAAPermission
import logging

logger = logging.getLogger(__name__)


class AuditMiddleware(MiddlewareMixin):
    """
    Middleware to log all user activities for audit purposes
    """
    
    def process_request(self, request):
        """Log request details"""
        if request.user.is_authenticated:
            # Update last activity timestamp
            request.session['last_activity'] = timezone.now()
            
            # Log data access
            if self._is_data_access_request(request):
                self._log_data_access(request)
    
    def process_response(self, request, response):
        """Log response details"""
        if request.user.is_authenticated:
            # Log security events based on response
            if response.status_code == 403:
                self._log_security_event(
                    request, 'PERMISSION_DENIED',
                    f"Access denied to {request.path}",
                    severity='MEDIUM'
                )
            elif response.status_code == 500:
                self._log_security_event(
                    request, 'SYSTEM_ERROR',
                    f"System error on {request.path}",
                    severity='HIGH'
                )
        
        return response
    
    def _is_data_access_request(self, request):
        """Check if request is accessing patient data"""
        data_paths = ['/api/v1/patients/', '/api/v1/medical-history/', '/api/v1/clinical-data/']
        return any(request.path.startswith(path) for path in data_paths)
    
    def _log_data_access(self, request):
        """Log data access for audit purposes"""
        try:
            SecurityEvent.objects.create(
                event_type='DATA_ACCESS',
                severity='LOW',
                user=request.user,
                ip_address=self._get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                description=f"Data access to {request.path}",
                details={
                    'path': request.path,
                    'method': request.method,
                    'query_params': dict(request.GET),
                }
            )
        except Exception as e:
            logger.error(f"Failed to log data access: {str(e)}")
    
    def _log_security_event(self, request, event_type, description, severity='MEDIUM'):
        """Log security events"""
        try:
            SecurityEvent.objects.create(
                event_type=event_type,
                severity=severity,
                user=request.user if request.user.is_authenticated else None,
                ip_address=self._get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                description=description
            )
        except Exception as e:
            logger.error(f"Failed to log security event: {str(e)}")
    
    def _get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class HIPAAComplianceMiddleware(MiddlewareMixin):
    """
    Middleware to enforce HIPAA compliance requirements
    """
    
    def process_request(self, request):
        """Enforce HIPAA compliance on requests"""
        if request.user.is_authenticated:
            # Check session timeout
            if self._is_session_expired(request):
                self._force_logout(request)
                return
            
            # Update session activity
            self._update_session_activity(request)
            
            # Check for suspicious activity
            if self._detect_suspicious_activity(request):
                self._handle_suspicious_activity(request)
    
    def process_response(self, request, response):
        """Add HIPAA compliance headers"""
        # Add security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        # Add cache control for sensitive data
        if self._is_sensitive_data_request(request):
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
        
        return response
    
    def _is_session_expired(self, request):
        """Check if user session has expired"""
        from django.conf import settings
        from datetime import timedelta
        
        session_timeout = getattr(settings, 'HIPAA_SETTINGS', {}).get('SESSION_TIMEOUT_MINUTES', 30)
        session_timeout_delta = timedelta(minutes=session_timeout)
        
        if 'last_activity' in request.session:
            last_activity = request.session['last_activity']
            if timezone.now() - last_activity > session_timeout_delta:
                return True
        
        return False
    
    def _force_logout(self, request):
        """Force user logout due to session timeout"""
        from django.contrib.auth import logout
        logout(request)
        
        # Log the timeout
        SecurityEvent.objects.create(
            event_type='LOGOUT',
            severity='LOW',
            user=request.user if request.user.is_authenticated else None,
            ip_address=self._get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            description="Session timeout - forced logout"
        )
    
    def _update_session_activity(self, request):
        """Update user session activity"""
        try:
            session_key = request.session.session_key
            if session_key:
                UserSession.objects.update_or_create(
                    session_key=session_key,
                    defaults={
                        'user': request.user,
                        'ip_address': self._get_client_ip(request),
                        'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                        'last_activity': timezone.now(),
                        'is_active': True,
                    }
                )
        except Exception as e:
            logger.error(f"Failed to update session activity: {str(e)}")
    
    def _detect_suspicious_activity(self, request):
        """Detect suspicious activity patterns"""
        from datetime import timedelta
        
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
        recent_access = SecurityEvent.objects.filter(
            user=user,
            event_type='DATA_ACCESS',
            timestamp__gte=one_hour_ago
        ).count()
        
        if recent_access > 100:  # More than 100 data accesses in an hour
            return True
        
        return False
    
    def _handle_suspicious_activity(self, request):
        """Handle detected suspicious activity"""
        # Log the suspicious activity
        SecurityEvent.objects.create(
            event_type='SUSPICIOUS_ACTIVITY',
            severity='HIGH',
            user=request.user,
            ip_address=self._get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            description="Suspicious activity pattern detected"
        )
        
        # In production, you might want to:
        # - Lock the user account
        # - Send alerts to administrators
        # - Require additional authentication
    
    def _is_sensitive_data_request(self, request):
        """Check if request is for sensitive patient data"""
        sensitive_paths = [
            '/api/v1/patients/',
            '/api/v1/medical-history/',
            '/api/v1/clinical-data/',
            '/api/v1/audit/',
        ]
        return any(request.path.startswith(path) for path in sensitive_paths)
    
    def _get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip