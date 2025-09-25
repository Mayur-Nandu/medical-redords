"""
Security URLs
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SecurityEventViewSet, DataAccessRequestViewSet, 
    HIPAAComplianceLogViewSet, UserSessionViewSet
)

router = DefaultRouter()
router.register(r'security-events', SecurityEventViewSet)
router.register(r'data-access-requests', DataAccessRequestViewSet)
router.register(r'hipaa-compliance', HIPAAComplianceLogViewSet)
router.register(r'user-sessions', UserSessionViewSet)

urlpatterns = [
    path('', include(router.urls)),
]