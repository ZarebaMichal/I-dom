"""
WSGI config for my_application project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/wsgi/
"""
import sys
import os

# important for deploying
path =  ('/home/ubuntu/I-dom/I-DOM')

sys.path.append('/home/ubuntu/I-dom/lib/python3.8/site-packages/')
#sys.path.append('/home/ubuntu/I-dom/my_application')
if path not in sys.path:
        sys.path.append(path)


from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'my_application.settings')

application = get_wsgi_application()
