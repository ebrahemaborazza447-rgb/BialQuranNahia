from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from django.utils import timezone
from django.conf import settings

from .models import ReviewPlan, Notification


def daily_review_notifications():
    """إنشاء تنبيه يومي للمراجعة لكل خطة مفعلة"""
    today = timezone.now().date()
    plans = ReviewPlan.objects.filter(
        day=today,
        is_completed=False,
        reminder_enabled=True   # ✅ بس المفعلة
    )

    for plan in plans:
        Notification.objects.create(
            user=plan.student.user,
            title="تذكير بالمراجعة اليومية",
            message=f"لديك مراجعة: {plan.surah} (عدد الآيات: {plan.ayat_count})",
        )
    print(f"✅ تم إنشاء {plans.count()} تنبيه لليوم {today}")


def start():
    scheduler = BackgroundScheduler(timezone=settings.TIME_ZONE)
    scheduler.add_jobstore(DjangoJobStore(), "default")

    # مثال: تشغيله كل يوم الساعة 8 صباحاً
    scheduler.add_job(
        daily_review_notifications,
        "cron",
        id="daily_review_notifications",
        hour=6,
        minute=38,
        replace_existing=True,
    )

    scheduler.start()
    print("🚀 الـ APScheduler بدأ يشتغل")
