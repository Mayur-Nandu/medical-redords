"""
Security Serializers
"""

from rest_framework import serializers
from .models import (
    SecurityEvent, DataAccessRequest, HIPAAComplianceLog,
    UserSession, EncryptionKey
)


class SecurityEventSerializer(serializers.ModelSerializer):
    """Security event serializer"""
    user_username = serializers.CharField(source='user.username', read_only=True)
    resolved_by_username = serializers.CharField(source='resolved_by.username', read_only=True)
    
    class Meta:
        model = SecurityEvent
        fields = [
            'id', 'event_type', 'severity', 'user', 'user_username', 'ip_address',
            'user_agent', 'description', 'details', 'timestamp', 'resolved',
            'resolved_by', 'resolved_by_username', 'resolved_at', 'resolution_notes'
        ]
        read_only_fields = ['id', 'timestamp', 'resolved_at']


class DataAccessRequestSerializer(serializers.ModelSerializer):
    """Data access request serializer"""
    requester_username = serializers.CharField(source='requester.username', read_only=True)
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    approved_by_username = serializers.CharField(source='approved_by.username', read_only=True)
    
    class Meta:
        model = DataAccessRequest
        fields = [
            'id', 'requester', 'requester_username', 'patient', 'patient_name',
            'request_type', 'purpose', 'data_requested', 'status', 'requested_at',
            'approved_by', 'approved_by_username', 'approved_at', 'expires_at',
            'access_granted_at', 'access_revoked_at', 'notes'
        ]
        read_only_fields = ['id', 'requested_at', 'approved_at', 'access_granted_at', 'access_revoked_at']


class HIPAAComplianceLogSerializer(serializers.ModelSerializer):
    """HIPAA compliance log serializer"""
    reported_by_username = serializers.CharField(source='reported_by.username', read_only=True)
    investigated_by_username = serializers.CharField(source='investigated_by.username', read_only=True)
    
    class Meta:
        model = HIPAAComplianceLog
        fields = [
            'id', 'activity_type', 'description', 'affected_patients', 'severity',
            'reported_by', 'reported_by_username', 'reported_at', 'investigated_by',
            'investigated_by_username', 'investigation_notes', 'resolution',
            'resolved_at', 'follow_up_required', 'follow_up_date'
        ]
        read_only_fields = ['id', 'reported_at', 'resolved_at']


class UserSessionSerializer(serializers.ModelSerializer):
    """User session serializer"""
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = UserSession
        fields = [
            'id', 'user', 'user_username', 'session_key', 'ip_address',
            'user_agent', 'created_at', 'last_activity', 'is_active',
            'logout_reason'
        ]
        read_only_fields = ['id', 'created_at', 'last_activity']


class EncryptionKeySerializer(serializers.ModelSerializer):
    """Encryption key serializer"""
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = EncryptionKey
        fields = [
            'id', 'key_name', 'key_value', 'created_at', 'created_by',
            'created_by_username', 'is_active', 'rotation_date'
        ]
        read_only_fields = ['id', 'created_at', 'created_by']