"""
Admin configuration for accounts application.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User, Organization, UserProfile, UserSession, AccessLog


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Admin interface for User model with healthcare-specific fields.
    """
    list_display = ['username', 'email', 'get_full_name', 'role', 'organization', 'is_verified', 'is_active']
    list_filter = ['role', 'specialty', 'is_verified', 'is_active', 'organization']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'license_number', 'npi_number']
    readonly_fields = ['date_joined', 'last_login', 'password_changed_at']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Healthcare Information', {
            'fields': ('role', 'specialty', 'license_number', 'npi_number', 'organization')
        }),
        ('Security', {
            'fields': ('is_verified', 'failed_login_attempts', 'account_locked_until', 'password_changed_at')
        }),
        ('Legal', {
            'fields': ('terms_accepted_at', 'privacy_policy_accepted_at')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('organization')


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    """
    Admin interface for Organization model.
    """
    list_display = ['name', 'organization_type', 'npi_number', 'is_active']
    list_filter = ['organization_type', 'is_active']
    search_fields = ['name', 'tax_id', 'npi_number']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """
    Admin interface for UserProfile model.
    """
    list_display = ['user', 'get_full_name', 'timezone', 'language_preference']
    search_fields = ['user__username', 'user__email', 'emergency_contact_name']
    readonly_fields = ['created_at', 'updated_at']
    
    def get_full_name(self, obj):
        return f"{obj.user.first_name} {obj.middle_name} {obj.user.last_name}".strip()
    get_full_name.short_description = 'Full Name'


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    """
    Admin interface for UserSession model.
    """
    list_display = ['user', 'ip_address', 'is_active', 'login_at', 'last_activity']
    list_filter = ['is_active', 'login_at']
    search_fields = ['user__username', 'ip_address']
    readonly_fields = ['created_at', 'updated_at', 'login_at', 'last_activity']
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


@admin.register(AccessLog)
class AccessLogAdmin(admin.ModelAdmin):
    """
    Admin interface for AccessLog model.
    """
    list_display = ['user', 'access_type', 'ip_address', 'created_at', 'get_details_summary']
    list_filter = ['access_type', 'created_at']
    search_fields = ['user__username', 'ip_address']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    
    def get_details_summary(self, obj):
        if obj.details:
            summary = str(obj.details)[:50]
            return format_html('<span title="{}">{}</span>', obj.details, summary)
        return '-'
    get_details_summary.short_description = 'Details'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False