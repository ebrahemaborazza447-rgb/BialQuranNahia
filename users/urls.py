from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth import views as auth_views
from users.views import logout_view
import json

urlpatterns = [
    path("signup/", views.signup_view, name="signup"),
    path("login/", views.login_view, name="login"),
    path('profile/', views.profile_view, name='profile'),
    path('student_dashboard/', views.student_dashboard, name='student_dashboard'),
    path('', views.inbox, name='inbox'),
    path('teachers/', views.teachers, name='teachers'),
    path('contact/', views.contact, name='contact'),
    path('payment/', views.payment, name='payment'),
    path('payment_review/', views.payment_review, name='payment_review'),
    path('check_approval/', views.check_approval_status, name='check_approval'),
    path('ajax/get_appointments/', views.get_appointments_by_phase, name='get_appointments_by_phase'),
    path('check_subscription/', views.check_subscription, name='check_subscription'),
    path("waiting_approval/", views.waiting_approval, name="waiting_approval"),
path("subscribe/<int:plan_id>/", views.subscribe, name="subscribe"),
path("get_appointments/", views.get_appointments, name="get_appointments"),
    path("admin/", admin.site.urls),
    path("schedule/", views.lessons_schedule, name="lessons_schedule"),
    path("meeting/<int:pk>/", views.meeting_detail, name="meeting_detail"),
    path('logout/', logout_view, name="logout"),
# ecommerce/urls.py
path("meetings/create/", views.create_meeting, name="create_meeting"),
path("student_meetings/", views.student_meetings, name="student_meetings"),
    path('student/update-profile/', views.update_profile_data, name='update_profile_data'),
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
path('student/update-profile-pic/', views.update_profile_pic, name='update_profile_pic'),
path("review/toggle/<int:plan_id>/", views.toggle_review, name="toggle_review"),
    path("review/toggle-reminder/<int:plan_id>/", views.toggle_reminder, name="toggle_reminder"),
    path("toggle-reminder/<int:plan_id>/", views.toggle_reminder, name="toggle_reminder"),
path("toggle-completed/<int:plan_id>/", views.toggle_completed, name="toggle_completed"),
path("latest-notification/", views.latest_notification, name="latest_notification"),
 path("notifications/", views.notifications_list, name="notifications_list"),
    path("notifications/latest/", views.latest_notification, name="latest_notification"),
path("subscribe/<int:plan_id>/<int:appointment_id>/", views.subscribe, name="subscribe"),
    path("subscription-history/", views.subscription_history, name="subscription_history"),
path('weekly-progress/<int:student_id>/', views.weekly_progress, name='weekly_progress'),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)