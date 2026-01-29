"""
WSGI config for argus_bikeshop project.

It exposes the WSGI callable as a module-level variable named ``application``.
"""

import os
from django.core.wsgi import get_wsgi_application

# Set the settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'argus_bikeshop.settings')

# Initialize the WSGI application
application = get_wsgi_application()

# --- DATABASE AUTO-MIGRATE ---
# This part ensures your Neon database tables are created automatically
try:
    from django.core.management import call_command
    print("Running migrations...")
    call_command('migrate', interactive=False)
except Exception as e:
    print(f"Migration failed: {e}")
# -----------------------------

# Vercel looks for 'app'
app = application