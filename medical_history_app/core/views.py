"""
Core application views.
"""
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.db import connection
import logging

logger = logging.getLogger(__name__)


class DashboardView(LoginRequiredMixin, TemplateView):
    """
    Main dashboard view for healthcare providers.
    """
    template_name = 'core/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add dashboard statistics
        try:
            from patients.models import Patient
            from medical_records.models import MedicalHistory
            
            context.update({
                'total_patients': Patient.objects.filter(is_active=True).count(),
                'recent_records': MedicalHistory.objects.filter(
                    is_active=True
                ).order_by('-updated_at')[:5],
                'user_role': self.request.user.role if hasattr(self.request.user, 'role') else 'provider',
            })
        except Exception as e:
            logger.warning(f"Dashboard data loading error: {e}")
            context.update({
                'total_patients': 0,
                'recent_records': [],
                'user_role': 'provider',
            })
        
        return context


def health_check(request):
    """
    Health check endpoint for monitoring.
    """
    try:
        # Check database connectivity
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        
        return JsonResponse({
            'status': 'healthy',
            'database': 'connected',
            'version': '1.0.0'
        })
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JsonResponse({
            'status': 'unhealthy',
            'error': str(e)
        }, status=500)