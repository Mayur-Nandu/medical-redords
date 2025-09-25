"""
Audit Serializers
"""

from rest_framework import serializers
from .models import AuditLog, DataAccessLog, ComplianceReport, DataRetentionPolicy, AuditTrail


class AuditLogSerializer(serializers.ModelSerializer):
    """Audit log serializer"""
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = AuditLog
        fields = [
            'id', 'user', 'user_username', 'session_id', 'ip_address', 'user_agent',
            'action', 'resource_type', 'resource_id', 'resource_name', 'content_type',
            'object_id', 'old_values', 'new_values', 'changed_fields', 'description',
            'details', 'severity', 'timestamp', 'duration_ms', 'hipaa_relevant',
            'phi_accessed', 'business_justification', 'retention_until', 'archived',
            'archived_at'
        ]
        read_only_fields = ['id', 'timestamp', 'archived_at']


class DataAccessLogSerializer(serializers.ModelSerializer):
    """Data access log serializer"""
    user_username = serializers.CharField(source='user.username', read_only=True)
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    patient_id = serializers.CharField(source='patient.patient_id', read_only=True)
    
    class Meta:
        model = DataAccessLog
        fields = [
            'id', 'user', 'user_username', 'patient', 'patient_name', 'patient_id',
            'access_type', 'data_fields_accessed', 'purpose', 'business_justification',
            'ip_address', 'user_agent', 'session_id', 'request_id', 'access_start',
            'access_end', 'duration_seconds', 'consent_verified', 'minimum_necessary',
            'hipaa_compliant', 'risk_level', 'notes', 'follow_up_required', 'follow_up_date'
        ]
        read_only_fields = ['id', 'access_start']


class ComplianceReportSerializer(serializers.ModelSerializer):
    """Compliance report serializer"""
    generated_by_username = serializers.CharField(source='generated_by.username', read_only=True)
    reviewed_by_username = serializers.CharField(source='reviewed_by.username', read_only=True)
    approved_by_username = serializers.CharField(source='approved_by.username', read_only=True)
    
    class Meta:
        model = ComplianceReport
        fields = [
            'id', 'report_type', 'title', 'description', 'status', 'start_date',
            'end_date', 'generated_at', 'generated_by', 'generated_by_username',
            'findings', 'recommendations', 'compliance_score', 'risk_assessment',
            'reviewed_by', 'reviewed_by_username', 'reviewed_at', 'review_notes',
            'approved_by', 'approved_by_username', 'approved_at', 'approval_notes',
            'follow_up_required', 'follow_up_date', 'follow_up_actions'
        ]
        read_only_fields = ['id', 'generated_at', 'generated_by']


class DataRetentionPolicySerializer(serializers.ModelSerializer):
    """Data retention policy serializer"""
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    updated_by_username = serializers.CharField(source='updated_by.username', read_only=True)
    
    class Meta:
        model = DataRetentionPolicy
        fields = [
            'id', 'data_type', 'retention_period_years', 'retention_period_days',
            'auto_delete', 'legal_basis', 'regulatory_requirements', 'exceptions',
            'is_active', 'created_at', 'created_by', 'created_by_username',
            'updated_at', 'updated_by', 'updated_by_username', 'last_cleanup',
            'records_cleaned', 'next_cleanup'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by', 'updated_by']


class AuditTrailSerializer(serializers.ModelSerializer):
    """Audit trail serializer"""
    user_username = serializers.CharField(source='user.username', read_only=True)
    content_type_name = serializers.CharField(source='content_type.model', read_only=True)
    
    class Meta:
        model = AuditTrail
        fields = [
            'id', 'content_type', 'content_type_name', 'object_id', 'field_name',
            'old_value', 'new_value', 'change_type', 'user', 'user_username',
            'timestamp', 'ip_address', 'reason', 'notes'
        ]
        read_only_fields = ['id', 'timestamp']