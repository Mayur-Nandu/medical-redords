"""
URL configuration for Medical History Recording Application.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Admin interface
    path('admin/', admin.site.urls),
    
    # Authentication
    path('accounts/', include('accounts.urls')),
    
    # API endpoints
    path('api/v1/patients/', include('patients.urls')),
    path('api/v1/medical-records/', include('medical_records.urls')),
    path('api/v1/clinical-data/', include('clinical_data.urls')),
    path('api/v1/audit/', include('audit_trail.urls')),
    
    # Core application routes
    path('', include('core.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)