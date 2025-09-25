"""
Patient Admin Interface
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import Patient, PatientPhoto, PatientConsent, PatientAccessLog, PatientRelationship


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['patient_id', 'full_name', 'date_of_birth', 'gender', 'is_active', 'created_at']
    list_filter = ['gender', 'ethnicity', 'race', 'is_active', 'created_at']
    search_fields = ['patient_id', 'first_name', 'last_name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Patient Information', {
            'fields': ('patient_id', 'first_name', 'last_name', 'middle_name', 'date_of_birth', 'gender')
        }),
        ('Demographics', {
            'fields': ('ethnicity', 'race', 'preferred_language', 'religion', 'marital_status')
        }),
        ('Contact Information', {
            'fields': ('address_line1', 'address_line2', 'city', 'state', 'postal_code', 'country', 
                      'phone_primary', 'phone_secondary', 'email')
        }),
        ('Emergency Contact', {
            'fields': ('emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relationship')
        }),
        ('Insurance', {
            'fields': ('insurance_primary', 'insurance_primary_id', 'insurance_secondary', 'insurance_secondary_id')
        }),
        ('System Information', {
            'fields': ('is_active', 'consent_given', 'consent_date', 'data_retention_until', 
                      'created_by', 'updated_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('created_by', 'updated_by')


@admin.register(PatientPhoto)
class PatientPhotoAdmin(admin.ModelAdmin):
    list_display = ['patient', 'created_at', 'created_by']
    readonly_fields = ['created_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('patient', 'created_by')


@admin.register(PatientConsent)
class PatientConsentAdmin(admin.ModelAdmin):
    list_display = ['patient', 'consent_type', 'consent_given', 'consent_date', 'created_by']
    list_filter = ['consent_type', 'consent_given', 'consent_date']
    search_fields = ['patient__patient_id', 'patient__first_name', 'patient__last_name']
    readonly_fields = ['consent_date']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('patient', 'created_by')


@admin.register(PatientAccessLog)
class PatientAccessLogAdmin(admin.ModelAdmin):
    list_display = ['patient', 'user', 'access_type', 'timestamp', 'ip_address']
    list_filter = ['access_type', 'timestamp']
    search_fields = ['patient__patient_id', 'user__username', 'ip_address']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('patient', 'user')


@admin.register(PatientRelationship)
class PatientRelationshipAdmin(admin.ModelAdmin):
    list_display = ['patient', 'related_patient', 'relationship_type', 'is_primary', 'created_at']
    list_filter = ['relationship_type', 'is_primary', 'created_at']
    search_fields = ['patient__patient_id', 'related_patient__patient_id']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('patient', 'related_patient', 'created_by')