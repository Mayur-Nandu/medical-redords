"""
Security Views - API endpoints for security management
"""

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from django.utils import timezone
from .models import (
    SecurityEvent, DataAccessRequest, HIPAAComplianceLog, 
    UserSession, EncryptionKey
)
from .serializers import (
    SecurityEventSerializer, DataAccessRequestSerializer,
    HIPAAComplianceLogSerializer, UserSessionSerializer,
    EncryptionKeySerializer
)
from .permissions import AuditPermission


class SecurityEventViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for security events (read-only for audit purposes)
    """
    queryset = SecurityEvent.objects.all()
    serializer_class = SecurityEventSerializer
    permission_classes = [IsAuthenticated, AuditPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['event_type', 'severity', 'user', 'resolved']
    search_fields = ['description', 'user__username', 'ip_address']
    ordering_fields = ['timestamp', 'severity']
    ordering = ['-timestamp']
    
    def get_queryset(self):
        return super().get_queryset().select_related('user', 'resolved_by')
    
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """Resolve a security event"""
        event = self.get_object()
        event.resolved = True
        event.resolved_by = request.user
        event.resolved_at = timezone.now()
        event.resolution_notes = request.data.get('resolution_notes', '')
        event.save()
        
        serializer = self.get_serializer(event)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get security events summary"""
        from django.db.models import Count
        from datetime import timedelta
        
        # Get events from last 30 days
        thirty_days_ago = timezone.now() - timedelta(days=30)
        events = self.get_queryset().filter(timestamp__gte=thirty_days_ago)
        
        summary = {
            'total_events': events.count(),
            'by_type': dict(events.values('event_type').annotate(count=Count('id')).values_list('event_type', 'count')),
            'by_severity': dict(events.values('severity').annotate(count=Count('id')).values_list('severity', 'count')),
            'unresolved': events.filter(resolved=False).count(),
        }
        
        return Response(summary)


class DataAccessRequestViewSet(viewsets.ModelViewSet):
    """
    ViewSet for data access requests
    """
    queryset = DataAccessRequest.objects.all()
    serializer_class = DataAccessRequestSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['request_type', 'status', 'requester']
    search_fields = ['patient__patient_id', 'patient__first_name', 'patient__last_name', 'purpose']
    ordering_fields = ['requested_at', 'approved_at']
    ordering = ['-requested_at']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Users can only see their own requests unless they have admin permissions
        if not self.request.user.has_perm('security.view_all_data_requests'):
            queryset = queryset.filter(requester=self.request.user)
        
        return queryset.select_related('requester', 'patient', 'approved_by')
    
    def perform_create(self, serializer):
        """Create data access request"""
        request = serializer.save(requester=self.request.user)
        
        # Log the request
        from .models import SecurityEvent
        SecurityEvent.objects.create(
            event_type='DATA_ACCESS',
            severity='MEDIUM',
            user=self.request.user,
            ip_address=self.get_client_ip(),
            user_agent=self.request.META.get('HTTP_USER_AGENT', ''),
            description=f"Data access request created for patient {request.patient.patient_id}",
            details={
                'request_type': request.request_type,
                'patient_id': request.patient.patient_id,
                'purpose': request.purpose
            }
        )
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve a data access request"""
        access_request = self.get_object()
        
        if not request.user.has_perm('security.approve_data_requests'):
            return Response(
                {'error': 'Permission denied'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        access_request.status = 'APPROVED'
        access_request.approved_by = request.user
        access_request.approved_at = timezone.now()
        access_request.access_granted_at = timezone.now()
        access_request.save()
        
        # Log the approval
        from .models import SecurityEvent
        SecurityEvent.objects.create(
            event_type='DATA_ACCESS',
            severity='MEDIUM',
            user=request.user,
            ip_address=self.get_client_ip(),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            description=f"Data access request approved for patient {access_request.patient.patient_id}",
            details={
                'request_id': str(access_request.id),
                'patient_id': access_request.patient.patient_id,
                'approved_by': request.user.username
            }
        )
        
        serializer = self.get_serializer(access_request)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def deny(self, request, pk=None):
        """Deny a data access request"""
        access_request = self.get_object()
        
        if not request.user.has_perm('security.approve_data_requests'):
            return Response(
                {'error': 'Permission denied'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        access_request.status = 'DENIED'
        access_request.approved_by = request.user
        access_request.approved_at = timezone.now()
        access_request.notes = request.data.get('notes', '')
        access_request.save()
        
        # Log the denial
        from .models import SecurityEvent
        SecurityEvent.objects.create(
            event_type='PERMISSION_DENIED',
            severity='MEDIUM',
            user=request.user,
            ip_address=self.get_client_ip(),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            description=f"Data access request denied for patient {access_request.patient.patient_id}",
            details={
                'request_id': str(access_request.id),
                'patient_id': access_request.patient.patient_id,
                'denied_by': request.user.username,
                'reason': request.data.get('notes', '')
            }
        )
        
        serializer = self.get_serializer(access_request)
        return Response(serializer.data)
    
    def get_client_ip(self):
        """Get client IP address"""
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip


class HIPAAComplianceLogViewSet(viewsets.ModelViewSet):
    """
    ViewSet for HIPAA compliance logs
    """
    queryset = HIPAAComplianceLog.objects.all()
    serializer_class = HIPAAComplianceLogSerializer
    permission_classes = [IsAuthenticated, AuditPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['activity_type', 'severity', 'reported_by', 'investigated_by']
    search_fields = ['description', 'reported_by__username', 'investigated_by__username']
    ordering_fields = ['reported_at', 'severity']
    ordering = ['-reported_at']
    
    def get_queryset(self):
        return super().get_queryset().select_related('reported_by', 'investigated_by')
    
    def perform_create(self, serializer):
        """Create HIPAA compliance log"""
        serializer.save(reported_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def investigate(self, request, pk=None):
        """Mark compliance log as under investigation"""
        compliance_log = self.get_object()
        compliance_log.investigated_by = request.user
        compliance_log.investigation_notes = request.data.get('investigation_notes', '')
        compliance_log.save()
        
        serializer = self.get_serializer(compliance_log)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """Resolve compliance log"""
        compliance_log = self.get_object()
        compliance_log.resolution = request.data.get('resolution', '')
        compliance_log.resolved_at = timezone.now()
        compliance_log.follow_up_required = request.data.get('follow_up_required', False)
        if compliance_log.follow_up_required:
            compliance_log.follow_up_date = request.data.get('follow_up_date')
        compliance_log.save()
        
        serializer = self.get_serializer(compliance_log)
        return Response(serializer.data)


class UserSessionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for user sessions (read-only for monitoring)
    """
    queryset = UserSession.objects.all()
    serializer_class = UserSessionSerializer
    permission_classes = [IsAuthenticated, AuditPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['user', 'is_active']
    search_fields = ['user__username', 'ip_address']
    ordering_fields = ['created_at', 'last_activity']
    ordering = ['-last_activity']
    
    def get_queryset(self):
        return super().get_queryset().select_related('user')
    
    @action(detail=True, methods=['post'])
    def terminate(self, request, pk=None):
        """Terminate a user session"""
        session = self.get_object()
        session.is_active = False
        session.logout_reason = request.data.get('reason', 'Admin terminated')
        session.save()
        
        # Log the session termination
        from .models import SecurityEvent
        SecurityEvent.objects.create(
            event_type='LOGOUT',
            severity='MEDIUM',
            user=request.user,
            ip_address=self.get_client_ip(),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            description=f"Session terminated for user {session.user.username}",
            details={
                'terminated_user': session.user.username,
                'session_key': session.session_key,
                'reason': session.logout_reason
            }
        )
        
        serializer = self.get_serializer(session)
        return Response(serializer.data)
    
    def get_client_ip(self):
        """Get client IP address"""
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip


class EncryptionKeyViewSet(viewsets.ModelViewSet):
    """
    ViewSet for encryption key management
    """
    queryset = EncryptionKey.objects.all()
    serializer_class = EncryptionKeySerializer
    permission_classes = [IsAuthenticated, AuditPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['key_name']
    ordering_fields = ['created_at', 'rotation_date']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return super().get_queryset().select_related('created_by')
    
    def perform_create(self, serializer):
        """Create encryption key"""
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def rotate(self, request, pk=None):
        """Rotate encryption key"""
        key = self.get_object()
        # In production, implement proper key rotation logic
        key.rotation_date = timezone.now()
        key.save()
        
        serializer = self.get_serializer(key)
        return Response(serializer.data)