"""
Views for patient management API endpoints.
"""
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Q
from django.core.exceptions import PermissionDenied
from accounts.models import AccessLog
from .models import Patient, PatientNote, PatientConsent
from .serializers import (
    PatientSerializer, PatientSummarySerializer, PatientSearchSerializer,
    PatientNoteSerializer, PatientConsentSerializer
)
import logging

logger = logging.getLogger(__name__)
security_logger = logging.getLogger('security')


class PatientPermissionMixin:
    """
    Mixin to check patient access permissions.
    """
    def check_patient_permission(self, patient, permission_type='view'):
        """
        Check if the current user has permission to access this patient.
        """
        user = self.request.user
        permissions = user.get_permissions_for_patient(patient)
        
        permission_key = f'can_{permission_type}'
        if not permissions.get(permission_key, False):
            # Log unauthorized access attempt
            AccessLog.objects.create(
                user=user,
                access_type='permission_denied',
                ip_address=self._get_client_ip(),
                user_agent=self.request.META.get('HTTP_USER_AGENT', ''),
                details={
                    'patient_id': str(patient.id),
                    'permission_type': permission_type,
                    'reason': f'insufficient_permissions_for_{permission_type}'
                }
            )
            
            security_logger.warning(
                f"Unauthorized patient access attempt: User {user.username} "
                f"tried to {permission_type} patient {patient.medical_record_number}"
            )
            
            raise PermissionDenied("You don't have permission to access this patient's data.")
    
    def _get_client_ip(self):
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip


class PatientListCreateView(PatientPermissionMixin, generics.ListCreateAPIView):
    """
    List patients (with search) and create new patients.
    """
    serializer_class = PatientSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Filter patients based on user permissions and search parameters.
        """
        user = self.request.user
        
        # Base queryset
        if user.role == 'patient':
            # Patients can only see their own profile
            if hasattr(user, 'patient_profile'):
                queryset = Patient.objects.filter(id=user.patient_profile.id)
            else:
                queryset = Patient.objects.none()
        elif user.can_access_patient_data:
            # Healthcare providers can see all patients
            queryset = Patient.objects.filter(is_active=True)
        else:
            queryset = Patient.objects.none()
        
        # Apply search filters
        search_serializer = PatientSearchSerializer(data=self.request.query_params)
        if search_serializer.is_valid():
            filters = search_serializer.validated_data
            
            if filters.get('query'):
                query = filters['query']
                queryset = queryset.filter(
                    Q(medical_record_number__icontains=query) |
                    Q(first_name_encrypted__icontains=query) |  # Note: This won't work with encryption
                    Q(last_name_encrypted__icontains=query)     # Better to implement search index
                )
            
            if filters.get('medical_record_number'):
                queryset = queryset.filter(
                    medical_record_number=filters['medical_record_number']
                )
            
            if filters.get('date_of_birth'):
                # This would need special handling for encrypted dates
                pass
            
            if filters.get('gender'):
                queryset = queryset.filter(gender=filters['gender'])
            
            if filters.get('primary_physician'):
                queryset = queryset.filter(primary_physician=filters['primary_physician'])
        
        return queryset.select_related('primary_physician', 'primary_address')
    
    def get_serializer_class(self):
        """
        Use summary serializer for list view, full serializer for detail/create.
        """
        if self.request.method == 'GET':
            return PatientSummarySerializer
        return PatientSerializer
    
    def perform_create(self, serializer):
        """
        Set created_by field and check permissions.
        """
        if not self.request.user.can_access_patient_data:
            raise PermissionDenied("You don't have permission to create patient records.")
        
        patient = serializer.save(created_by=self.request.user)
        
        # Log patient creation
        AccessLog.objects.create(
            user=self.request.user,
            access_type='data_modification',
            ip_address=self._get_client_ip(),
            user_agent=self.request.META.get('HTTP_USER_AGENT', ''),
            details={
                'action': 'patient_created',
                'patient_id': str(patient.id),
                'patient_mrn': patient.medical_record_number
            }
        )
        
        logger.info(f"Patient created: {patient.medical_record_number} by {self.request.user.username}")


class PatientDetailView(PatientPermissionMixin, generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or soft-delete a patient.
    """
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        """
        Get patient object and check permissions.
        """
        patient = super().get_object()
        
        # Check view permission for all operations
        self.check_patient_permission(patient, 'view')
        
        # Log data access
        AccessLog.objects.create(
            user=self.request.user,
            access_type='data_access',
            ip_address=self._get_client_ip(),
            user_agent=self.request.META.get('HTTP_USER_AGENT', ''),
            details={
                'action': 'patient_accessed',
                'patient_id': str(patient.id),
                'patient_mrn': patient.medical_record_number
            }
        )
        
        return patient
    
    def perform_update(self, serializer):
        """
        Check edit permissions before updating.
        """
        patient = self.get_object()
        self.check_patient_permission(patient, 'edit')
        
        serializer.save(updated_by=self.request.user)
        
        # Log modification
        AccessLog.objects.create(
            user=self.request.user,
            access_type='data_modification',
            ip_address=self._get_client_ip(),
            user_agent=self.request.META.get('HTTP_USER_AGENT', ''),
            details={
                'action': 'patient_updated',
                'patient_id': str(patient.id),
                'patient_mrn': patient.medical_record_number
            }
        )
        
        logger.info(f"Patient updated: {patient.medical_record_number} by {self.request.user.username}")
    
    def perform_destroy(self, instance):
        """
        Soft delete instead of hard delete for HIPAA compliance.
        """
        self.check_patient_permission(instance, 'delete')
        
        # Soft delete
        instance.is_active = False
        instance.updated_by = self.request.user
        instance.save()
        
        # Log deletion
        AccessLog.objects.create(
            user=self.request.user,
            access_type='data_modification',
            ip_address=self._get_client_ip(),
            user_agent=self.request.META.get('HTTP_USER_AGENT', ''),
            details={
                'action': 'patient_deleted',
                'patient_id': str(instance.id),
                'patient_mrn': instance.medical_record_number
            }
        )
        
        logger.info(f"Patient soft deleted: {instance.medical_record_number} by {self.request.user.username}")


class PatientNoteListCreateView(PatientPermissionMixin, generics.ListCreateAPIView):
    """
    List and create patient notes.
    """
    serializer_class = PatientNoteSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Get notes for the specified patient.
        """
        patient_id = self.kwargs['patient_id']
        try:
            patient = Patient.objects.get(id=patient_id)
            self.check_patient_permission(patient, 'view')
            return PatientNote.objects.filter(patient=patient, is_active=True)
        except Patient.DoesNotExist:
            return PatientNote.objects.none()
    
    def perform_create(self, serializer):
        """
        Create note for the specified patient.
        """
        patient_id = self.kwargs['patient_id']
        patient = Patient.objects.get(id=patient_id)
        self.check_patient_permission(patient, 'edit')
        
        serializer.save(
            patient=patient,
            created_by=self.request.user
        )


class PatientConsentListCreateView(PatientPermissionMixin, generics.ListCreateAPIView):
    """
    List and create patient consents.
    """
    serializer_class = PatientConsentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Get consents for the specified patient.
        """
        patient_id = self.kwargs['patient_id']
        try:
            patient = Patient.objects.get(id=patient_id)
            self.check_patient_permission(patient, 'view')
            return PatientConsent.objects.filter(patient=patient, is_active=True)
        except Patient.DoesNotExist:
            return PatientConsent.objects.none()
    
    def perform_create(self, serializer):
        """
        Create consent for the specified patient.
        """
        patient_id = self.kwargs['patient_id']
        patient = Patient.objects.get(id=patient_id)
        self.check_patient_permission(patient, 'edit')
        
        serializer.save(
            patient=patient,
            created_by=self.request.user
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def patient_search(request):
    """
    Advanced patient search endpoint.
    """
    if not request.user.can_access_patient_data:
        return Response(
            {'error': 'You do not have permission to search patients'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    search_serializer = PatientSearchSerializer(data=request.query_params)
    if not search_serializer.is_valid():
        return Response(
            search_serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Implement search logic here
    # Note: Searching encrypted fields requires special handling
    # Consider implementing a search index or using searchable encryption
    
    patients = Patient.objects.filter(is_active=True)[:20]  # Limit results
    serializer = PatientSummarySerializer(patients, many=True)
    
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def patient_alerts(request, patient_id):
    """
    Get active alerts for a patient.
    """
    try:
        patient = Patient.objects.get(id=patient_id)
        
        # Check permissions
        user = request.user
        permissions = user.get_permissions_for_patient(patient)
        if not permissions.get('can_view', False):
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get active alerts
        from django.utils import timezone
        alerts = PatientNote.objects.filter(
            patient=patient,
            is_alert=True,
            is_active=True
        ).filter(
            Q(alert_expiry__isnull=True) | Q(alert_expiry__gt=timezone.now())
        )
        
        serializer = PatientNoteSerializer(alerts, many=True)
        return Response(serializer.data)
        
    except Patient.DoesNotExist:
        return Response(
            {'error': 'Patient not found'},
            status=status.HTTP_404_NOT_FOUND
        )