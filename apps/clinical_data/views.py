"""
Clinical Data Views - API endpoints for clinical data management
"""

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from django.utils import timezone
from .models import VitalSigns, LabResult, DiagnosticImaging, ClinicalNote, PreventiveCare
from .serializers import (
    VitalSignsSerializer, LabResultSerializer, DiagnosticImagingSerializer,
    ClinicalNoteSerializer, PreventiveCareSerializer
)
from apps.security.permissions import HIPAAPermission
from apps.audit.models import AuditLog


class VitalSignsViewSet(viewsets.ModelViewSet):
    """
    ViewSet for vital signs management
    """
    queryset = VitalSigns.objects.all()
    serializer_class = VitalSignsSerializer
    permission_classes = [IsAuthenticated, HIPAAPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['measurement_type', 'temperature_unit', 'weight_unit', 'height_unit']
    search_fields = ['patient__patient_id', 'patient__first_name', 'patient__last_name']
    ordering_fields = ['measurement_date', 'created_at']
    ordering = ['-measurement_date']
    
    def get_queryset(self):
        """Filter vital signs based on user permissions"""
        queryset = super().get_queryset()
        
        # Apply HIPAA access controls
        if not self.request.user.has_perm('clinical_data.view_all_vital_signs'):
            # Users can only see vital signs they have access to
            queryset = queryset.filter(
                Q(created_by=self.request.user) |
                Q(updated_by=self.request.user)
            )
        
        return queryset.select_related('patient', 'created_by', 'updated_by')
    
    def perform_create(self, serializer):
        """Create vital signs with audit logging"""
        vital_signs = serializer.save()
        
        # Log vital signs creation
        AuditLog.objects.create(
            user=self.request.user,
            action='CREATE_VITAL_SIGNS',
            resource_type='VitalSigns',
            resource_id=str(vital_signs.id),
            details={
                'patient_id': vital_signs.patient.patient_id,
                'measurement_type': vital_signs.measurement_type,
                'measurement_date': vital_signs.measurement_date.isoformat()
            },
            ip_address=self.get_client_ip()
        )
    
    def perform_update(self, serializer):
        """Update vital signs with audit logging"""
        old_data = self.get_object()
        vital_signs = serializer.save()
        
        # Log vital signs update
        AuditLog.objects.create(
            user=self.request.user,
            action='UPDATE_VITAL_SIGNS',
            resource_type='VitalSigns',
            resource_id=str(vital_signs.id),
            details={
                'patient_id': vital_signs.patient.patient_id,
                'changes': 'Vital signs updated'
            },
            ip_address=self.get_client_ip()
        )
    
    @action(detail=False, methods=['get'])
    def patient_vitals(self, request):
        """Get vital signs for specific patient"""
        patient_id = request.query_params.get('patient_id')
        if not patient_id:
            return Response({'error': 'patient_id parameter required'}, status=status.HTTP_400_BAD_REQUEST)
        
        vitals = self.get_queryset().filter(patient__patient_id=patient_id)
        serializer = self.get_serializer(vitals, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def abnormal_values(self, request):
        """Get vital signs with abnormal values"""
        # This would contain logic to identify abnormal vital signs
        # For now, return a placeholder
        return Response({'message': 'Abnormal values detection not implemented'})
    
    def get_client_ip(self):
        """Get client IP address"""
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip


class LabResultViewSet(viewsets.ModelViewSet):
    """
    ViewSet for lab results management
    """
    queryset = LabResult.objects.all()
    serializer_class = LabResultSerializer
    permission_classes = [IsAuthenticated, HIPAAPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['test_category', 'critical_level', 'status']
    search_fields = ['test_name', 'patient__patient_id']
    ordering_fields = ['result_date', 'ordered_date', 'created_at']
    ordering = ['-result_date']
    
    def get_queryset(self):
        """Filter lab results based on user permissions"""
        queryset = super().get_queryset()
        
        # Apply HIPAA access controls
        if not self.request.user.has_perm('clinical_data.view_all_lab_results'):
            # Users can only see lab results they have access to
            queryset = queryset.filter(
                Q(created_by=self.request.user) |
                Q(updated_by=self.request.user)
            )
        
        return queryset.select_related('patient', 'created_by', 'updated_by')
    
    def perform_create(self, serializer):
        """Create lab result with audit logging"""
        lab_result = serializer.save()
        
        # Log lab result creation
        AuditLog.objects.create(
            user=self.request.user,
            action='CREATE_LAB_RESULT',
            resource_type='LabResult',
            resource_id=str(lab_result.id),
            details={
                'patient_id': lab_result.patient.patient_id,
                'test_name': lab_result.test_name,
                'critical_level': lab_result.critical_level
            },
            ip_address=self.get_client_ip()
        )
    
    def perform_update(self, serializer):
        """Update lab result with audit logging"""
        old_data = self.get_object()
        lab_result = serializer.save()
        
        # Log lab result update
        AuditLog.objects.create(
            user=self.request.user,
            action='UPDATE_LAB_RESULT',
            resource_type='LabResult',
            resource_id=str(lab_result.id),
            details={
                'patient_id': lab_result.patient.patient_id,
                'changes': 'Lab result updated'
            },
            ip_address=self.get_client_ip()
        )
    
    @action(detail=False, methods=['get'])
    def critical_results(self, request):
        """Get critical lab results"""
        critical_results = self.get_queryset().filter(
            critical_level__in=['CRITICAL_HIGH', 'CRITICAL_LOW']
        )
        serializer = self.get_serializer(critical_results, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def pending_results(self, request):
        """Get pending lab results"""
        pending_results = self.get_queryset().filter(status='PENDING')
        serializer = self.get_serializer(pending_results, many=True)
        return Response(serializer.data)
    
    def get_client_ip(self):
        """Get client IP address"""
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip


class DiagnosticImagingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for diagnostic imaging management
    """
    queryset = DiagnosticImaging.objects.all()
    serializer_class = DiagnosticImagingSerializer
    permission_classes = [IsAuthenticated, HIPAAPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['imaging_type', 'body_part', 'image_quality']
    search_fields = ['study_description', 'patient__patient_id']
    ordering_fields = ['performed_date', 'ordered_date', 'created_at']
    ordering = ['-performed_date']
    
    def get_queryset(self):
        """Filter diagnostic imaging based on user permissions"""
        queryset = super().get_queryset()
        
        # Apply HIPAA access controls
        if not self.request.user.has_perm('clinical_data.view_all_diagnostic_imaging'):
            # Users can only see imaging they have access to
            queryset = queryset.filter(
                Q(created_by=self.request.user) |
                Q(updated_by=self.request.user)
            )
        
        return queryset.select_related('patient', 'created_by', 'updated_by')
    
    def perform_create(self, serializer):
        """Create diagnostic imaging with audit logging"""
        imaging = serializer.save()
        
        # Log diagnostic imaging creation
        AuditLog.objects.create(
            user=self.request.user,
            action='CREATE_DIAGNOSTIC_IMAGING',
            resource_type='DiagnosticImaging',
            resource_id=str(imaging.id),
            details={
                'patient_id': imaging.patient.patient_id,
                'imaging_type': imaging.imaging_type,
                'body_part': imaging.body_part
            },
            ip_address=self.get_client_ip()
        )
    
    def perform_update(self, serializer):
        """Update diagnostic imaging with audit logging"""
        old_data = self.get_object()
        imaging = serializer.save()
        
        # Log diagnostic imaging update
        AuditLog.objects.create(
            user=self.request.user,
            action='UPDATE_DIAGNOSTIC_IMAGING',
            resource_type='DiagnosticImaging',
            resource_id=str(imaging.id),
            details={
                'patient_id': imaging.patient.patient_id,
                'changes': 'Diagnostic imaging updated'
            },
            ip_address=self.get_client_ip()
        )
    
    @action(detail=False, methods=['get'])
    def follow_up_required(self, request):
        """Get imaging studies requiring follow-up"""
        follow_up_imaging = self.get_queryset().filter(follow_up_required=True)
        serializer = self.get_serializer(follow_up_imaging, many=True)
        return Response(serializer.data)
    
    def get_client_ip(self):
        """Get client IP address"""
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip


class ClinicalNoteViewSet(viewsets.ModelViewSet):
    """
    ViewSet for clinical notes management
    """
    queryset = ClinicalNote.objects.all()
    serializer_class = ClinicalNoteSerializer
    permission_classes = [IsAuthenticated, HIPAAPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['note_type', 'is_draft', 'is_final', 'requires_signature']
    search_fields = ['title', 'patient__patient_id']
    ordering_fields = ['note_date', 'created_at']
    ordering = ['-note_date']
    
    def get_queryset(self):
        """Filter clinical notes based on user permissions"""
        queryset = super().get_queryset()
        
        # Apply HIPAA access controls
        if not self.request.user.has_perm('clinical_data.view_all_clinical_notes'):
            # Users can only see notes they have access to
            queryset = queryset.filter(
                Q(created_by=self.request.user) |
                Q(updated_by=self.request.user)
            )
        
        return queryset.select_related('patient', 'created_by', 'updated_by')
    
    def perform_create(self, serializer):
        """Create clinical note with audit logging"""
        note = serializer.save()
        
        # Log clinical note creation
        AuditLog.objects.create(
            user=self.request.user,
            action='CREATE_CLINICAL_NOTE',
            resource_type='ClinicalNote',
            resource_id=str(note.id),
            details={
                'patient_id': note.patient.patient_id,
                'note_type': note.note_type,
                'title': note.title
            },
            ip_address=self.get_client_ip()
        )
    
    def perform_update(self, serializer):
        """Update clinical note with audit logging"""
        old_data = self.get_object()
        note = serializer.save()
        
        # Log clinical note update
        AuditLog.objects.create(
            user=self.request.user,
            action='UPDATE_CLINICAL_NOTE',
            resource_type='ClinicalNote',
            resource_id=str(note.id),
            details={
                'patient_id': note.patient.patient_id,
                'changes': 'Clinical note updated'
            },
            ip_address=self.get_client_ip()
        )
    
    @action(detail=True, methods=['post'])
    def sign(self, request, pk=None):
        """Sign a clinical note"""
        note = self.get_object()
        note.author_signature = request.data.get('signature', '')
        note.is_final = True
        note.is_draft = False
        note.save()
        
        serializer = self.get_serializer(note)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def unsigned_notes(self, request):
        """Get unsigned clinical notes"""
        unsigned_notes = self.get_queryset().filter(
            requires_signature=True,
            is_final=False
        )
        serializer = self.get_serializer(unsigned_notes, many=True)
        return Response(serializer.data)
    
    def get_client_ip(self):
        """Get client IP address"""
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip


class PreventiveCareViewSet(viewsets.ModelViewSet):
    """
    ViewSet for preventive care management
    """
    queryset = PreventiveCare.objects.all()
    serializer_class = PreventiveCareSerializer
    permission_classes = [IsAuthenticated, HIPAAPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['care_type', 'status', 'follow_up_required']
    search_fields = ['care_name', 'patient__patient_id']
    ordering_fields = ['due_date', 'completed_date', 'created_at']
    ordering = ['due_date']
    
    def get_queryset(self):
        """Filter preventive care based on user permissions"""
        queryset = super().get_queryset()
        
        # Apply HIPAA access controls
        if not self.request.user.has_perm('clinical_data.view_all_preventive_care'):
            # Users can only see preventive care they have access to
            queryset = queryset.filter(
                Q(created_by=self.request.user) |
                Q(updated_by=self.request.user)
            )
        
        return queryset.select_related('patient', 'created_by', 'updated_by')
    
    def perform_create(self, serializer):
        """Create preventive care with audit logging"""
        care = serializer.save()
        
        # Log preventive care creation
        AuditLog.objects.create(
            user=self.request.user,
            action='CREATE_PREVENTIVE_CARE',
            resource_type='PreventiveCare',
            resource_id=str(care.id),
            details={
                'patient_id': care.patient.patient_id,
                'care_type': care.care_type,
                'care_name': care.care_name
            },
            ip_address=self.get_client_ip()
        )
    
    def perform_update(self, serializer):
        """Update preventive care with audit logging"""
        old_data = self.get_object()
        care = serializer.save()
        
        # Log preventive care update
        AuditLog.objects.create(
            user=self.request.user,
            action='UPDATE_PREVENTIVE_CARE',
            resource_type='PreventiveCare',
            resource_id=str(care.id),
            details={
                'patient_id': care.patient.patient_id,
                'changes': 'Preventive care updated'
            },
            ip_address=self.get_client_ip()
        )
    
    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """Get overdue preventive care"""
        from datetime import date
        overdue_care = self.get_queryset().filter(
            due_date__lt=date.today(),
            status__in=['DUE', 'OVERDUE']
        )
        serializer = self.get_serializer(overdue_care, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def due_soon(self, request):
        """Get preventive care due soon (within 30 days)"""
        from datetime import date, timedelta
        thirty_days_from_now = date.today() + timedelta(days=30)
        due_soon = self.get_queryset().filter(
            due_date__lte=thirty_days_from_now,
            status='DUE'
        )
        serializer = self.get_serializer(due_soon, many=True)
        return Response(serializer.data)
    
    def get_client_ip(self):
        """Get client IP address"""
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip