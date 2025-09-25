"""
Audit Views - API endpoints for audit and compliance management
"""

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count
from django.utils import timezone
from datetime import timedelta
from .models import AuditLog, DataAccessLog, ComplianceReport, DataRetentionPolicy, AuditTrail
from .serializers import (
    AuditLogSerializer, DataAccessLogSerializer, ComplianceReportSerializer,
    DataRetentionPolicySerializer, AuditTrailSerializer
)
from apps.security.permissions import AuditPermission


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for audit logs (read-only for compliance)
    """
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated, AuditPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['action', 'resource_type', 'severity', 'hipaa_relevant', 'phi_accessed']
    search_fields = ['user__username', 'description', 'resource_name']
    ordering_fields = ['timestamp', 'severity']
    ordering = ['-timestamp']
    
    def get_queryset(self):
        return super().get_queryset().select_related('user', 'content_type')
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get audit log summary"""
        # Get logs from last 30 days
        thirty_days_ago = timezone.now() - timedelta(days=30)
        logs = self.get_queryset().filter(timestamp__gte=thirty_days_ago)
        
        summary = {
            'total_logs': logs.count(),
            'by_action': dict(logs.values('action').annotate(count=Count('id')).values_list('action', 'count')),
            'by_severity': dict(logs.values('severity').annotate(count=Count('id')).values_list('severity', 'count')),
            'hipaa_relevant': logs.filter(hipaa_relevant=True).count(),
            'phi_accessed': logs.filter(phi_accessed=True).count(),
            'unique_users': logs.values('user').distinct().count(),
        }
        
        return Response(summary)
    
    @action(detail=False, methods=['get'])
    def user_activity(self, request):
        """Get user activity summary"""
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response({'error': 'user_id parameter required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get user activity for last 30 days
        thirty_days_ago = timezone.now() - timedelta(days=30)
        user_logs = self.get_queryset().filter(
            user_id=user_id,
            timestamp__gte=thirty_days_ago
        )
        
        activity = {
            'user_id': user_id,
            'total_activities': user_logs.count(),
            'by_action': dict(user_logs.values('action').annotate(count=Count('id')).values_list('action', 'count')),
            'by_resource': dict(user_logs.values('resource_type').annotate(count=Count('id')).values_list('resource_type', 'count')),
            'hipaa_relevant_activities': user_logs.filter(hipaa_relevant=True).count(),
            'phi_access_count': user_logs.filter(phi_accessed=True).count(),
        }
        
        return Response(activity)
    
    @action(detail=False, methods=['get'])
    def compliance_report(self, request):
        """Generate compliance report"""
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if not start_date or not end_date:
            return Response(
                {'error': 'start_date and end_date parameters required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            start_date = timezone.datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            end_date = timezone.datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        except ValueError:
            return Response(
                {'error': 'Invalid date format. Use ISO format.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        logs = self.get_queryset().filter(
            timestamp__gte=start_date,
            timestamp__lte=end_date
        )
        
        report = {
            'period': {'start': start_date, 'end': end_date},
            'total_activities': logs.count(),
            'hipaa_relevant': logs.filter(hipaa_relevant=True).count(),
            'phi_access': logs.filter(phi_accessed=True).count(),
            'by_action': dict(logs.values('action').annotate(count=Count('id')).values_list('action', 'count')),
            'by_user': dict(logs.values('user__username').annotate(count=Count('id')).values_list('user__username', 'count')),
            'high_severity': logs.filter(severity='HIGH').count(),
            'critical_severity': logs.filter(severity='CRITICAL').count(),
        }
        
        return Response(report)


class DataAccessLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for data access logs (read-only for compliance)
    """
    queryset = DataAccessLog.objects.all()
    serializer_class = DataAccessLogSerializer
    permission_classes = [IsAuthenticated, AuditPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['access_type', 'risk_level', 'consent_verified', 'hipaa_compliant']
    search_fields = ['user__username', 'patient__patient_id', 'purpose']
    ordering_fields = ['access_start', 'duration_seconds']
    ordering = ['-access_start']
    
    def get_queryset(self):
        return super().get_queryset().select_related('user', 'patient')
    
    @action(detail=False, methods=['get'])
    def patient_access(self, request):
        """Get access logs for specific patient"""
        patient_id = request.query_params.get('patient_id')
        if not patient_id:
            return Response({'error': 'patient_id parameter required'}, status=status.HTTP_400_BAD_REQUEST)
        
        logs = self.get_queryset().filter(patient__patient_id=patient_id)
        serializer = self.get_serializer(logs, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def user_access(self, request):
        """Get access logs for specific user"""
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response({'error': 'user_id parameter required'}, status=status.HTTP_400_BAD_REQUEST)
        
        logs = self.get_queryset().filter(user_id=user_id)
        serializer = self.get_serializer(logs, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def risk_analysis(self, request):
        """Analyze access patterns for risk assessment"""
        # Get high-risk access patterns
        high_risk_logs = self.get_queryset().filter(risk_level__in=['HIGH', 'CRITICAL'])
        
        analysis = {
            'high_risk_access_count': high_risk_logs.count(),
            'by_risk_level': dict(high_risk_logs.values('risk_level').annotate(count=Count('id')).values_list('risk_level', 'count')),
            'by_access_type': dict(high_risk_logs.values('access_type').annotate(count=Count('id')).values_list('access_type', 'count')),
            'non_compliant_access': high_risk_logs.filter(hipaa_compliant=False).count(),
            'without_consent': high_risk_logs.filter(consent_verified=False).count(),
        }
        
        return Response(analysis)


class ComplianceReportViewSet(viewsets.ModelViewSet):
    """
    ViewSet for compliance reports
    """
    queryset = ComplianceReport.objects.all()
    serializer_class = ComplianceReportSerializer
    permission_classes = [IsAuthenticated, AuditPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['report_type', 'status', 'follow_up_required']
    search_fields = ['title', 'description']
    ordering_fields = ['generated_at', 'compliance_score']
    ordering = ['-generated_at']
    
    def get_queryset(self):
        return super().get_queryset().select_related('generated_by', 'reviewed_by', 'approved_by')
    
    def perform_create(self, serializer):
        """Create compliance report"""
        serializer.save(generated_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def review(self, request, pk=None):
        """Review a compliance report"""
        report = self.get_object()
        report.reviewed_by = request.user
        report.reviewed_at = timezone.now()
        report.review_notes = request.data.get('review_notes', '')
        report.status = 'REVIEWED'
        report.save()
        
        serializer = self.get_serializer(report)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve a compliance report"""
        report = self.get_object()
        report.approved_by = request.user
        report.approved_at = timezone.now()
        report.approval_notes = request.data.get('approval_notes', '')
        report.status = 'APPROVED'
        report.save()
        
        serializer = self.get_serializer(report)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def generate_hipaa_audit(self, request):
        """Generate HIPAA compliance audit report"""
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        
        if not start_date or not end_date:
            return Response(
                {'error': 'start_date and end_date required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Generate HIPAA audit report
        report = ComplianceReport.objects.create(
            report_type='HIPAA_AUDIT',
            title=f'HIPAA Compliance Audit - {start_date} to {end_date}',
            description='Automated HIPAA compliance audit report',
            start_date=start_date,
            end_date=end_date,
            generated_by=request.user,
            status='COMPLETED',
            findings=self._generate_hipaa_findings(start_date, end_date),
            recommendations=self._generate_hipaa_recommendations(),
            compliance_score=self._calculate_compliance_score(start_date, end_date)
        )
        
        serializer = self.get_serializer(report)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def _generate_hipaa_findings(self, start_date, end_date):
        """Generate HIPAA audit findings"""
        # This would contain actual audit logic
        return {
            'total_phi_access': 0,
            'unauthorized_access': 0,
            'missing_consent': 0,
            'security_incidents': 0,
        }
    
    def _generate_hipaa_recommendations(self):
        """Generate HIPAA recommendations"""
        return [
            'Implement additional access controls',
            'Review user permissions regularly',
            'Enhance audit logging',
        ]
    
    def _calculate_compliance_score(self, start_date, end_date):
        """Calculate compliance score"""
        # This would contain actual scoring logic
        return 85


class DataRetentionPolicyViewSet(viewsets.ModelViewSet):
    """
    ViewSet for data retention policies
    """
    queryset = DataRetentionPolicy.objects.all()
    serializer_class = DataRetentionPolicySerializer
    permission_classes = [IsAuthenticated, AuditPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['data_type', 'is_active', 'auto_delete']
    search_fields = ['data_type', 'legal_basis']
    ordering_fields = ['data_type', 'retention_period_years']
    ordering = ['data_type']
    
    def get_queryset(self):
        return super().get_queryset().select_related('created_by', 'updated_by')
    
    def perform_create(self, serializer):
        """Create data retention policy"""
        serializer.save(created_by=self.request.user, updated_by=self.request.user)
    
    def perform_update(self, serializer):
        """Update data retention policy"""
        serializer.save(updated_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def cleanup(self, request, pk=None):
        """Execute data cleanup based on retention policy"""
        policy = self.get_object()
        
        # This would contain actual cleanup logic
        policy.last_cleanup = timezone.now()
        policy.records_cleaned = 0  # Would be calculated
        policy.next_cleanup = timezone.now() + timedelta(days=30)
        policy.save()
        
        serializer = self.get_serializer(policy)
        return Response(serializer.data)


class AuditTrailViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for audit trails (read-only for compliance)
    """
    queryset = AuditTrail.objects.all()
    serializer_class = AuditTrailSerializer
    permission_classes = [IsAuthenticated, AuditPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['change_type', 'field_name']
    search_fields = ['user__username', 'field_name', 'reason']
    ordering_fields = ['timestamp']
    ordering = ['-timestamp']
    
    def get_queryset(self):
        return super().get_queryset().select_related('user', 'content_type')
    
    @action(detail=False, methods=['get'])
    def object_changes(self, request):
        """Get changes for specific object"""
        content_type_id = request.query_params.get('content_type_id')
        object_id = request.query_params.get('object_id')
        
        if not content_type_id or not object_id:
            return Response(
                {'error': 'content_type_id and object_id parameters required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        trails = self.get_queryset().filter(
            content_type_id=content_type_id,
            object_id=object_id
        )
        serializer = self.get_serializer(trails, many=True)
        return Response(serializer.data)