"""
Clinical Data App Configuration
"""

from django.apps import AppConfig


class ClinicalDataConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.clinical_data'
    verbose_name = 'Clinical Data Management'