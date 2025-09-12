from django.dispatch import receiver
from allauth.account.signals import user_signed_up
from .models import StudentProfile

@receiver(user_signed_up)
def create_student_profile(request, user, **kwargs):
    """
    يتنفذ أول مرة المستخدم يسجل دخول بجوجل.
    """
    # إنشاء StudentProfile لو مش موجود
    if not StudentProfile.objects.filter(user=user).exists():
        StudentProfile.objects.create(user=user)

    # نخلي نوع المستخدم طالب (افتراضي)
    if not hasattr(user, "user_type") or not user.user_type:
        user.user_type = "student"
        user.save()
