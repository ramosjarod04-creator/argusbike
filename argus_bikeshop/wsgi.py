import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'argus_bikeshop.settings')

application = get_wsgi_application()

# This handles the database migration on Vercel deployment automatically
try:
    from django.core.management import call_command
    print("Running migrations...")
    call_command('migrate', interactive=False)
except Exception as e:
    print(f"Migration error: {e}")

app = application