"""
Admin configuration for patients application.
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import Patient, PatientIdentifier, PatientNote, PatientConsent


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    """
    Admin interface for Patient model with encrypted field handling.
    """
    list_display = [
        'medical_record_number', 'get_display_name', 'get_age_display',
        'gender', 'primary_physician', 'is_active'
    ]
    list_filter = ['gender', 'ethnicity', 'race', 'marital_status', 'is_active', 'primary_physician']
    search_fields = ['medical_record_number', 'first_name_encrypted', 'last_name_encrypted']
    readonly_fields = ['created_at', 'updated_at', 'version', 'get_age_display']
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'medical_record_number', 'get_display_name', 'get_age_display',
                'gender', 'ethnicity', 'race', 'marital_status'
            )
        }),
        ('Contact Information', {
            'fields': ('primary_address', 'preferred_language', 'religion')
        }),
        ('Medical Information', {
            'fields': ('primary_physician', 'photo')
        }),
        ('System Information', {
            'fields': ('user_account', 'is_active', 'created_at', 'updated_at', 'version'),
            'classes': ('collapse',)
        }),
    )
    
    def get_display_name(self, obj):
        """Display patient name (not encrypted data in admin)."""
        return f"{obj.first_name} {obj.last_name}"
    get_display_name.short_description = 'Name'
    
    def get_age_display(self, obj):
        """Display patient age."""
        age = obj.get_age()
        return f"{age} years old" if age is not None else "Unknown"
    get_age_display.short_description = 'Age'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'primary_physician', 'primary_address'
        )


class PatientIdentifierInline(admin.TabularInline):
    """
    Inline admin for patient identifiers.
    """
    model = PatientIdentifier
    extra = 0
    readonly_fields = ['created_at', 'updated_at']


class PatientNoteInline(admin.TabularInline):
    """
    Inline admin for patient notes.
    """
    model = PatientNote
    extra = 0
    readonly_fields = ['created_at', 'updated_at']
    fields = ['note_type', 'title', 'is_alert', 'alert_expiry']


class PatientConsentInline(admin.TabularInline):
    """
    Inline admin for patient consents.
    """
    model = PatientConsent
    extra = 0
    readonly_fields = ['created_at', 'updated_at']


@admin.register(PatientNote)
class PatientNoteAdmin(admin.ModelAdmin):
    """
    Admin interface for patient notes.
    """
    list_display = ['patient', 'note_type', 'title', 'is_alert', 'created_at']
    list_filter = ['note_type', 'is_alert', 'created_at']
    search_fields = ['patient__medical_record_number', 'title']
    readonly_fields = ['created_at', 'updated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('patient')


@admin.register(PatientConsent)
class PatientConsentAdmin(admin.ModelAdmin):
    """
    Admin interface for patient consents.
    """
    list_display = [
        'patient', 'consent_type', 'is_granted', 'consent_date', 'expiry_date'
    ]
    list_filter = ['consent_type', 'is_granted', 'consent_date']
    search_fields = ['patient__medical_record_number']
    readonly_fields = ['created_at', 'updated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('patient')