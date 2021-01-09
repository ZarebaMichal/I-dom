"""
WSGI config for my_application project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/wsgi/
"""
import sys
import os

# important for deploying
path =  ('/home/pi/I-dom/I-DOM')
# import CHECK FEW TIMES IF USER IS CORRECT
sys.path.append('/home/pi/I-dom/lib/python3.7/site-packages/')
#sys.path.append('/home/ubuntu/I-dom/my_application')
if path not in sys.path:
        sys.path.append(path)


from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'my_application.settings')

application = get_wsgi_application()
