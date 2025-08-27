from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.conf import settings
from datetime import timedelta
import random, string
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone

import uuid
# User Manager
class CustomUserManager(BaseUserManager):
    def create_user(self, email, name, password=None, **extra_fields):
        if not email:
            raise ValueError("البريد الإلكتروني مطلوب")
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, name, password, **extra_fields)

# Custom User
class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    USER_TYPE_CHOICES = (
        ('student', 'طالب'),
        ('teacher', 'معلم'),
        ('admin', 'مشرف'),
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='student')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    objects = CustomUserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return self.email

# Teacher
class Teacher(models.Model):
    name = models.CharField(max_length=100)
    image = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name


def get_default_teacher():
    """ترجع id لمعلم اسمه 'معلم غير محدد' لو موجود"""
    teacher = Teacher.objects.filter(name="معلم غير محدد").first()
    return teacher.id if teacher else None



class StudentProfile(models.Model):
    # خيارات التقييم
    LEVEL_CHOICES = [
        ("ضعيف", "ضعيف"),
        ("جيد", "جيد"),
        ("جيد جدا", "جيد جدا"),
        ("ممتاز", "ممتاز"),
        ("ممتاز جدا", "ممتاز جدا"),
    ]
    LEVEL_CHOICES = [
        ("مبتدئ", "مبتدئ"),
        ("متوسط", "متوسط"),
        ("متقدم", "متقدم"),
    ]
    # بيانات أساسية
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    age = models.PositiveIntegerField(default=0)
    city = models.CharField(max_length=100, blank=True)
    image = models.ImageField(upload_to='student_images/', blank=True, null=True)
    current_surah = models.CharField(max_length=100, default='-')
    current_juz = models.CharField(max_length=100, default='-')
    progress = models.PositiveSmallIntegerField(default=0)
    payment_receipt = models.ImageField(upload_to='student_receipts/', null=True, blank=True)
    reviews = models.IntegerField(default=0, verbose_name="المراجعات الناجحة")
    rating = models.IntegerField(default=0, verbose_name="التقييم")  # مثلاً من 5
    commitment = models.FloatField(default=0, verbose_name="معدل الالتزام")  # %
    weekly_level = models.CharField(max_length=20, choices=LEVEL_CHOICES, blank=True, null=True, verbose_name="التقييم الأسبوعي")
    monthly_level = models.CharField(max_length=20, choices=LEVEL_CHOICES, blank=True, null=True, verbose_name="التقييم الشهري")
    yearly_level = models.CharField(max_length=20, choices=LEVEL_CHOICES, blank=True, null=True, verbose_name="التقييم السنوي")
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default="مبتدئ")  # 👈 رجّعه هنا

    def __str__(self):
        return self.user.name
    
class Meta:
    unique_together = ('student', 'day')
class WeeklyProgress(models.Model):
    
    DAYS_OF_WEEK = [
    ('السبت', 'السبت'),
    ('الأحد', 'الأحد'),
    ('الإثنين', 'الإثنين'),
    ('الثلاثاء', 'الثلاثاء'),
    ('الأربعاء', 'الأربعاء'),
    ('الخميس', 'الخميس'),
    ('الجمعة', 'الجمعة'),
]
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    day = models.CharField(max_length=10, choices=DAYS_OF_WEEK)
    
    
    memorization_rating = models.CharField(
        max_length=20,
        choices=[
            ('ضعيف', 'ضعيف'),
            ('جيد', 'جيد'),
            ('جيد جدًا', 'جيد جدًا'),
            ('ممتاز', 'ممتاز'),
            ('ممتاز جدًا', 'ممتاز جدًا')
        ],
        blank=True,
        null=True
    )
    review_rating = models.CharField(
        max_length=20,
        choices=[
            ('ضعيف', 'ضعيف'),
            ('جيد', 'جيد'),
            ('جيد جدًا', 'جيد جدًا'),
            ('ممتاز', 'ممتاز'),
            ('ممتاز جدًا', 'ممتاز جدًا')
        ],
        blank=True,
        null=True
    )
class Appointment(models.Model):
    PHASE_CHOICES = [
        ("beginner", "مبتدئ"),
        ("intermediate", "متوسط"),
        ("advanced", "متقدم"),
        ("expert", "متخصص"),
        ("general", "المقرأة العامة"),
    ]
    PERIOD_CHOICES = [
        ("am", "صباحًا"),
        ("pm", "مساءً"),
    ]
    DAYS_CHOICES = [
        ("saturday", "السبت"),
        ("sunday", "الأحد"),
        ("monday", "الاثنين"),
        ("tuesday", "الثلاثاء"),
        ("wednesday", "الأربعاء"),
        ("thursday", "الخميس"),
        ("friday", "الجمعة"),
    ]
    plan = models.ForeignKey('users.Plan', on_delete=models.CASCADE, null=True, blank=True)
    phase = models.CharField(max_length=20, choices=PHASE_CHOICES, verbose_name="المرحلة", default="beginner")
    period = models.CharField(max_length=20, choices=PERIOD_CHOICES, default="am", verbose_name="الفترة")
    day_of_week = models.CharField(max_length=20, verbose_name="اليوم", default="غير محدد")
    date = models.DateField(null=True, blank=True, verbose_name="التاريخ (اختياري)")
    start_time = models.TimeField(verbose_name="وقت البداية", default="00:00")
    trainer = models.CharField(max_length=100, verbose_name="المدرب", default="غير محدد")
    is_booked = models.BooleanField(default=False, verbose_name="محجوز؟")
    booked_by = models.ForeignKey("CustomUser", on_delete=models.SET_NULL, null=True, blank=True)
    day = models.CharField(max_length=20, choices=DAYS_CHOICES, null=True, blank=True)

    def __str__(self):
        return f"{self.get_phase_display()} - {self.get_day_display()} {self.start_time} ({self.get_period_display()}) - {self.trainer}"

    def clean(self):
        if self.start_time.hour >= 12 and self.period == "am":
            raise ValidationError("الوقت يشير إلى فترة مسائية، لكن اخترت صباحاً.")
        if self.start_time.hour < 12 and self.period == "pm":
            raise ValidationError("الوقت يشير إلى فترة صباحية، لكن اخترت مساءً.")
# Badge
class Badge(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    icon = models.CharField(max_length=50)
    label = models.CharField(max_length=50)
    bg = models.CharField(max_length=20, default='bg-gray-100')
    text_color = models.CharField(max_length=20, default='text-gray-400')
    label_color = models.CharField(max_length=20, default='text-gray-400')
    def __str__(self):
        return self.label

# Lesson
class Lesson(models.Model):
    title = models.CharField(max_length=255, null=True, blank=True)
    date = models.DateField()
    time = models.TimeField()
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True, default=get_default_teacher)
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    meeting_link = models.URLField(blank=True, null=True)
    record_link = models.URLField(blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    # أي حقول إضافية

    def __str__(self):
        return self.title

# Evaluation
class Evaluation(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True)
    date = models.DateField()
    stars = models.PositiveSmallIntegerField(default=0)
    comment = models.TextField(blank=True)

    def last_evaluation(self):
        return self.evaluation_set.order_by('-date').first()

    def last_stars(self):
        last_eval = self.last_evaluation()
        return last_eval.stars if last_eval else 0

    def __str__(self):
        return f"{self.student.user.name} - {self.stars} نجوم"

# Message
class Message(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True)
    time = models.CharField(max_length=50)
    text = models.TextField()
    def __str__(self):
        return f"{self.teacher} > {self.student}"

# Plan
class Plan(models.Model):
    custom_id = models.PositiveIntegerField(unique=True, null=True, blank=True, verbose_name="Plan Code")

    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    duration_days = models.IntegerField(default=30)
    duration_text = models.CharField(max_length=50, default="شهر")
    price = models.DecimalField(max_digits=8, decimal_places=2)
    teacher = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.name
from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

class Subscription(models.Model):
    PHASE_CHOICES = [
        ('beginner', 'مبتدئ'),
        ('intermediate', 'متوسط'),
        ('advanced', 'متقدم'),
        ('expert', 'متخصص'),
        ('general', 'المقرأة العامة'),
    ]
    appointment = models.ForeignKey('Appointment', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="الموعد")
    appointment_name = models.CharField(max_length=100, verbose_name="اسم الموعد", null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)
    plan = models.ForeignKey('Plan', on_delete=models.CASCADE, null=True, blank=True)
    phase = models.CharField(max_length=100, choices=PHASE_CHOICES, null=True, blank=True)
    teacher = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(null=True, blank=True)
    payment_image = models.ImageField(upload_to='payments/', null=True, blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    duration_days = models.IntegerField(blank=True, null=True)
    duration_text = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=[("pending", "قيد المراجعة"), ("approved", "مقبول"), ("rejected", "مرفوض")],
        default="pending",
    )
    start_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    end_date = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    @property
    def is_active(self):
        now = timezone.now()
        return self.status == "approved" and self.end_date and self.end_date > now

    @property
    def display_status(self):
        now = timezone.now()
        if self.status == "rejected":
            return "مرفوض"
        elif self.status == "pending":
            return "قيد المراجعة"
        elif self.status == "approved":
            if self.end_date and self.end_date > now:
                return "نشط"
            else:
                return "منتهي"
        return "غير معروف"

    def __str__(self):
        user_label = getattr(self.user, "email", None) or getattr(self.user, "username", None) or str(self.user)
        plan_label = getattr(self.plan, "name", None) or str(self.plan)
        status_label = self.get_status_display() if hasattr(self, "get_status_display") else self.status
        return f"{user_label} – {plan_label} – {status_label}"

    def save(self, *args, **kwargs):
        if not self.end_date and self.plan and self.plan.duration_days:
            self.end_date = timezone.now() + timedelta(days=self.plan.duration_days)
        super().save(*args, **kwargs)

# Payment
class Payment(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=[('pending', 'قيد المراجعة'), ('confirmed', 'تم التأكيد')], default='pending')
    invoice = models.ImageField(upload_to='payment_invoices/')
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, null=True, blank=True)
    def __str__(self):
        return f"دفع {self.student} - {self.status}"
    
    
def generate_room_name():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=12))
class ReviewPlan(models.Model):
    student = models.ForeignKey(
        "StudentProfile",
        on_delete=models.CASCADE,
        related_name="review_plans",
        null=True,
        blank=True
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    day = models.DateField(default=timezone.now)
    surah = models.CharField(max_length=100, blank=True, null=True)
    ayat_count = models.PositiveIntegerField(default=0)
    is_completed = models.BooleanField(default=False)
    reminder_enabled = models.BooleanField(default=False)  # ✅ اختيار المستخدم

    # 🔹 الإدخال اليدوي
    successful_reviews_manual = models.PositiveIntegerField(null=True, blank=True)

    @property
    def successful_reviews_auto(self):
        """الحسبة الأوتوماتيك"""
        return ReviewPlan.objects.filter(student=self.student, is_completed=True).count()

    @property
    def successful_reviews(self):
        """نستخدم اليدوي لو متسجل، وإلا نرجع الأوتوماتيك"""
        if self.successful_reviews_manual is not None:
            return self.successful_reviews_manual
        return self.successful_reviews_auto   # ✅ هنا كان فيه return زايدة

    def __str__(self):
        return f"{self.student.user.name} - {self.title}"

class ReviewTask(models.Model):
    plan = models.ForeignKey("ReviewPlan", related_name="tasks", on_delete=models.CASCADE)
    description = models.CharField(max_length=255)
    is_done = models.BooleanField(default=False)
class Notification(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications"
    )
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.title}"
