from django.shortcuts import redirect
from django.urls import reverse
from .models import Subscription

def subscribe_required(subscribe_url="subscribe"):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect("login")  # لازم يسجل دخول الأول

            # هات آخر اشتراك للمستخدم (الأحدث)
            subscription = Subscription.objects.filter(user=request.user).order_by("-created_at").first()

            if not subscription:
                # مفيش اشتراك → رجعه على صفحة الاشتراك
                plan_id = kwargs.get("plan_id")
                if plan_id:
                    request.session["pending_plan_id"] = plan_id
                    return redirect(reverse(subscribe_url, kwargs={"plan_id": plan_id}))
                return redirect("subscribe_list")  # أو صفحة بتعرض الخطط

            # لو لقى اشتراك → وجّه حسب الحالة
            if subscription.status == "pending":
                return redirect("waiting_approval")
            elif subscription.status == "approved":
                return view_func(request, *args, **kwargs)  # يدخل عادي
            elif subscription.status == "rejected":
                return redirect("waiting_approval")  # أو صفحة تشرحله الرفض

            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
