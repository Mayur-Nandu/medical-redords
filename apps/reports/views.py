"""
Reports Views - API endpoints for reporting and analytics
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from apps.security.permissions import AuditPermission


class ReportViewSet(viewsets.ViewSet):
    """
    ViewSet for generating various reports
    """
    permission_classes = [IsAuthenticated, AuditPermission]
    
    @action(detail=False, methods=['get'])
    def patient_summary(self, request):
        """Generate patient summary report"""
        from apps.patients.models import Patient
        from apps.medical_history.models import MedicalHistory
        from apps.clinical_data.models import VitalSigns, LabResult
        
        patient_id = request.query_params.get('patient_id')
        if not patient_id:
            return Response({'error': 'patient_id parameter required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            patient = Patient.objects.get(patient_id=patient_id)
        except Patient.DoesNotExist:
            return Response({'error': 'Patient not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Get patient data
        medical_histories = MedicalHistory.objects.filter(patient=patient, is_active=True)
        vital_signs = VitalSigns.objects.filter(patient=patient).order_by('-measurement_date')[:10]
        lab_results = LabResult.objects.filter(patient=patient).order_by('-result_date')[:10]
        
        summary = {
            'patient': {
                'id': str(patient.id),
                'patient_id': patient.patient_id,
                'name': patient.full_name,
                'age': patient.age,
                'gender': patient.gender,
            },
            'medical_histories_count': medical_histories.count(),
            'recent_vital_signs': [
                {
                    'date': vs.measurement_date.isoformat(),
                    'systolic_bp': vs.systolic_bp,
                    'diastolic_bp': vs.diastolic_bp,
                    'heart_rate': vs.heart_rate,
                    'temperature': float(vs.temperature) if vs.temperature else None,
                } for vs in vital_signs
            ],
            'recent_lab_results': [
                {
                    'test_name': lr.test_name,
                    'result_value': lr.result_value,
                    'result_date': lr.result_date.isoformat() if lr.result_date else None,
                    'critical_level': lr.critical_level,
                } for lr in lab_results
            ],
        }
        
        return Response(summary)
    
    @action(detail=False, methods=['get'])
    def population_health(self, request):
        """Generate population health report"""
        from apps.patients.models import Patient
        from apps.medical_history.models import MedicalHistory
        from apps.clinical_data.models import VitalSigns
        
        # Get date range
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
        
        # Population statistics
        total_patients = Patient.objects.filter(is_active=True).count()
        new_patients = Patient.objects.filter(
            created_at__gte=start_date,
            created_at__lte=end_date
        ).count()
        
        # Medical history statistics
        medical_histories = MedicalHistory.objects.filter(
            visit_date__gte=start_date,
            visit_date__lte=end_date
        )
        
        # Vital signs statistics
        vital_signs = VitalSigns.objects.filter(
            measurement_date__gte=start_date,
            measurement_date__lte=end_date
        )
        
        # Calculate averages
        avg_systolic_bp = vital_signs.aggregate(
            avg=models.Avg('systolic_bp')
        )['avg'] or 0
        
        avg_diastolic_bp = vital_signs.aggregate(
            avg=models.Avg('diastolic_bp')
        )['avg'] or 0
        
        avg_heart_rate = vital_signs.aggregate(
            avg=models.Avg('heart_rate')
        )['avg'] or 0
        
        report = {
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            },
            'population': {
                'total_patients': total_patients,
                'new_patients': new_patients,
                'active_visits': medical_histories.count(),
            },
            'vital_signs_averages': {
                'systolic_bp': round(float(avg_systolic_bp), 1),
                'diastolic_bp': round(float(avg_diastolic_bp), 1),
                'heart_rate': round(float(avg_heart_rate), 1),
            },
            'visit_types': dict(
                medical_histories.values('visit_type')
                .annotate(count=Count('id'))
                .values_list('visit_type', 'count')
            ),
        }
        
        return Response(report)
    
    @action(detail=False, methods=['get'])
    def compliance_report(self, request):
        """Generate HIPAA compliance report"""
        from apps.audit.models import AuditLog, DataAccessLog
        from apps.security.models import SecurityEvent
        
        # Get date range
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
        
        # Audit logs
        audit_logs = AuditLog.objects.filter(
            timestamp__gte=start_date,
            timestamp__lte=end_date
        )
        
        # Data access logs
        data_access_logs = DataAccessLog.objects.filter(
            access_start__gte=start_date,
            access_start__lte=end_date
        )
        
        # Security events
        security_events = SecurityEvent.objects.filter(
            timestamp__gte=start_date,
            timestamp__lte=end_date
        )
        
        report = {
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            },
            'audit_activity': {
                'total_activities': audit_logs.count(),
                'hipaa_relevant': audit_logs.filter(hipaa_relevant=True).count(),
                'phi_accessed': audit_logs.filter(phi_accessed=True).count(),
            },
            'data_access': {
                'total_access_events': data_access_logs.count(),
                'unique_users': data_access_logs.values('user').distinct().count(),
                'unique_patients': data_access_logs.values('patient').distinct().count(),
                'high_risk_access': data_access_logs.filter(risk_level__in=['HIGH', 'CRITICAL']).count(),
            },
            'security_events': {
                'total_events': security_events.count(),
                'by_severity': dict(
                    security_events.values('severity')
                    .annotate(count=Count('id'))
                    .values_list('severity', 'count')
                ),
                'by_type': dict(
                    security_events.values('event_type')
                    .annotate(count=Count('id'))
                    .values_list('event_type', 'count')
                ),
            },
            'compliance_score': self._calculate_compliance_score(audit_logs, data_access_logs, security_events),
        }
        
        return Response(report)
    
    @action(detail=False, methods=['get'])
    def quality_metrics(self, request):
        """Generate quality metrics report"""
        from apps.patients.models import Patient
        from apps.medical_history.models import MedicalHistory
        from apps.clinical_data.models import VitalSigns, LabResult, PreventiveCare
        
        # Get date range
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
        
        # Data completeness metrics
        medical_histories = MedicalHistory.objects.filter(
            created_at__gte=start_date,
            created_at__lte=end_date
        )
        
        avg_completeness = medical_histories.aggregate(
            avg=models.Avg('completeness_score')
        )['avg'] or 0
        
        avg_reliability = medical_histories.aggregate(
            avg=models.Avg('reliability_score')
        )['avg'] or 0
        
        # Lab results metrics
        lab_results = LabResult.objects.filter(
            result_date__gte=start_date,
            result_date__lte=end_date
        )
        
        critical_results = lab_results.filter(
            critical_level__in=['CRITICAL_HIGH', 'CRITICAL_LOW']
        ).count()
        
        # Preventive care metrics
        preventive_care = PreventiveCare.objects.filter(
            due_date__gte=start_date,
            due_date__lte=end_date
        )
        
        completed_care = preventive_care.filter(status='COMPLETED').count()
        overdue_care = preventive_care.filter(status='OVERDUE').count()
        
        metrics = {
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            },
            'data_quality': {
                'avg_completeness_score': round(float(avg_completeness), 1),
                'avg_reliability_score': round(float(avg_reliability), 1),
                'total_medical_histories': medical_histories.count(),
            },
            'lab_results': {
                'total_results': lab_results.count(),
                'critical_results': critical_results,
                'critical_rate': round((critical_results / lab_results.count() * 100) if lab_results.count() > 0 else 0, 2),
            },
            'preventive_care': {
                'total_due': preventive_care.count(),
                'completed': completed_care,
                'overdue': overdue_care,
                'completion_rate': round((completed_care / preventive_care.count() * 100) if preventive_care.count() > 0 else 0, 2),
            },
        }
        
        return Response(metrics)
    
    def _calculate_compliance_score(self, audit_logs, data_access_logs, security_events):
        """Calculate overall compliance score"""
        # This is a simplified calculation
        # In production, this would be more sophisticated
        
        total_activities = audit_logs.count()
        if total_activities == 0:
            return 100
        
        # Calculate score based on various factors
        hipaa_compliant_ratio = audit_logs.filter(hipaa_relevant=True).count() / total_activities
        security_incidents = security_events.filter(severity__in=['HIGH', 'CRITICAL']).count()
        high_risk_access = data_access_logs.filter(risk_level__in=['HIGH', 'CRITICAL']).count()
        
        # Calculate score (simplified)
        base_score = 100
        penalty = (security_incidents * 10) + (high_risk_access * 5)
        score = max(0, base_score - penalty)
        
        return round(score, 1)