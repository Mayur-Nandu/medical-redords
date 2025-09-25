"""
Security and audit middleware for HIPAA compliance.
"""
import logging
import json
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponse
from django.conf import settings

security_logger = logging.getLogger('security')
audit_logger = logging.getLogger('audit')


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Add security headers to all responses for HIPAA compliance.
    """
    
    def process_response(self, request, response):
        # Content Security Policy
        response['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:; "
            "font-src 'self'; "
            "connect-src 'self'"
        )
        
        # Additional security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
        
        # HIPAA-specific headers
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate, private'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        
        return response


class AuditMiddleware(MiddlewareMixin):
    """
    Comprehensive audit logging for HIPAA compliance.
    """
    
    def process_request(self, request):
        # Store request start time for performance tracking
        request._audit_start_time = time.time()
        
        # Log sensitive operations
        if self._is_sensitive_operation(request):
            audit_data = {
                'user': getattr(request.user, 'id', None) if hasattr(request, 'user') else None,
                'ip_address': self._get_client_ip(request),
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                'method': request.method,
                'path': request.path,
                'timestamp': time.time(),
                'session_key': request.session.session_key if hasattr(request, 'session') else None,
            }
            
            audit_logger.info(f"Request started: {json.dumps(audit_data)}")
    
    def process_response(self, request, response):
        # Log response for sensitive operations
        if self._is_sensitive_operation(request):
            duration = time.time() - getattr(request, '_audit_start_time', 0)
            
            audit_data = {
                'user': getattr(request.user, 'id', None) if hasattr(request, 'user') else None,
                'ip_address': self._get_client_ip(request),
                'method': request.method,
                'path': request.path,
                'status_code': response.status_code,
                'duration_ms': int(duration * 1000),
                'timestamp': time.time(),
            }
            
            audit_logger.info(f"Request completed: {json.dumps(audit_data)}")
        
        return response
    
    def _is_sensitive_operation(self, request):
        """
        Determine if the request involves sensitive medical data.
        """
        sensitive_paths = [
            '/api/v1/patients/',
            '/api/v1/medical-records/',
            '/api/v1/clinical-data/',
            '/admin/',
        ]
        
        return any(request.path.startswith(path) for path in sensitive_paths)
    
    def _get_client_ip(self, request):
        """
        Get the client IP address from request headers.
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


import time