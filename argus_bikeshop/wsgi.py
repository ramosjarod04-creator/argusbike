import os
import sys
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'argus_bikeshop.settings')

application = get_wsgi_application()

# Attempt auto-migration for Neon Database
try:
    from django.core.management import call_command
    print("Vercel Deployment: Running database migrations...")
    call_command('migrate', interactive=False)
except Exception as e:
    print(f"Migration Error: {e}", file=sys.stderr)

app = application