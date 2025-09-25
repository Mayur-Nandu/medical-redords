"""
WSGI config for Medical History Recording Application.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medical_history.settings')

application = get_wsgi_application()