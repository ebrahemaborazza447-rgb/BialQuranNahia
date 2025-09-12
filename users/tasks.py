# users/tasks.py
from .models import Exam, GoogleFormResult
from .google_sheets import fetch_google_form_results, fetch_and_store_entries
def sync_google_form_job():
    exams = Exam.objects.exclude(google_sheet_url__isnull=True).exclude(google_sheet_url="")
    for exam in exams:
        new_entries = fetch_and_store_entries(exam)
        print(f"🔄 {exam.title} - تمت إضافة {len(new_entries)} نتيجة")
