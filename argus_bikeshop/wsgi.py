"""
WSGI config for argus_bikeshop project.

It exposes the WSGI callable as a module-level variable named ``application``.
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'argus_bikeshop.settings')

# This is the standard Django application
application = get_wsgi_application()

# This is the entry point Vercel needs to find the app
app = application