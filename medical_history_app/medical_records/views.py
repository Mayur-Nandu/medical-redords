"""
Views for medical records API endpoints.
"""
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from patients.models import Patient
from patients.views import PatientPermissionMixin
from .models import (
    MedicalHistory, PastMedicalHistory, FamilyHistory, SocialHistory,
    Medication, Allergy, ReviewOfSystems
)
from .serializers import (
    MedicalHistorySerializer, PastMedicalHistorySerializer, FamilyHistorySerializer,
    SocialHistorySerializer, MedicationSerializer, AllergySerializer,
    ReviewOfSystemsSerializer
)
import logging

logger = logging.getLogger(__name__)


class MedicalHistoryDetailView(PatientPermissionMixin, generics.RetrieveUpdateAPIView):
    """
    Retrieve and update comprehensive medical history for a patient.
    """
    serializer_class = MedicalHistorySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        """Get or create medical history for the patient."""
        patient_id = self.kwargs['patient_id']
        patient = get_object_or_404(Patient, id=patient_id)
        
        # Check permissions
        self.check_patient_permission(patient, 'view')
        
        # Get or create medical history
        medical_history, created = MedicalHistory.objects.get_or_create(
            patient=patient,
            defaults={'created_by': self.request.user}
        )
        
        return medical_history
    
    def perform_update(self, serializer):
        """Update medical history with audit trail."""
        patient_id = self.kwargs['patient_id']
        patient = get_object_or_404(Patient, id=patient_id)
        self.check_patient_permission(patient, 'edit')
        
        serializer.save(
            last_updated_by=self.request.user,
            updated_by=self.request.user
        )


class PastMedicalHistoryListCreateView(PatientPermissionMixin, generics.ListCreateAPIView):
    """
    List and create past medical history entries.
    """
    serializer_class = PastMedicalHistorySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get past medical history for the patient."""
        patient_id = self.kwargs['patient_id']
        patient = get_object_or_404(Patient, id=patient_id)
        self.check_patient_permission(patient, 'view')
        
        return PastMedicalHistory.objects.filter(
            patient=patient,
            is_active=True
        ).order_by('-onset_date')
    
    def perform_create(self, serializer):
        """Create past medical history entry."""
        patient_id = self.kwargs['patient_id']
        patient = get_object_or_404(Patient, id=patient_id)
        self.check_patient_permission(patient, 'edit')
        
        serializer.save(
            patient=patient,
            created_by=self.request.user
        )


class PastMedicalHistoryDetailView(PatientPermissionMixin, generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete past medical history entry.
    """
    serializer_class = PastMedicalHistorySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        """Get past medical history entry with permission check."""
        patient_id = self.kwargs['patient_id']
        entry_id = self.kwargs['pk']
        
        entry = get_object_or_404(
            PastMedicalHistory,
            id=entry_id,
            patient_id=patient_id,
            is_active=True
        )
        
        self.check_patient_permission(entry.patient, 'view')
        return entry
    
    def perform_update(self, serializer):
        """Update with permission check."""
        self.check_patient_permission(self.get_object().patient, 'edit')
        serializer.save(updated_by=self.request.user)
    
    def perform_destroy(self, instance):
        """Soft delete with permission check."""
        self.check_patient_permission(instance.patient, 'delete')
        instance.is_active = False
        instance.updated_by = self.request.user
        instance.save()


class FamilyHistoryListCreateView(PatientPermissionMixin, generics.ListCreateAPIView):
    """
    List and create family history entries.
    """
    serializer_class = FamilyHistorySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get family history for the patient."""
        patient_id = self.kwargs['patient_id']
        patient = get_object_or_404(Patient, id=patient_id)
        self.check_patient_permission(patient, 'view')
        
        return FamilyHistory.objects.filter(
            patient=patient,
            is_active=True
        ).order_by('relationship')
    
    def perform_create(self, serializer):
        """Create family history entry."""
        patient_id = self.kwargs['patient_id']
        patient = get_object_or_404(Patient, id=patient_id)
        self.check_patient_permission(patient, 'edit')
        
        serializer.save(
            patient=patient,
            created_by=self.request.user
        )


class SocialHistoryDetailView(PatientPermissionMixin, generics.RetrieveUpdateAPIView):
    """
    Retrieve and update social history for a patient.
    """
    serializer_class = SocialHistorySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        """Get or create social history for the patient."""
        patient_id = self.kwargs['patient_id']
        patient = get_object_or_404(Patient, id=patient_id)
        
        # Check permissions
        self.check_patient_permission(patient, 'view')
        
        # Get or create social history
        social_history, created = SocialHistory.objects.get_or_create(
            patient=patient,
            defaults={'created_by': self.request.user}
        )
        
        return social_history
    
    def perform_update(self, serializer):
        """Update social history with audit trail."""
        patient_id = self.kwargs['patient_id']
        patient = get_object_or_404(Patient, id=patient_id)
        self.check_patient_permission(patient, 'edit')
        
        serializer.save(updated_by=self.request.user)


class MedicationListCreateView(PatientPermissionMixin, generics.ListCreateAPIView):
    """
    List and create medication entries.
    """
    serializer_class = MedicationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get medications for the patient."""
        patient_id = self.kwargs['patient_id']
        patient = get_object_or_404(Patient, id=patient_id)
        self.check_patient_permission(patient, 'view')
        
        # Filter by status if provided
        status_filter = self.request.query_params.get('status', 'active')
        
        queryset = Medication.objects.filter(
            patient=patient,
            is_active=True
        )
        
        if status_filter != 'all':
            queryset = queryset.filter(status=status_filter)
        
        return queryset.order_by('-start_date')
    
    def perform_create(self, serializer):
        """Create medication entry."""
        patient_id = self.kwargs['patient_id']
        patient = get_object_or_404(Patient, id=patient_id)
        self.check_patient_permission(patient, 'edit')
        
        serializer.save(
            patient=patient,
            created_by=self.request.user
        )


class MedicationDetailView(PatientPermissionMixin, generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete medication entry.
    """
    serializer_class = MedicationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        """Get medication entry with permission check."""
        patient_id = self.kwargs['patient_id']
        medication_id = self.kwargs['pk']
        
        medication = get_object_or_404(
            Medication,
            id=medication_id,
            patient_id=patient_id,
            is_active=True
        )
        
        self.check_patient_permission(medication.patient, 'view')
        return medication
    
    def perform_update(self, serializer):
        """Update with permission check."""
        self.check_patient_permission(self.get_object().patient, 'edit')
        serializer.save(updated_by=self.request.user)
    
    def perform_destroy(self, instance):
        """Soft delete with permission check."""
        self.check_patient_permission(instance.patient, 'delete')
        instance.is_active = False
        instance.updated_by = self.request.user
        instance.save()


class AllergyListCreateView(PatientPermissionMixin, generics.ListCreateAPIView):
    """
    List and create allergy entries.
    """
    serializer_class = AllergySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get allergies for the patient."""
        patient_id = self.kwargs['patient_id']
        patient = get_object_or_404(Patient, id=patient_id)
        self.check_patient_permission(patient, 'view')
        
        return Allergy.objects.filter(
            patient=patient,
            is_active=True
        ).order_by('-severity', 'allergy_type')
    
    def perform_create(self, serializer):
        """Create allergy entry."""
        patient_id = self.kwargs['patient_id']
        patient = get_object_or_404(Patient, id=patient_id)
        self.check_patient_permission(patient, 'edit')
        
        serializer.save(
            patient=patient,
            created_by=self.request.user
        )


class AllergyDetailView(PatientPermissionMixin, generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete allergy entry.
    """
    serializer_class = AllergySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        """Get allergy entry with permission check."""
        patient_id = self.kwargs['patient_id']
        allergy_id = self.kwargs['pk']
        
        allergy = get_object_or_404(
            Allergy,
            id=allergy_id,
            patient_id=patient_id,
            is_active=True
        )
        
        self.check_patient_permission(allergy.patient, 'view')
        return allergy
    
    def perform_update(self, serializer):
        """Update with permission check."""
        self.check_patient_permission(self.get_object().patient, 'edit')
        serializer.save(updated_by=self.request.user)
    
    def perform_destroy(self, instance):
        """Soft delete with permission check."""
        self.check_patient_permission(instance.patient, 'delete')
        instance.is_active = False
        instance.updated_by = self.request.user
        instance.save()


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def medical_history_summary(request, patient_id):
    """
    Get a summary of patient's medical history.
    """
    patient = get_object_or_404(Patient, id=patient_id)
    
    # Check permissions using the mixin pattern
    mixin = PatientPermissionMixin()
    mixin.request = request
    mixin.check_patient_permission(patient, 'view')
    
    try:
        medical_history = MedicalHistory.objects.get(patient=patient)
        
        # Get active entries only
        active_conditions = PastMedicalHistory.objects.filter(
            patient=patient,
            is_active=True,
            status__in=['active', 'chronic']
        ).count()
        
        active_medications = Medication.objects.filter(
            patient=patient,
            is_active=True,
            status='active'
        ).count()
        
        allergies = Allergy.objects.filter(
            patient=patient,
            is_active=True
        ).count()
        
        critical_allergies = Allergy.objects.filter(
            patient=patient,
            is_active=True,
            severity__in=['severe', 'life_threatening']
        ).count()
        
        summary = {
            'patient_id': str(patient.id),
            'patient_name': patient.get_full_name(),
            'medical_record_number': patient.medical_record_number,
            'last_updated': medical_history.updated_at,
            'summary': {
                'active_conditions': active_conditions,
                'active_medications': active_medications,
                'allergies': allergies,
                'critical_allergies': critical_allergies,
            }
        }
        
        return Response(summary)
        
    except MedicalHistory.DoesNotExist:
        return Response({
            'patient_id': str(patient.id),
            'patient_name': patient.get_full_name(),
            'medical_record_number': patient.medical_record_number,
            'message': 'No medical history found',
            'summary': {
                'active_conditions': 0,
                'active_medications': 0,
                'allergies': 0,
                'critical_allergies': 0,
            }
        })