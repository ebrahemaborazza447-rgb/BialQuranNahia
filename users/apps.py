import os
from django.apps import AppConfig

class UsersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "users"

    def ready(self):
        # 🟢 1- يشغل reminders مره واحدة
        if os.environ.get("RUN_MAIN") == "true":
            from . import reminders
            reminders.start()

        # 🟢 2- يتأكد أن في خطة أساسية
       

