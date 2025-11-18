from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    CustomUser, StudentProfile, Badge, Lesson, Evaluation, Message,
    Teacher, Subscription, Payment, Appointment, Plan
)
from django.utils.html import format_html
from django.shortcuts import render, redirect
from .models import ReviewPlan
from .models import WeeklyProgress
from .models import GoogleFormResult
from .models import Exam
from .models import ContactMessage

# Action لتفعيل المستخدمين
@admin.action(description='تفعيل المستخدمين المحددين')
def make_active(modeladmin, request, queryset):
    queryset.update(is_active=True)

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('email', 'name', 'user_type', 'is_staff', 'is_active')
    list_filter = ('user_type', 'is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('email', 'name', 'password', 'user_type')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'user_type', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )
    search_fields = ('email', 'name')
    ordering = ('email',)
    actions = [make_active]

try:
    admin.site.unregister(CustomUser)
except admin.sites.NotRegistered:
    pass

admin.site.register(CustomUser, CustomUserAdmin)

@admin.register(WeeklyProgress)
class WeeklyProgressAdmin(admin.ModelAdmin):
    list_display = ('student', 'day',  'memorization_rating',  'review_rating')
    list_editable = ('day','memorization_rating', 'review_rating')
# admin.py
@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user", "age", "city", "level", "current_surah", "current_juz",
        "progress", "commitment", "weekly_level", "monthly_level", "yearly_level"
    )
    search_fields = ("user__name", "user__email", "city")
    list_filter = ("weekly_level", "monthly_level", "yearly_level", "city")
  
    actions = ["calculate_commitment"]

    def commitment_percent(self, obj):
        return f"{obj.commitment}%"   # ✅ كده يبان في الجدول بالنسبة
    commitment_percent.short_description = "الالتزام"

    @admin.action(description="احسب الالتزام تلقائيًا")
    def calculate_commitment(self, request, queryset):
        for profile in queryset:
            total_lessons = profile.lesson_set.count()
            attended = profile.lesson_set.filter(status="حضر").count()
            if total_lessons > 0:
                profile.commitment = round((attended / total_lessons) * 100, 2)
            else:
                profile.commitment = 0
            profile.save()
        self.message_user(request, f"✅ تم تحديث الالتزام لـ {queryset.count()} طالب")
        
# @admin.register(Badge)
# class BadgeAdmin(admin.ModelAdmin):
#     list_display = ('student', 'label', 'icon', 'bg', 'text_color', 'label_color')
#     search_fields = ('label', 'student__user__name')
#     list_filter = ('bg', 'text_color')

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = (
        "id", "plan", "phase", "day_of_week", "date",
        "start_time", "period", "is_booked", "trainer",
        "booked_by_display", "participants_list",
        "participants_count", "is_public"
    )

    list_filter = ("plan", "phase", "day_of_week", "period", "is_booked")
    search_fields = ("day_of_week", "phase", "trainer")
    ordering = ("date", "start_time")
    filter_horizontal = ("participants",)  # عشان اختيار المشاركين يبقى أسهل

    # ✅ نخصص الحقول حسب نوع الموعد
    def get_fieldsets(self, request, obj=None):
        base_fields = (
            ("بيانات الموعد", {
                "fields": ("plan", "phase", "day_of_week", "date", "start_time", "period")
            }),
            ("المعلم", {
                "fields": ("trainer",)
            }),
        )

        if obj and obj.is_public:
            # جماعي → participants
            booking_fields = ("الحجز", {
                "fields": ("is_booked", "is_public", "participants")
            })
        else:
            # فردي → booked_by
            booking_fields = ("الحجز", {
                "fields": ("is_booked", "is_public", "booked_by")
            })

        return base_fields + (booking_fields,)

    # عرض أسماء المشاركين
    def participants_list(self, obj):
        return ", ".join([p.email for p in obj.participants.all()])

    participants_list.short_description = "المشاركون"

    # عدد المشاركين
    def participants_count(self, obj):
        return obj.participants.count()
    participants_count.short_description = "عدد المشاركين"

    # عرض اسم الشخص الحاجز في حالة الفردي
    def booked_by_display(self, obj):
        return obj.booked_by.name if obj.booked_by else "-"
    booked_by_display.short_description = "المستخدم الحاجز"

    # لو الموعد محجوز → نخلي booked_by للقراءة فقط
    def get_readonly_fields(self, request, obj=None):
        if obj and obj.is_booked:
            return ("booked_by",)
        return ()

    # Action لتعيين مرحلة ومدرب
    actions = ["assign_phase_and_trainer"]

    def assign_phase_and_trainer(self, request, queryset):
        from django.contrib import messages
        from .models import Phase, Trainer

        try:
            phase = Phase.objects.get(name="المرحلة الأولى")
            trainer = Trainer.objects.get(name="ابراهيم")
        except (Phase.DoesNotExist, Trainer.DoesNotExist):
            self.message_user(request, "❌ المرحلة أو المدرب غير موجودين", level=messages.ERROR)
            return

        count = queryset.update(phase=phase, trainer=trainer)
        self.message_user(request, f"✅ تم تحديث {count} موعد وتعيين المرحلة والمدرب لهم", level=messages.SUCCESS)

    assign_phase_and_trainer.short_description = "إسناد المرحلة الأولى والمدرب إبراهيم"
@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "plan",
        "phase",
        "appointment",
        "appointment_name",
        "teacher",
        "status",
        "start_date",
        "end_date",
    )
    list_filter = ("status", "phase", "plan")
    search_fields = ("user__email", "user__name", "teacher")
    ordering = ("-created_at",)

    actions = ["approve_subscriptions", "reject_subscriptions"]
    
    fieldsets = (
        ("بيانات الاشتراك", {
            "fields": ("user", "plan", "phase", "appointment", "appointment_name", "teacher", "description")
        }),
        ("الدفع", {
            "fields": ("payment_image", "price", "duration_days", "duration_text")
        }),
        ("الحالة", {
            "fields": ("status", "start_date", "end_date")
        }),
    )
    readonly_fields = ("start_date",)  # يظهر لكن مش قابل للتعديل

    @admin.action(description="الموافقة على الاشتراكات المحددة")
    def approve_subscriptions(self, request, queryset):
        count = 0
        for sub in queryset:
            sub.status = "approved"
            sub.save()
            if sub.appointment and not sub.appointment.is_booked:
                sub.appointment.is_booked = True
                sub.appointment.booked_by = sub.user
                sub.appointment.save()
            count += 1
        self.message_user(request, f"تمت الموافقة على {count} اشتراك/اشتراكات ✅")

    @admin.action(description="رفض الاشتراكات المحددة")
    def reject_subscriptions(self, request, queryset):
        updated = queryset.update(status="rejected")
        self.message_user(request, f"تم رفض {updated} اشتراك/اشتراكات ❌")

@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ("name", "duration_days", "duration_text", "exam", "price", "teacher", "plan_code")
    search_fields = ("name",)
    ordering = ("price",)

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'student', 'teacher', 'date', 'time', 'meeting_link', 'record_link')
    search_fields = ('title', 'teacher__name', 'student__name')
    list_filter = ('date', 'teacher')

@admin.register(Evaluation)
class EvaluationAdmin(admin.ModelAdmin):
    list_display = ('student', 'teacher', 'date', 'stars')
    search_fields = ('student__user__name', 'teacher__name')
    list_filter = ('date', 'stars')

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'student', 'time', 'text')
    search_fields = ('teacher__name', 'student__user__name', 'text')
    list_filter = ('teacher', 'student')

# @admin.register(Teacher)
# class TeacherAdmin(admin.ModelAdmin):
#     list_display = ('name',)
#     search_fields = ('name',)

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('student', 'date', 'amount', 'status', 'invoice_preview')
    list_filter = ('status', 'date')
    actions = ['confirm_payment']

    def invoice_preview(self, obj):
        if obj.invoice:
            return format_html('<img src="{}" style="width: 100px; height:auto;" />', obj.invoice.url)
        return "لا يوجد"
    invoice_preview.short_description = "صورة الإيصال"

    @admin.action(description='تأكيد الدفع وتفعيل المستخدم')
    def confirm_payment(self, request, queryset):
        for payment in queryset:
            payment.status = 'confirmed'
            payment.save()
            # تفعيل المستخدم
            payment.student.user.is_active = True
            payment.student.user.save()
            
            
    def create_meeting(request):
        if request.method == "POST":
            title = request.POST.get("title")
            meeting = Meeting.objects.create(host=request.user, title=title)
            return redirect("meeting_detail", pk=meeting.id)
        return render(request, "create_meeting.html") 
     
@admin.register(ReviewPlan)
class ReviewPlanAdmin(admin.ModelAdmin):
    list_display = ("title", "student", "day", "created_at", 'is_completed', "successful_reviews_manual")
    list_filter = ("day", "student")
    search_fields = ("title", "description", "student__user__username")
    list_editable = ("is_completed", "successful_reviews_manual")

    def successful_reviews_display(self, obj):
        return obj.successful_reviews
    successful_reviews_display.short_description = "عدد المراجعات الناجحة"
    
@admin.register(GoogleFormResult)
class GoogleFormResultAdmin(admin.ModelAdmin):
    list_display = ("exam", "email", "score", "form_date", "submitted_at")
    search_fields = ("email", "score")
    list_filter = ("exam", "submitted_at")

@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "stage", "google_form_link", "google_sheet_url", "created_at")
    search_fields = ("title", "google_form_link", "google_sheet_url")
    list_filter = ("stage", "created_at")
@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'created_at', 'status', 'short_message', 'is_read')
    list_filter = ('status', 'is_read', 'created_at')
    search_fields = ('name', 'email', 'message')
    list_editable = ('status', 'is_read')
    readonly_fields = ('name', 'email', 'message', 'created_at')
    date_hierarchy = 'created_at'
    
    def short_message(self, obj):
        return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message
    short_message.short_description = 'الرسالة'
