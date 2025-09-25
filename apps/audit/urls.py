"""
Audit URLs
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AuditLogViewSet, DataAccessLogViewSet, ComplianceReportViewSet,
    DataRetentionPolicyViewSet, AuditTrailViewSet
)

router = DefaultRouter()
router.register(r'audit-logs', AuditLogViewSet)
router.register(r'data-access-logs', DataAccessLogViewSet)
router.register(r'compliance-reports', ComplianceReportViewSet)
router.register(r'retention-policies', DataRetentionPolicyViewSet)
router.register(r'audit-trails', AuditTrailViewSet)

urlpatterns = [
    path('', include(router.urls)),
]