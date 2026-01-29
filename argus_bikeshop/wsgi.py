import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'argus_bikeshop.settings')

application = get_wsgi_application()

# Runs migrations on every deployment to ensure Neon DB is ready
try:
    from django.core.management import call_command
    print("Executing auto-migrations...")
    call_command('migrate', interactive=False)
except Exception as e:
    print(f"Auto-migration failed: {e}")

app = application