"""
URL patterns for patients application.
"""
from django.urls import path
from . import views

app_name = 'patients'

urlpatterns = [
    # Patient CRUD operations
    path('', views.PatientListCreateView.as_view(), name='patient_list_create'),
    path('<uuid:pk>/', views.PatientDetailView.as_view(), name='patient_detail'),
    path('search/', views.patient_search, name='patient_search'),
    
    # Patient notes
    path('<uuid:patient_id>/notes/', views.PatientNoteListCreateView.as_view(), name='patient_notes'),
    
    # Patient consents
    path('<uuid:patient_id>/consents/', views.PatientConsentListCreateView.as_view(), name='patient_consents'),
    
    # Patient alerts
    path('<uuid:patient_id>/alerts/', views.patient_alerts, name='patient_alerts'),
]