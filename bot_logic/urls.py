from django.urls import path
from django.conf import settings
from .views import get_web_hook
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path(f'{settings.TELEGRAM_TOKEN}', csrf_exempt(get_web_hook))
]
