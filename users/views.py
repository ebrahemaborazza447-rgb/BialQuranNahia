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
from django.db.models import Q
from django.contrib.auth import login

# views.py
from django.shortcuts import render
from googleapiclient.discovery import build
from google.oauth2 import service_account

from .models import GoogleFormResult
from .google_sheets import fetch_google_form_results
from .models import Exam
from .models import StudentProfile
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages as django_messages
from django.http import JsonResponse
from django.db.models import Q
from .models import Message
from django.contrib.auth import get_user_model
from .models import ContactMessage as Message
from .models import ContactMessage
from .forms import ContactForm


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
            messages.error(request, "❌ كلمتا المرور غير متطابقتين")
        elif User.objects.filter(email=email).exists():
            messages.error(request, "❌ البريد الإلكتروني مسجّل مسبقًا")
        else:
            # إنشاء المستخدم
            user = User.objects.create_user(
                name=name,
                email=email,
                password=password1
            )
            
            # إنشاء StudentProfile تلقائي
            StudentProfile.objects.create(user=user)

            # تسجيل دخول مباشر بعد التسجيل
            login(request, user, backend="django.contrib.auth.backends.ModelBackend")

            # توجيه حسب نوع المستخدم
            if user.user_type == 'student':
                return redirect("inbox")
            elif user.user_type == 'teacher':
                return redirect("inbox")
            elif user.user_type == 'admin':
                return redirect("inbox")

            return redirect("inbox")

    return render(request, "html/signup.html")


from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.shortcuts import render, redirect

def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(request, email=email, password=password)
        if user:
            login(request, user, backend="django.contrib.auth.backends.ModelBackend")

            # توجيه حسب نوع المستخدم
            if user.user_type == 'student':
                return redirect("inbox")
            elif user.user_type == 'teacher':
                return redirect("inbox")
            elif user.user_type == 'admin':
                return redirect("inbox")

            return redirect("inbox")
        else:
            messages.error(request, "❌ البريد الإلكتروني أو كلمة المرور غير صحيحة")

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
    # يجيب أو ينشئ البروفايل
    student_profile, created = StudentProfile.objects.get_or_create(user=user)

    now = timezone.now().date()
    today = timezone.now().date()
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

    messages_qs = ContactMessage.objects.filter(email=request.user.email)
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

    is_complete = student_profile.is_complete()

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
        "student": user,
        "is_complete": is_complete,
    }

    return render(request, 'html/student_dashboard.html', context)
def update_profile(request):
    if request.method == "POST" and request.user.is_authenticated:
        user = request.user
        student_profile, created = StudentProfile.objects.get_or_create(user=user)

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

    return redirect("inbox")

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

    # رجع exams كدكشنري مفصول حسب stage/plan.id
    exams_by_stage = {}
    all_exams = Exam.objects.all()
    for exam in all_exams:
        exams_by_stage.setdefault(exam.stage, []).append(exam)

    user_subscriptions = {}
    if request.user.is_authenticated:
        subs = Subscription.objects.filter(user=request.user)
        for sub in subs:
            if sub.plan:  # عشان نتجنب NoneType error
                user_subscriptions[sub.plan.id] = sub

    return render(
        request,
        "html/inbox.html",
        {
            "user_subscriptions": user_subscriptions,
            "today": today,
            "exams_by_stage": exams_by_stage,
        },
    )


def teachers(request):
    return render(request, 'html/teachers.html')
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.contrib import messages
from django.shortcuts import render, redirect
from django.conf import settings
from .forms import ContactForm

@login_required
def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            message_obj = form.save(commit=False)
            message_obj.user = request.user
            message_obj.name = f"{getattr(request.user, 'first_name', '')} {getattr(request.user, 'last_name', '')}".strip() or request.user.email
            message_obj.email = request.user.email
            message_obj.message_type = 'message'
            message_obj.save()

            # إرسال إيميل للإدمن
            send_mail(
                f'رسالة جديدة من {message_obj.name}',
                f'الاسم: {message_obj.name}\nالبريد الإلكتروني: {message_obj.email}\n\n{message_obj.message}',
                settings.DEFAULT_FROM_EMAIL,
                [settings.ADMIN_EMAIL],
                fail_silently=True,
            )

            messages.success(request, 'تم إرسال رسالتك بنجاح. سنقوم بالرد في أقرب وقت ممكن.')
            return redirect('student_dashboard')
    else:
        form = ContactForm()

    return render(request, 'html/contact.html', {'form': form})

@require_POST
def mark_as_read(request, message_id):
    if request.user.is_staff:
        try:
            message = ContactMessage.objects.get(id=message_id)
            message.status = 'read'
            message.save()
            return JsonResponse({'status': 'success'})
        except ContactMessage.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Message not found'}, status=404)
    return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=403)

def waiting_approval(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'html/waiting_approval.html')

@login_required(login_url='login')
def subscribe(request, plan_id):
    plan = get_object_or_404(Plan, id=plan_id)

    # لو الخطة فيها امتحان
    if plan.exam:
        results = GoogleFormResult.objects.filter(
            exam=plan.exam,   # نجيب النتائج الخاصة بالامتحان ده
            email__iexact=request.user.email
        ).order_by('-form_date')

        if not results.exists():
            # مفيش نتيجة أصلاً
            return redirect("inbox")

        last_result = results.first()
        percentage = last_result.calculate_percentage()  # أو last_result.score لو عندك النسبة محفوظة

        if percentage is None or percentage < 50:
            # ساقط
            return redirect('exam_failed', plan_id=plan.id, exam_id=plan.exam.id)
        # ناجح 👌
    # لو الخطة ملهاش امتحان
    if request.method == "POST":
        form = SubscriptionForm(request.POST, request.FILES)

        if form.is_valid():
            appointment_id = request.POST.get("appointment_id")
            if not appointment_id:
                messages.error(request, "يجب اختيار موعد.")
                return redirect("subscribe", plan_id=plan.id)

            try:
                appointment = Appointment.objects.get(id=appointment_id, plan=plan)
            except Appointment.DoesNotExist:
                messages.error(request, "هذا الموعد غير متاح.")
                return redirect("subscribe", plan_id=plan.id)

            # التحقق من نوع الموعد
            if appointment.is_public:
                # جماعي: تحقق إذا كان المستخدم مشارك بالفعل
                if request.user in appointment.participants.all():
                    messages.warning(request, "أنت بالفعل مشارك في هذا الموعد.")
                    return redirect("subscribe", plan_id=plan.id)
                # أضف المستخدم إلى المشاركين
                appointment.participants.add(request.user)
                appointment.save()
            else:
                # فردي: تحقق إذا كان محجوز بالفعل
                if appointment.is_booked:
                    messages.error(request, "هذا الموعد غير متاح.")
                    return redirect("subscribe", plan_id=plan.id)
                appointment.is_booked = True
                appointment.booked_by = request.user
                appointment.save()

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

            messages.success(request, "تم إرسال طلب الاشتراك وهو في انتظار موافقة الإدارة.")
            return redirect("waiting_approval")

        else:
            print("❌ Subscription form errors:", form.errors)

    else:
        form = SubscriptionForm()

    return render(request, "html/subscribe.html", {
        "plan": plan,
        "duration_text": plan.duration_text,
        "form": form,
    })



def payment(request):
    # Your view logic here
    return render(request, 'html/payment.html')
def payment_review(request):
    return render(request, 'html/payment_review.html')

@login_required(login_url='login')
def book_appointment(request, appointment_id):
    try:
        appointment = Appointment.objects.get(id=appointment_id)
    except Appointment.DoesNotExist:
        messages.error(request, "هذا الموعد غير موجود.")
        return redirect("appointments_list")

    # لو الموعد فردي ومتحجز بالفعل
    if not appointment.is_public:
        if appointment.is_booked:
            messages.error(request, "هذا الموعد غير متاح.")
            return redirect("appointments_list")
    else:
        # لو جماعي، تأكد إن المستخدم مش محجوز بالفعل
        if request.user in appointment.participants.all():
            messages.warning(request, "أنت بالفعل مشارك في هذا الموعد.")
            return redirect("appointments_list")


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
       return JsonResponse({'subscribed': subscription.is_active})

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

    appointments = Appointment.objects.filter(phase=student_profile.level).order_by('date', 'start_time')
    return JsonResponse(list(appointments), safe=False)


PHASE_MAP = {
    "مبتدئ": "beginner",
    "beginner": "beginner",
    "متوسط": "intermediate",
    "intermediate": "intermediate",
    "متقدم": "advanced",
    "advanced": "advanced",
    "متخصص": "expert",
    "expert": "expert",
    "المقرأة العامة": "general",
    "general": "general"
}

@login_required(login_url='login')
def get_appointments(request):
    plan_id = request.GET.get("plan_id")
    phase = request.GET.get("phase")  # ✅ ناخد المرحلة من الـ request

    if not plan_id:
        return JsonResponse([], safe=False)

    # ✅ فلترة بالمخطط والمرحلة
    appointments = Appointment.objects.filter(plan_id=plan_id)

    if phase:
        appointments = appointments.filter(Q(phase=phase) | Q(phase=PHASE_MAP.get(phase, "")))

    # ✅ لو الموعد عام OR مش محجوز
    appointments = appointments.filter(
         Q(is_public=True) | Q(is_booked=False)
    )


    data = [{
        "id": app.id,
        "day": app.day_of_week,
        "date": app.date.strftime("%Y-%m-%d") if app.date else "غير محدد",
        "time": app.start_time.strftime("%H:%M"),
        "period": app.period,
        "trainer": str(app.trainer) if app.trainer else "غير محدد",
        "is_booked": app.is_booked and not app.is_public,   # لو عام يفضل مفتوح
        "is_public": app.is_public,                        # جديد
        "participants": [p.email for p in app.participants.all()]
    } for app in appointments]

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


from django.shortcuts import render
def google_form(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    return render(request, "html/google_form.html", {"exam": exam})


def exam_list_view(request):
    exams = Exam.objects.all()
    return render(request, "exams/exam_list.html", {"exams": exams})

def exam_detail_view(request, pk):
    exam = get_object_or_404(Exam, pk=pk)
    return render(request, "exams/exam_detail.html", {"exam": exam})

def exam_results_view(request, pk):
    exam = get_object_or_404(Exam, pk=pk)
    if not exam.sheet_id:
        return HttpResponse("❌ رابط Google Sheet غير صالح")

    data = fetch_google_form_results(exam.sheet_id)
    return render(request, "exams/exam_results.html", {"exam": exam, "results": data})

def sync_all_results_view(request):
    if not Exam.objects.exists():
        return HttpResponse("❌ لا يوجد امتحانات")

    for exam in Exam.objects.all():
        if exam.sheet_id:
            fetch_and_store_entries(exam.sheet_id)

    return HttpResponse("✅ تم تحديث البيانات لكل الامتحانات")

def sync_job_trigger_view(request):
    sync_google_form_job()
    return HttpResponse("✅ تم تحديث البيانات عبر الـ Job")

def sync_google_form_results(request):
    SHEET_ID = "1JVXMnTC_Elh9bZckyBr6ZPeesPk_G2qkhe4Z7ucmP1E"
    data = fetch_google_form_results(SHEET_ID)

    for row in data:
        email = row.get("عنوان البريد الإلكتروني")
        score = row.get("النتيجة")

        # نخزن باقي الأعمدة
        answers = {k: v for k, v in row.items() if k not in ["عنوان البريد الإلكتروني", "النتيجة"]}

        # نعمل سجل جديد لكل إدخال
        GoogleFormResult.objects.create(
            email=email,
            score=score,
            answers=answers,
        )

    return HttpResponse("✅ تم تخزين كل النماذج كسجلات منفصلة")

def sync_google_form_job():
    exams = Exam.objects.exclude(google_sheet_url__isnull=True).exclude(google_sheet_url="")
    for exam in exams:
        sheet_id = exam.sheet_id
        if not sheet_id:
            print(f"❌ رابط غير صالح: {exam.google_sheet_url}")
            continue

        new_entries = fetch_and_store_entries(sheet_id, exam)
        print(f"✅ {exam.title} - تمت إضافة {len(new_entries)} نتيجة جديدة")

@login_required(login_url='login')
def exam_failed(request, plan_id, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)

    result = GoogleFormResult.objects.filter(
        exam=exam,
        email=request.user.email
    ).order_by('-form_date', '-submitted_at').first()

    context = {
        "exam": exam,
        "score": result.score if result else None,
        "percentage": result.percentage if result else None,
    }
    return render(request, "html/exam_failed.html", context)

User = get_user_model()


@login_required
def message_list(request):
    # هات كل الرسائل الخاصة بالمستخدم
    user_messages = ContactMessage.objects.filter(user=request.user).order_by('-created_at')

    # علّم الرسائل كـ مقروءة
    user_messages.filter(is_read=False).update(is_read=True)

    context = {
        'contact_messages': user_messages,  # ده اللي بيتعرض في التمبلت
        'unread_count': ContactMessage.objects.filter(user=request.user, is_read=False).count()
    }
    return render(request, 'html/message_list.html', context)

@login_required
def message_detail(request, message_id):
    try:
        message = get_object_or_404(Message, id=message_id, user=request.user)
        
        # تحديث حالة الرسالة كمقروءة
        if not message.is_read:
            message.is_read = True
            message.status = 'read'
            message.save(update_fields=['is_read', 'status'])
        
        # معالجة إرسال الرد
        if request.method == 'POST' and 'content' in request.POST:
            content = request.POST.get('content', '').strip()
            if content:  # التأكد من وجود محتوى قبل الحفظ
                reply = Message.objects.create(
                    user=request.user,
                    message_type=message.message_type,
                    subject=f"Re: {message.subject}",
                    content=content,
                    parent_message=message,
                    status='unread',
                    is_from_admin=not request.user.is_staff  # إذا كان المستخدم ليس مدير، فالرد من المستخدم
                )
                
                # معالجة المرفقات
                if 'attachments' in request.FILES:
                    for file in request.FILES.getlist('attachments'):
                        attachment = MessageAttachment(
                            message=reply,
                            file=file,
                            file_name=file.name,
                            file_type=file.content_type,
                            file_size=file.size
                        )
                        attachment.save()
                
                # تحديث حالة الرسالة الأصلية
                message.status = 'replied'
                message.save(update_fields=['status'])
                
                # إعادة توجيه المستخدم بنجاح
                messages.success(request, 'تم إرسال الرد بنجاح')
                return redirect('message_detail', message_id=message_id)
            else:
                messages.error(request, 'يرجى إدخال محتوى الرد')
        
        # الحصول على سجل المحادثة
        thread = Message.objects.filter(
            models.Q(id=message.parent_message_id) | 
            models.Q(parent_message=message) |
            models.Q(parent_message_id=message.parent_message_id)
        ).exclude(id=message.id).order_by('created_at')

        return render(request, 'html/message_detail.html', {
            'message': message,
            'thread': thread,
            'unread_count': get_unread_count(request.user)
        })
        
    except Exception as e:
        messages.error(request, f'حدث خطأ: {str(e)}')
        return redirect('message_list')

@login_required
def send_message(request):
    if request.method == 'POST':
        subject = request.POST.get('subject')
        content = request.POST.get('content')
        message_type = request.POST.get('message_type', 'message')
        
        if subject and content:
            Message.objects.create(
                user=request.user,
                subject=subject,
                content=content,
                message_type=message_type,
                is_from_admin=False
            )
            django_messages.success(request, 'تم إرسال رسالتك بنجاح')
            return redirect('message_list')
    
    return redirect('contact')

@login_required
def delete_message(request, message_id):
    message = get_object_or_404(Message, id=message_id, user=request.user)
    message.delete()
    django_messages.success(request, 'تم حذف الرسالة بنجاح')
    return redirect('message_list')

def unread_messages_count(request):
    if request.user.is_authenticated:
        return {
            'unread_messages_count': Message.objects.filter(user=request.user, is_read=False).count()
        }
    return {}
def get_unread_count(request):
    count = Message.objects.filter(is_read=False, receiver=request.user).count()
    return JsonResponse({'unread_count': count})


def privacy_view(request):
    return render(request, 'html/privacy.html')
def faq_view(request):
    return render(request, 'html/faq.html')
def terms_view(request):
    return render(request, 'html/terms.html')

def about_me(request):
    return render(request, 'html/about_me.html')
