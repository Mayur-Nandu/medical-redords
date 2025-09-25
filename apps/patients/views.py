"""
Patient Views - API endpoints for patient management
"""

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from django.utils import timezone
from .models import Patient, PatientPhoto, PatientConsent, PatientAccessLog, PatientRelationship
from .serializers import (
    PatientSerializer, PatientListSerializer, PatientPhotoSerializer,
    PatientConsentSerializer, PatientAccessLogSerializer, PatientRelationshipSerializer
)
from apps.security.permissions import HIPAAPermission
from apps.audit.models import AuditLog


class PatientViewSet(viewsets.ModelViewSet):
    """
    ViewSet for patient management with HIPAA compliance
    """
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated, HIPAAPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['gender', 'ethnicity', 'race', 'is_active']
    search_fields = ['patient_id', 'first_name', 'last_name', 'phone_primary', 'email']
    ordering_fields = ['created_at', 'last_name', 'first_name', 'patient_id']
    ordering = ['last_name', 'first_name']
    
    def get_serializer_class(self):
        """Use different serializers for list vs detail views"""
        if self.action == 'list':
            return PatientListSerializer
        return PatientSerializer
    
    def get_queryset(self):
        """Filter patients based on user permissions"""
        queryset = super().get_queryset()
        
        # Apply HIPAA access controls
        if not self.request.user.has_perm('patients.view_all_patients'):
            # Users can only see patients they have access to
            queryset = queryset.filter(
                Q(created_by=self.request.user) |
                Q(updated_by=self.request.user)
            )
        
        return queryset.select_related('created_by', 'updated_by')
    
    def perform_create(self, serializer):
        """Create patient with audit logging"""
        patient = serializer.save()
        
        # Log patient creation
        AuditLog.objects.create(
            user=self.request.user,
            action='CREATE_PATIENT',
            resource_type='Patient',
            resource_id=str(patient.id),
            details={'patient_id': patient.patient_id},
            ip_address=self.get_client_ip()
        )
    
    def perform_update(self, serializer):
        """Update patient with audit logging"""
        old_data = self.get_object()
        patient = serializer.save()
        
        # Log patient update
        AuditLog.objects.create(
            user=self.request.user,
            action='UPDATE_PATIENT',
            resource_type='Patient',
            resource_id=str(patient.id),
            details={'patient_id': patient.patient_id, 'changes': 'Patient record updated'},
            ip_address=self.get_client_ip()
        )
    
    def perform_destroy(self, instance):
        """Soft delete patient with audit logging"""
        instance.is_active = False
        instance.save()
        
        # Log patient deactivation
        AuditLog.objects.create(
            user=self.request.user,
            action='DEACTIVATE_PATIENT',
            resource_type='Patient',
            resource_id=str(instance.id),
            details={'patient_id': instance.patient_id},
            ip_address=self.get_client_ip()
        )
    
    @action(detail=True, methods=['post'])
    def add_photo(self, request, pk=None):
        """Add photo to patient"""
        patient = self.get_object()
        serializer = PatientPhotoSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            # Delete existing photo if any
            PatientPhoto.objects.filter(patient=patient).delete()
            photo = serializer.save(patient=patient)
            
            # Log photo addition
            AuditLog.objects.create(
                user=request.user,
                action='ADD_PATIENT_PHOTO',
                resource_type='Patient',
                resource_id=str(patient.id),
                details={'patient_id': patient.patient_id},
                ip_address=self.get_client_ip()
            )
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def access_logs(self, request, pk=None):
        """Get patient access logs"""
        patient = self.get_object()
        logs = PatientAccessLog.objects.filter(patient=patient).order_by('-timestamp')
        serializer = PatientAccessLogSerializer(logs, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def relationships(self, request, pk=None):
        """Get patient relationships"""
        patient = self.get_object()
        relationships = PatientRelationship.objects.filter(
            Q(patient=patient) | Q(related_patient=patient)
        ).select_related('patient', 'related_patient', 'created_by')
        serializer = PatientRelationshipSerializer(relationships, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def consents(self, request, pk=None):
        """Get patient consents"""
        patient = self.get_object()
        consents = PatientConsent.objects.filter(patient=patient).order_by('-consent_date')
        serializer = PatientConsentSerializer(consents, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_consent(self, request, pk=None):
        """Add patient consent"""
        patient = self.get_object()
        serializer = PatientConsentSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            consent = serializer.save(patient=patient)
            
            # Log consent addition
            AuditLog.objects.create(
                user=request.user,
                action='ADD_PATIENT_CONSENT',
                resource_type='Patient',
                resource_id=str(patient.id),
                details={
                    'patient_id': patient.patient_id,
                    'consent_type': consent.consent_type,
                    'consent_given': consent.consent_given
                },
                ip_address=self.get_client_ip()
            )
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get_client_ip(self):
        """Get client IP address"""
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip


class PatientPhotoViewSet(viewsets.ModelViewSet):
    """ViewSet for patient photos"""
    queryset = PatientPhoto.objects.all()
    serializer_class = PatientPhotoSerializer
    permission_classes = [IsAuthenticated, HIPAAPermission]
    
    def get_queryset(self):
        return super().get_queryset().select_related('patient', 'created_by')


class PatientConsentViewSet(viewsets.ModelViewSet):
    """ViewSet for patient consents"""
    queryset = PatientConsent.objects.all()
    serializer_class = PatientConsentSerializer
    permission_classes = [IsAuthenticated, HIPAAPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['consent_type', 'consent_given']
    search_fields = ['patient__patient_id', 'patient__first_name', 'patient__last_name']
    
    def get_queryset(self):
        return super().get_queryset().select_related('patient', 'created_by')


class PatientAccessLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for patient access logs (read-only)"""
    queryset = PatientAccessLog.objects.all()
    serializer_class = PatientAccessLogSerializer
    permission_classes = [IsAuthenticated, HIPAAPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['access_type', 'user', 'patient']
    search_fields = ['patient__patient_id', 'user__username', 'ip_address']
    ordering_fields = ['timestamp']
    ordering = ['-timestamp']
    
    def get_queryset(self):
        return super().get_queryset().select_related('patient', 'user')


class PatientRelationshipViewSet(viewsets.ModelViewSet):
    """ViewSet for patient relationships"""
    queryset = PatientRelationship.objects.all()
    serializer_class = PatientRelationshipSerializer
    permission_classes = [IsAuthenticated, HIPAAPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['relationship_type', 'is_primary']
    search_fields = ['patient__patient_id', 'related_patient__patient_id']
    
    def get_queryset(self):
        return super().get_queryset().select_related('patient', 'related_patient', 'created_by')