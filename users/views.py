from django.contrib.auth.models import User
from .models import StudentProfile, Badge, Lesson, Evaluation, Message, Teacher, Subscription, Payment,Plan
from datetime import datetime
from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import StudentProfile  # تأكد إنه موجود فوق
from django.http import HttpResponse
from django.views import View
from .models import Appointment
from django.utils import timezone
from django.http import JsonResponse
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.admin.views.decorators import staff_member_required
from .models import Subscription
from .decorators import subscribe_required
from datetime import timedelta   # 👈 أهو اللي ناقص
import random
import string
from django.shortcuts import get_object_or_404
from django.contrib.auth.views import LogoutView
from .forms import SubscriptionForm
from .models import StudentProfile
from django.views.decorators.http import require_POST
from .models import ReviewPlan
from django.views.decorators.csrf import csrf_exempt
from users.models import Plan
import json
from .models import Notification
from .models import WeeklyProgress

def plans_list(request):
    plans = Plan.objects.all()
    user_subscriptions = {
        sub.plan_id: sub for sub in Subscription.objects.filter(user=request.user)
    } if request.user.is_authenticated else {}

    return render(request, "plans.html", {
        "plans": plans,
        "user_subscriptions": user_subscriptions,
        "today": timezone.now().date(),
    })



User = get_user_model()
def signup_view(request):
    if request.method == "POST":
        name = request.POST["name"]
        email = request.POST["email"]
        password1 = request.POST["password1"]
        password2 = request.POST["password2"]

        if password1 != password2:
            messages.error(request, "كلمتا المرور غير متطابقتين")
        elif User.objects.filter(email=email).exists():
            messages.error(request, "البريد الإلكتروني مسجّل مسبقًا")
        else:
            # إنشاء المستخدم
            user = User.objects.create_user(name=name, email=email, password=password1)
            
            # إنشاء StudentProfile تلقائي
            StudentProfile.objects.create(user=user)
            
            messages.success(request, "تم إنشاء الحساب بنجاح! سجّل دخولك الآن.")
            return redirect("login")

    return render(request, "html/signup.html")

def login_view(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]

        user = authenticate(request, email=email, password=password)
        if user:
            login(request, user)

            # توجيه حسب نوع المستخدم
            if user.user_type == 'student':
                return redirect("student_dashboard")
            elif user.user_type == 'teacher':
                return redirect("teacher_dashboard")  # اعمل صفحة المعلم
            elif user.user_type == 'admin':
                return redirect("admin_dashboard")    # اعمل لوحة التحكم

            # في حالة نوع غير معروف
            return redirect("student_dashboard")

        messages.error(request, "البريد الإلكتروني أو كلمة المرور غير صحيحة")

    return render(request, "html/login.html")



def logout_view(request):
    logout(request)
    return redirect("/")

@login_required
@require_POST
def update_profile_pic(request):
    user = request.user
    student_profile, created = StudentProfile.objects.get_or_create(user=user)
    image = request.FILES.get('image')
    if image:
        # لو تستخدم ImageField بدلاً من URLField في الموديل
        student_profile.image = image
        student_profile.save()
    return redirect('student_dashboard')

@login_required
def profile_view(request):
    user = request.user

    # مثال على الإحصائيات — تقدر تغيرها حسب المشروع
    stats = {
        "products_count": user.products.count() if hasattr(user, 'products') else 0,
        "reviews_count": user.reviews.count() if hasattr(user, 'reviews') else 0,
        "orders_count": user.orders.count() if hasattr(user, 'orders') else 0,
    }

    return render(request, 'profile.html', {
        'user': user,
        'stats': stats
    })
@login_required
def student_dashboard(request):
    user = request.user
    student_profile, created = StudentProfile.objects.get_or_create(user=user)
    now = timezone.now().date()
    student = request.user  # لو المستخدم الحالي هو الطالب

    student_data = {
        'name': user.name,
        'age': student_profile.age,
        'city': student_profile.city,
        'image': student_profile.image or 'https://randomuser.me/api/portraits/men/1.jpg',
        'level': student_profile.level,
        'current_surah': student_profile.current_surah,
        'current_juz': student_profile.current_juz,
        'progress': student_profile.progress,
        'commitment': student_profile.commitment,
        'notifications': 0,
        "student_data": student_profile,
        "reviews": student_profile.reviews,
        "rating": student_profile.rating,
    }

    messages_qs = Message.objects.filter(student=student_profile).order_by('-id')
    teachers = Teacher.objects.all()
    badges = Badge.objects.filter(student=student_profile)
    lessons_upcoming = Lesson.objects.filter(student=request.user, date__gte=now).order_by('date', 'time')
    lessons_past = Lesson.objects.filter(student=request.user, date__lt=now).order_by('-date', '-time')
    lessons = Lesson.objects.filter(student=request.user).order_by('-date', '-time')
    appointments = Appointment.objects.filter(phase=student_profile.level).order_by('date', 'start_time')
    evaluations = Evaluation.objects.filter(student=student_profile).order_by('-date')
    subscription = Subscription.objects.filter(user=request.user, status="approved").order_by('-end_date').first()
    payments = Payment.objects.filter(student=student_profile).order_by('-date')
    meetings = Lesson.objects.filter(student=request.user, date__gte=now)
    past_meetings = Lesson.objects.filter(student=request.user, date__lt=now)
    today = timezone.now().date()
    plans = student_profile.review_plans.all().order_by('-day')
  # 1. الأجزاء المحفوظة
    saved_parts = getattr(student_profile, "saved_parts", 0)  # عدل حسب اسم الحقل أو طريقة الحفظ

    # 2. المراجعات الناجحة
    successful_reviews = ReviewPlan.objects.filter(student=student_profile, is_completed=True).count()

    # 3. التقييم (آخر تقييم أو متوسط)
    last_evaluation = Evaluation.objects.filter(student=student_profile).order_by('-date').first()
    evaluation_stars = last_evaluation.stars if last_evaluation else 0
    latest_subscription = Subscription.objects.filter(user=request.user).order_by("-created_at").first()

    # 4. الالتزام (معدل الحضور)
    commitment = getattr(student_profile, "commitment", 0)
    # ✅ 4. التقييمات من الإدمن (بدل الحسابات القديمة)
    weekly_level = student_profile.weekly_level
    monthly_level = student_profile.monthly_level
    yearly_level = student_profile.yearly_level

   
    # ✅ احسب حالة الاشتراك قبل إضافته للـ context
    if subscription and subscription.end_date.date() > today:
        status = "نشط"
    else:
        status = "منتهي"

    context = {
        'student_data': student_data,
        'messages': messages_qs,
        'teachers': teachers,
        'badges': badges,
        'lessons': lessons,
        'lessons_upcoming': lessons_upcoming,
        'lessons_past': lessons_past,
        'evaluations': evaluations,
        'subscription': subscription,
        'payments': payments,
        'appointments': appointments,
        'meetings': meetings,
        'past_meetings': past_meetings,
        'evaluation': evaluations.first() if evaluations else None,
        "plans": plans,
        "status": status,
        'today': today,
        'saved_parts': saved_parts,
        'successful_reviews': successful_reviews,
        'evaluation_stars': evaluation_stars,
        'commitment': commitment,
        "latest_subscription": latest_subscription,
        "student": student,
    }

    return render(request, 'html/student_dashboard.html', context)

@login_required
def weekly_progress(request, student_id):
    days_order = ['السبت', 'الأحد', 'الإثنين', 'الثلاثاء', 'الأربعاء', 'الخميس', 'الجمعة']
    progress = WeeklyProgress.objects.filter(student_id=student_id)
    memorized_data = []
    reviews_data = []
    for day in days_order:
        record = progress.filter(day=day).order_by('-id').first()
        memorized_data.append(record.memorization_rating if record and record.memorization_rating else 'ضعيف')
        reviews_data.append(record.review_rating if record and record.review_rating else 'ضعيف')
    return JsonResponse({
        "days": days_order,
        "memorized": memorized_data,
        "reviews": reviews_data
    })
@login_required
def update_profile_data(request):
    if request.method == 'POST':
        user = request.user
        student_profile, created = StudentProfile.objects.get_or_create(user=user)

        # البيانات النصية
        student_profile.age = request.POST.get('age', student_profile.age)
        student_profile.city = request.POST.get('city', student_profile.city)
        student_profile.level = request.POST.get('level', student_profile.level)
        student_profile.current_surah = request.POST.get('current_surah', student_profile.current_surah)
        student_profile.current_juz = request.POST.get('current_juz', student_profile.current_juz)

        # الصورة
        if 'image' in request.FILES:
            student_profile.image = request.FILES['image']

        # الاسم
        user.name = request.POST.get('name', user.name)
        user.save()
        student_profile.save()

        return JsonResponse({
            "success": True,
            "message": "تم تحديث البيانات بنجاح ✅",
            "name": user.name,
            "age": student_profile.age,
            "city": student_profile.city,
            "level": student_profile.level,
            "current_surah": student_profile.current_surah,
            "current_juz": student_profile.current_juz,
            "image_url": student_profile.image.url if student_profile.image else None,
        })

    return JsonResponse({"success": False, "errors": "طلب غير صحيح"})
def your_view(request):
    response = HttpResponse()
    response['Content-Type'] = 'text/html; charset=utf-8'
    return response
def inbox(request):
    today = timezone.now()
    user_subscriptions = {}

    if request.user.is_authenticated:
        subs = Subscription.objects.filter(user=request.user)
        for sub in subs:
            if sub.plan:  # عشان نتجنب NoneType error
                user_subscriptions[sub.plan.id] = sub

    return render(
        request,
        "html/inbox.html",
        {"user_subscriptions": user_subscriptions, "today": today},
    )

def teachers(request):
    return render(request, 'teachers.html')

def contact(request):
    return render(request, 'contact.html')

def waiting_approval(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'html/waiting_approval.html')
# In your views.py

@login_required(login_url='login')
def subscribe(request, plan_id=None):
    plan = get_object_or_404(Plan, id=plan_id)

    if request.method == "POST":
        form = SubscriptionForm(request.POST, request.FILES)

        if form.is_valid():
            # ناخد appointment_id من الـ hidden input
            appointment_id = request.POST.get("appointment_id")
            if not appointment_id:
                messages.error(request, "يجب اختيار موعد.")
                return redirect("subscribe", plan_id=plan.id)

            try:
                appointment = Appointment.objects.get(id=appointment_id, plan=plan, is_booked=False)
            except Appointment.DoesNotExist:
                messages.error(request, "هذا الموعد غير متاح.")
                return redirect("subscribe", plan_id=plan.id)

            payment_image = form.cleaned_data.get("payment_image")

            start_date = timezone.now()
            end_date = start_date + timedelta(days=plan.duration_days)

            subscription = Subscription.objects.create(
                user=request.user,
                plan=plan,
                phase=plan.name,
                appointment=appointment,
                price=plan.price,
                duration_days=plan.duration_days,
                duration_text=plan.duration_text,
                teacher=plan.teacher,
                payment_image=payment_image,
                status="pending",
                created_at=start_date,
                end_date=end_date
            )

            appointment.is_booked = True
            appointment.booked_by = request.user
            appointment.save()

            messages.success(request, "تم إرسال طلب الاشتراك وهو في انتظار موافقة الإدارة.")
            return redirect("waiting_approval")

        else:
            print("❌ Subscription form errors:", form.errors)

    else:
        form = SubscriptionForm()

    return render(request, "html/subscribe.html", {
        "plan": plan,
        "duration_text": plan.duration_text,
        "form": form
    })



def payment(request):
    # Your view logic here
    return render(request, 'html/payment.html')
def payment_review(request):
    return render(request, 'html/payment_review.html')


def book_appointment(request, appointment_id):
    appointment = Appointment.objects.get(id=appointment_id)
    Lesson.objects.create(
        student=request.user,
        appointment=appointment,
        teacher=appointment.trainer,
        date=appointment.date,
        time=appointment.time,
        content="حصة قرآن"  # أو أي محتوى آخر
    )
    # إعادة التوجيه للداشبورد أو صفحة التأكيد
    return redirect('student_dashboard')

from django.shortcuts import get_object_or_404

def approve_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.is_active = True
    user.save()
    
    # Clear the subscription flag when admin approves
    if hasattr(request, 'session'):
        request.session['subscription_submitted'] = False
    
    return redirect('admin:auth_user_changelist')
@login_required
def check_approval_status(request):
    approved = request.user.is_active
    return JsonResponse({'approved': approved})

@receiver(post_save, sender=Payment)
def update_student_profile_receipt(sender, instance, created, **kwargs):
    if instance.invoice:
        try:
            profile = instance.student
            profile.payment_receipt = instance.invoice
            profile.save()
        except StudentProfile.DoesNotExist:
            # إنشاء بروفايل جديد لو مش موجود
            StudentProfile.objects.create(
                user=instance.student.user,  # أو حسب العلاقة عندك
                payment_receipt=instance.invoice,
                age=0,
                city='',
                country='',
                image='',
                level='-',
                current_surah='-',
                current_juz='-',
                progress=0,
                commitment='0%'
            )

@staff_member_required
def pending_students(request):
    students = StudentProfile.objects.filter(is_approved=False)
    return render(request, 'admin/pending_students.html', {'students': students})
@login_required
def check_subscription(request):
    try:
        subscription = Subscription.objects.get(user=request.user)
        return JsonResponse({'subscribed': subscription.active})
    except Subscription.DoesNotExist:
        return JsonResponse({'subscribed': False})
@login_required
def waiting_approval(request):
    subscription = Subscription.objects.filter(user=request.user).last()
    if not subscription:
        # مفيش اشتراك → رجعه على صفحة الاشتراك
        return redirect("subscribe", plan_id=1)

    # لو فيه اشتراك → اعرض صفحة قيد المراجعة
    return render(request, "html/waiting_approval.html", {"subscription": subscription})
def get_appointments_by_phase(request):
    phase = request.GET.get("phase")
    if not phase:
        return JsonResponse({"error": "phase is required"}, status=400)

    appointments = Appointment.objects.filter(phase=phase).values("id", "day", "time")
    return JsonResponse(list(appointments), safe=False)
@login_required(login_url='login')
def get_appointments(request):
    plan_id = request.GET.get("plan_id")
    appointments = Appointment.objects.filter(
        plan_id=plan_id
    ).order_by("day_of_week", "start_time")

    data = [
        {
            "id": a.id,
            "day": a.day_of_week,
            "time": a.start_time.strftime("%I:%M %p"),
            "period": a.get_period_display(),
            "is_booked": a.is_booked,
        }
        for a in appointments
    ]
    return JsonResponse(data, safe=False)
def meeting_detail(request, pk):
    meeting = get_object_or_404(Meeting, pk=pk)
    return render(request, "meeting_detail.html", {"meeting": meeting})
def lessons_schedule(request):
    lessons = Lesson.objects.all()
    return render(request, "lessons_schedule.html", {"lessons": lessons})
@login_required
def create_meeting(request):
    if request.method == "POST":
        form = MeetingForm(request.POST)
        if form.is_valid():
            meeting = form.save(commit=False)
            meeting.created_by = request.user
            meeting.save()
            return redirect("meeting_list")  # بعد الإنشاء يروح لقائمة الاجتماعات
    else:
        form = MeetingForm()
    return render(request, "users/create_meeting.html", {"form": form})
@login_required
def student_meetings(request):
    meetings = Meeting.objects.all().order_by("date")
    return render(request, "users/student_meetings.html", {"meetings": meetings})

@login_required
def toggle_review(request, plan_id):
    if request.method == "POST":
        plan = get_object_or_404(ReviewPlan, id=plan_id, student=request.user.studentprofile)
        plan.is_completed = not plan.is_completed
        plan.save()
        return JsonResponse({"is_completed": plan.is_completed})
    return JsonResponse({"error": "Invalid request"}, status=400)
@login_required
def notifications_list(request):
    notifications = request.user.notifications.order_by("-created_at")
    return render(request, "users/notifications.html", {"notifications": notifications})
def latest_notification(request):
    notif = Notification.objects.filter(user=request.user, is_read=False).last()
    if notif:
        # أول ما يجيبه، نعلمه إنه اتقرأ
        notif.is_read = True
        notif.save()

        return JsonResponse({
            "title": notif.title,
            "message": notif.message,
        })
    return JsonResponse({})


@csrf_exempt
def toggle_reminder(request, plan_id):
    if request.method == "POST":
        try:
            plan = ReviewPlan.objects.get(id=plan_id)
            data = json.loads(request.body.decode("utf-8"))  # نقرأ القيمة من الـ fetch
            plan.reminder_enabled = data.get("reminder_enabled", False)
            plan.save()
            return JsonResponse({"success": True, "reminder_enabled": plan.reminder_enabled})
        except ReviewPlan.DoesNotExist:
            return JsonResponse({"success": False, "error": "Plan not found"})
    return JsonResponse({"success": False, "error": "Invalid request"})
@csrf_exempt
def toggle_completed(request, plan_id):
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode("utf-8"))
            plan = ReviewPlan.objects.get(id=plan_id)
            plan.is_completed = data.get("is_completed", False)
            plan.save()
            return JsonResponse({"success": True, "is_completed": plan.is_completed})
        except ReviewPlan.DoesNotExist:
            return JsonResponse({"success": False, "error": "الخطة غير موجودة"})
    return JsonResponse({"success": False, "error": "طلب غير صالح"})

@login_required(login_url='login')
def subscription_history(request):
    # كل الاشتراكات الخاصة باليوزر الحالي
    subscriptions = Subscription.objects.filter(user=request.user).order_by("-created_at")

    return render(request, "html/subscription_history.html", {
        "subscriptions": subscriptions,
    })

@login_required
def meeting_view(request, lesson_id=None):
    # اسم غرفة فريد (مثلاً مرتبط بالدرس/المعلم/الطالب)
    base = f"quran-app-{request.user.id}-{lesson_id or ''}-{secrets.token_hex(4)}"
    room = slugify(base)  # بدون مسافات
    return render(request, "html/meeting.html", {"room_name": room})