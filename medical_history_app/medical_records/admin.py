"""
Admin configuration for medical records application.
"""
from django.contrib import admin
from .models import (
    MedicalHistory, PastMedicalHistory, FamilyHistory, SocialHistory,
    Medication, Allergy, ReviewOfSystems
)


class PastMedicalHistoryInline(admin.TabularInline):
    """Inline admin for past medical history."""
    model = PastMedicalHistory
    extra = 0
    readonly_fields = ['created_at', 'updated_at']


class FamilyHistoryInline(admin.TabularInline):
    """Inline admin for family history."""
    model = FamilyHistory
    extra = 0
    readonly_fields = ['created_at', 'updated_at']


class MedicationInline(admin.TabularInline):
    """Inline admin for medications."""
    model = Medication
    extra = 0
    readonly_fields = ['created_at', 'updated_at']


class AllergyInline(admin.TabularInline):
    """Inline admin for allergies."""
    model = Allergy
    extra = 0
    readonly_fields = ['created_at', 'updated_at']


@admin.register(MedicalHistory)
class MedicalHistoryAdmin(admin.ModelAdmin):
    """Admin interface for MedicalHistory model."""
    list_display = ['patient', 'last_updated_by', 'updated_at']
    readonly_fields = ['created_at', 'updated_at', 'version']
    # Note: Inlines are commented out due to different FK relationships
    # inlines = [PastMedicalHistoryInline, FamilyHistoryInline, MedicationInline, AllergyInline]
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('patient', 'last_updated_by')


@admin.register(Medication)
class MedicationAdmin(admin.ModelAdmin):
    """Admin interface for Medication model."""
    list_display = ['patient', 'get_medication_name', 'status', 'start_date', 'end_date']
    list_filter = ['medication_type', 'status', 'frequency']
    readonly_fields = ['created_at', 'updated_at']
    
    def get_medication_name(self, obj):
        return obj.medication_name
    get_medication_name.short_description = 'Medication'


@admin.register(Allergy)
class AllergyAdmin(admin.ModelAdmin):
    """Admin interface for Allergy model."""
    list_display = ['patient', 'get_allergen', 'allergy_type', 'severity', 'verified']
    list_filter = ['allergy_type', 'severity', 'verified']
    readonly_fields = ['created_at', 'updated_at']
    
    def get_allergen(self, obj):
        return obj.allergen
    get_allergen.short_description = 'Allergen'