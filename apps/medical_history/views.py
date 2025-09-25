"""
Medical History Views - API endpoints for medical history management
"""

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from django.utils import timezone
from .models import MedicalHistory, Medication, Allergy, Immunization, SocialHistory
from .serializers import (
    MedicalHistorySerializer, MedicationSerializer, AllergySerializer,
    ImmunizationSerializer, SocialHistorySerializer
)
from apps.security.permissions import HIPAAPermission
from apps.audit.models import AuditLog


class MedicalHistoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for medical history management
    """
    queryset = MedicalHistory.objects.all()
    serializer_class = MedicalHistorySerializer
    permission_classes = [IsAuthenticated, HIPAAPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['visit_type', 'is_active', 'data_source']
    search_fields = ['chief_complaint', 'patient__patient_id', 'patient__first_name', 'patient__last_name']
    ordering_fields = ['visit_date', 'created_at']
    ordering = ['-visit_date']
    
    def get_queryset(self):
        """Filter medical histories based on user permissions"""
        queryset = super().get_queryset()
        
        # Apply HIPAA access controls
        if not self.request.user.has_perm('medical_history.view_all_medical_histories'):
            # Users can only see medical histories they have access to
            queryset = queryset.filter(
                Q(created_by=self.request.user) |
                Q(updated_by=self.request.user)
            )
        
        return queryset.select_related('patient', 'created_by', 'updated_by')
    
    def perform_create(self, serializer):
        """Create medical history with audit logging"""
        medical_history = serializer.save()
        
        # Log medical history creation
        AuditLog.objects.create(
            user=self.request.user,
            action='CREATE_MEDICAL_HISTORY',
            resource_type='MedicalHistory',
            resource_id=str(medical_history.id),
            details={
                'patient_id': medical_history.patient.patient_id,
                'visit_type': medical_history.visit_type,
                'chief_complaint': medical_history.chief_complaint[:100]
            },
            ip_address=self.get_client_ip()
        )
    
    def perform_update(self, serializer):
        """Update medical history with audit logging"""
        old_data = self.get_object()
        medical_history = serializer.save()
        
        # Log medical history update
        AuditLog.objects.create(
            user=self.request.user,
            action='UPDATE_MEDICAL_HISTORY',
            resource_type='MedicalHistory',
            resource_id=str(medical_history.id),
            details={
                'patient_id': medical_history.patient.patient_id,
                'changes': 'Medical history updated'
            },
            ip_address=self.get_client_ip()
        )
    
    def perform_destroy(self, instance):
        """Soft delete medical history with audit logging"""
        instance.is_active = False
        instance.save()
        
        # Log medical history deactivation
        AuditLog.objects.create(
            user=self.request.user,
            action='DEACTIVATE_MEDICAL_HISTORY',
            resource_type='MedicalHistory',
            resource_id=str(instance.id),
            details={'patient_id': instance.patient.patient_id},
            ip_address=self.get_client_ip()
        )
    
    @action(detail=True, methods=['get'])
    def medications(self, request, pk=None):
        """Get medications for this medical history"""
        medical_history = self.get_object()
        medications = Medication.objects.filter(medical_history=medical_history)
        serializer = MedicationSerializer(medications, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def allergies(self, request, pk=None):
        """Get allergies for this medical history"""
        medical_history = self.get_object()
        allergies = Allergy.objects.filter(medical_history=medical_history)
        serializer = AllergySerializer(allergies, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def immunizations(self, request, pk=None):
        """Get immunizations for this medical history"""
        medical_history = self.get_object()
        immunizations = Immunization.objects.filter(medical_history=medical_history)
        serializer = ImmunizationSerializer(immunizations, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def social_history(self, request, pk=None):
        """Get social history for this medical history"""
        medical_history = self.get_object()
        social_histories = SocialHistory.objects.filter(medical_history=medical_history)
        serializer = SocialHistorySerializer(social_histories, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_medication(self, request, pk=None):
        """Add medication to medical history"""
        medical_history = self.get_object()
        serializer = MedicationSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            medication = serializer.save(medical_history=medical_history)
            
            # Log medication addition
            AuditLog.objects.create(
                user=request.user,
                action='ADD_MEDICATION',
                resource_type='MedicalHistory',
                resource_id=str(medical_history.id),
                details={
                    'patient_id': medical_history.patient.patient_id,
                    'medication_name': medication.name
                },
                ip_address=self.get_client_ip()
            )
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def add_allergy(self, request, pk=None):
        """Add allergy to medical history"""
        medical_history = self.get_object()
        serializer = AllergySerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            allergy = serializer.save(medical_history=medical_history)
            
            # Log allergy addition
            AuditLog.objects.create(
                user=request.user,
                action='ADD_ALLERGY',
                resource_type='MedicalHistory',
                resource_id=str(medical_history.id),
                details={
                    'patient_id': medical_history.patient.patient_id,
                    'allergen': allergy.allergen
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


class MedicationViewSet(viewsets.ModelViewSet):
    """ViewSet for medication management"""
    queryset = Medication.objects.all()
    serializer_class = MedicationSerializer
    permission_classes = [IsAuthenticated, HIPAAPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['medication_type', 'is_current', 'effectiveness']
    search_fields = ['name', 'generic_name', 'patient__patient_id']
    ordering_fields = ['created_at', 'start_date']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return super().get_queryset().select_related('patient', 'medical_history', 'created_by', 'updated_by')
    
    def perform_create(self, serializer):
        """Create medication with audit logging"""
        medication = serializer.save()
        
        # Log medication creation
        AuditLog.objects.create(
            user=self.request.user,
            action='CREATE_MEDICATION',
            resource_type='Medication',
            resource_id=str(medication.id),
            details={
                'patient_id': medication.patient.patient_id,
                'medication_name': medication.name
            },
            ip_address=self.get_client_ip()
        )
    
    def get_client_ip(self):
        """Get client IP address"""
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip


class AllergyViewSet(viewsets.ModelViewSet):
    """ViewSet for allergy management"""
    queryset = Allergy.objects.all()
    serializer_class = AllergySerializer
    permission_classes = [IsAuthenticated, HIPAAPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['allergy_type', 'severity', 'is_active']
    search_fields = ['allergen', 'patient__patient_id']
    ordering_fields = ['created_at', 'onset_date']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return super().get_queryset().select_related('patient', 'medical_history', 'created_by', 'updated_by')
    
    def perform_create(self, serializer):
        """Create allergy with audit logging"""
        allergy = serializer.save()
        
        # Log allergy creation
        AuditLog.objects.create(
            user=self.request.user,
            action='CREATE_ALLERGY',
            resource_type='Allergy',
            resource_id=str(allergy.id),
            details={
                'patient_id': allergy.patient.patient_id,
                'allergen': allergy.allergen,
                'severity': allergy.severity
            },
            ip_address=self.get_client_ip()
        )
    
    def get_client_ip(self):
        """Get client IP address"""
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip


class ImmunizationViewSet(viewsets.ModelViewSet):
    """ViewSet for immunization management"""
    queryset = Immunization.objects.all()
    serializer_class = ImmunizationSerializer
    permission_classes = [IsAuthenticated, HIPAAPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_complete']
    search_fields = ['vaccine_name', 'patient__patient_id']
    ordering_fields = ['administration_date', 'created_at']
    ordering = ['-administration_date']
    
    def get_queryset(self):
        return super().get_queryset().select_related('patient', 'medical_history', 'created_by', 'updated_by')
    
    def perform_create(self, serializer):
        """Create immunization with audit logging"""
        immunization = serializer.save()
        
        # Log immunization creation
        AuditLog.objects.create(
            user=self.request.user,
            action='CREATE_IMMUNIZATION',
            resource_type='Immunization',
            resource_id=str(immunization.id),
            details={
                'patient_id': immunization.patient.patient_id,
                'vaccine_name': immunization.vaccine_name,
                'administration_date': immunization.administration_date.isoformat()
            },
            ip_address=self.get_client_ip()
        )
    
    def get_client_ip(self):
        """Get client IP address"""
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip


class SocialHistoryViewSet(viewsets.ModelViewSet):
    """ViewSet for social history management"""
    queryset = SocialHistory.objects.all()
    serializer_class = SocialHistorySerializer
    permission_classes = [IsAuthenticated, HIPAAPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['smoking_status', 'alcohol_use', 'drug_use', 'sexual_activity']
    search_fields = ['patient__patient_id']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return super().get_queryset().select_related('patient', 'medical_history', 'created_by', 'updated_by')
    
    def perform_create(self, serializer):
        """Create social history with audit logging"""
        social_history = serializer.save()
        
        # Log social history creation
        AuditLog.objects.create(
            user=self.request.user,
            action='CREATE_SOCIAL_HISTORY',
            resource_type='SocialHistory',
            resource_id=str(social_history.id),
            details={
                'patient_id': social_history.patient.patient_id,
                'smoking_status': social_history.smoking_status,
                'alcohol_use': social_history.alcohol_use
            },
            ip_address=self.get_client_ip()
        )
    
    def get_client_ip(self):
        """Get client IP address"""
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip