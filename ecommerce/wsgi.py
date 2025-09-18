"""
WSGI config for ecommerce project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
# """
import sys

import os
# أضف مسار المشروع
path = r"C:\Users\DATA Technology\Desktop\test5\ecommerce"
# path = '/home/BialQuranNahia/BialQuranNahia'
if path not in sys.path:
    sys.path.append(path)

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')

application = get_wsgi_application()
