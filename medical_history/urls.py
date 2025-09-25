"""
Medical History Recording Application - URL Configuration
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from rest_framework import routers
from apps.patients.views import PatientViewSet
from apps.medical_history.views import MedicalHistoryViewSet
from apps.clinical_data.views import ClinicalDataViewSet
from apps.reports.views import ReportViewSet

# API Router
router = routers.DefaultRouter()
router.register(r'patients', PatientViewSet)
router.register(r'medical-history', MedicalHistoryViewSet)
router.register(r'clinical-data', ClinicalDataViewSet)
router.register(r'reports', ReportViewSet)

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # API
    path('api/v1/', include(router.urls)),
    path('api/v1/auth/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    path('api/v1/security/', include('apps.security.urls')),
    path('api/v1/audit/', include('apps.audit.urls')),
    path('api/v1/integrations/', include('apps.integrations.urls')),
    
    # Frontend
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
    path('dashboard/', TemplateView.as_view(template_name='dashboard.html'), name='dashboard'),
    path('patients/', TemplateView.as_view(template_name='patients.html'), name='patients'),
    path('medical-history/', TemplateView.as_view(template_name='medical_history.html'), name='medical_history'),
    path('reports/', TemplateView.as_view(template_name='reports.html'), name='reports'),
    path('patient-portal/', TemplateView.as_view(template_name='patient_portal.html'), name='patient_portal'),
    
    # Authentication
    path('accounts/', include('django.contrib.auth.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)