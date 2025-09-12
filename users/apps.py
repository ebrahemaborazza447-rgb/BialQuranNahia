# users/apps.py
import os
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _
from apscheduler.schedulers.background import BackgroundScheduler

class UsersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "users"
    verbose_name = _("المستخدمين")

    def ready(self):
        import users.signals

        if os.environ.get("RUN_MAIN") == "true":
            from .tasks import sync_google_form_job  # 👈 صح هنا

            scheduler = BackgroundScheduler()
            scheduler.add_job(sync_google_form_job, "interval", minutes=1)
            scheduler.start()
