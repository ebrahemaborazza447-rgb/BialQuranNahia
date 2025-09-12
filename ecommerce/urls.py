"""
URL configuration for ecommerce project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from users import views
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth import views as auth_views
from users.views import logout_view
import json




urlpatterns = [
    path('signup/', views.signup_view, name="signup"),
    path('login', views.login_view, name="login"),
    path('profile/', views.profile_view, name='profile'),
    path('student_dashboard/', views.student_dashboard, name='student_dashboard'),
    path('', views.inbox, name='inbox'),
    path("inbox/", views.inbox, name="inbox"),

    path('contact/', views.contact, name='contact'),
    path('payment/', views.payment, name='payment'),
    path('payment_review/', views.payment_review, name='payment_review'),
    path('waiting_approval/', views.waiting_approval, name='waiting_approval'),
    path('check_approval/', views.check_approval_status, name='check_approval'),
    path('ajax/get_appointments/', views.get_appointments_by_phase, name='get_appointments_by_phase'),
    path('check_subscription/', views.check_subscription, name='check_subscription'),
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
    path("subscription-history/", views.subscription_history, name="subscription_history"),
path('weekly-progress/<int:student_id>/', views.weekly_progress, name='weekly_progress'),
path("subscribe/<int:plan_id>/", views.subscribe, name="subscribe"),
    path("accounts/", include("allauth.urls")),
# ecommerce/urls.py
path("sync-results/", views.sync_all_results_view, name="sync_results"),
  path("exams/", views.exam_list_view, name="exam_list"),
    path("exams/<int:pk>/", views.exam_detail_view, name="exam_detail"),
path('google-form/<int:exam_id>/', views.google_form, name='google_form'),
    path("exam-failed/<int:plan_id>/<int:exam_id>/", views.exam_failed, name="exam_failed"),
    path('update-profile/', views.update_profile, name="update_profile"),
    path('mark-read/<int:message_id>/', views.mark_as_read, name='mark_as_read'),
path('message_list/', views.message_list, name='message_list'),
    path('<int:message_id>/', views.message_detail, name='message_detail'),
    path('<int:message_id>/delete/', views.delete_message, name='delete_message'),
    path('send/', views.send_message, name='send_message'),
    path('unread-count/', views.get_unread_count, name='get_unread_count'),
    path('privacy/', views.privacy_view, name='privacy'),
    path('terms/', views.terms_view, name='terms'),
    path("about-me/", views.about_me, name="about_me"),
    path('faq/', views.faq_view, name='faq'),
path("faq/contact/", views.contact, name="faq_contact"),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)