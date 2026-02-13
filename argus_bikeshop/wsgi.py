import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'argus_bikeshop.settings')

application = get_wsgi_application()

# Vercel needs the 'app' variable to point to the WSGI application
app = application
