"""
URL patterns for medical records application.
"""
from django.urls import path
from . import views

app_name = 'medical_records'

urlpatterns = [
    # Medical History
    path('<uuid:patient_id>/', views.MedicalHistoryDetailView.as_view(), name='medical_history'),
    path('<uuid:patient_id>/summary/', views.medical_history_summary, name='medical_history_summary'),
    
    # Past Medical History
    path('<uuid:patient_id>/past-history/', views.PastMedicalHistoryListCreateView.as_view(), name='past_history_list'),
    path('<uuid:patient_id>/past-history/<uuid:pk>/', views.PastMedicalHistoryDetailView.as_view(), name='past_history_detail'),
    
    # Family History
    path('<uuid:patient_id>/family-history/', views.FamilyHistoryListCreateView.as_view(), name='family_history_list'),
    
    # Social History
    path('<uuid:patient_id>/social-history/', views.SocialHistoryDetailView.as_view(), name='social_history'),
    
    # Medications
    path('<uuid:patient_id>/medications/', views.MedicationListCreateView.as_view(), name='medication_list'),
    path('<uuid:patient_id>/medications/<uuid:pk>/', views.MedicationDetailView.as_view(), name='medication_detail'),
    
    # Allergies
    path('<uuid:patient_id>/allergies/', views.AllergyListCreateView.as_view(), name='allergy_list'),
    path('<uuid:patient_id>/allergies/<uuid:pk>/', views.AllergyDetailView.as_view(), name='allergy_detail'),
]