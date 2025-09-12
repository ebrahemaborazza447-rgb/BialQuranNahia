# users/google_sheets.py
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
import os
from pathlib import Path
from django.utils import timezone
from .models import GoogleFormResult

BASE_DIR = Path(__file__).resolve().parent.parent
CREDS_FILE = os.path.join(BASE_DIR, "ecommerce/service_account_new.json")

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/drive.readonly",
]

creds = Credentials.from_service_account_file(CREDS_FILE, scopes=SCOPES)
client = gspread.authorize(creds)


def fetch_google_form_results(sheet_id, worksheet_index=0):
    """ يرجع كل الصفوف من Google Sheet كـ list of dicts """
    try:
        ws = client.open_by_key(sheet_id).get_worksheet(worksheet_index)
        return ws.get_all_records()
    except Exception as e:
        print(f"❌ Sheet error: {e}")
        return []


def fetch_and_store_entries(exam, worksheet_index=0):
    """ يجلب البيانات من Google Sheets ويخزن آخر رد لكل إيميل فقط """
    sheet_id = exam.sheet_id
    if not sheet_id:
        print(f"❌ مفيش sheet_id للامتحان: {exam.title}")
        return []

    try:
        ws = client.open_by_key(sheet_id).get_worksheet(worksheet_index)
        rows = ws.get_all_values()
    except Exception as e:
        print(f"❌ Sheet error for {exam.title}: {e}")
        return []

    if not rows or len(rows) < 2:
        return []

    headers = rows[0]
    records = rows[1:]

    EMAIL_KEYS = ["email", "بريد", "عنوان البريد", "البريد الإلكتروني"]
    DATE_KEYS = ["date", "timestamp", "time", "تاريخ", "الطابع الزمني", "وقت", "طابع زمني"]
    SCORE_KEYS = ["score", "نتيجة", "النتيجة", "درجة"]

    def find_col(keys):
        for i, h in enumerate(headers):
            h_norm = (h or "").strip().casefold()
            if any(k in h_norm for k in [k.casefold() for k in keys]):
                return i
        return None

    email_col = find_col(EMAIL_KEYS)
    date_col = find_col(DATE_KEYS)
    score_col = find_col(SCORE_KEYS)

    objs = []
    for row in records:
        row = list(row) + [""] * (len(headers) - len(row))

        email = row[email_col] if email_col is not None else None
        score = row[score_col] if score_col is not None else ""

        form_date_raw = row[date_col] if date_col is not None else ""
        parsed_date = None
        for fmt in (
            "%Y-%m-%d %H:%M:%S",
            "%d/%m/%Y %H:%M:%S",
            "%Y-%m-%d",
            "%d/%m/%Y",
            "%I:%M:%S %p %Y/%m/%d",  # 3:15:51 PM 2025/09/06
        ):
            try:
                form_date_clean = (
                    form_date_raw.replace("م", "PM")
                                 .replace("ص", "AM")
                                 .strip()
                )
                parsed_date = datetime.strptime(form_date_clean, fmt)
                break
            except Exception:
                continue

        if not email or not parsed_date:
            continue

        if timezone.is_naive(parsed_date):
            parsed_date = timezone.make_aware(parsed_date, timezone.get_current_timezone())

        objs.append(GoogleFormResult(
            exam=exam,
            email=email,
            score=score or "",
            form_date=parsed_date,
            answers=dict(zip(headers, row))
        ))

    # ✅ آخر رد فقط لكل إيميل
    if objs:
        latest_results = {}

        for obj in objs:
            if obj.email not in latest_results:
                latest_results[obj.email] = obj
            else:
                if obj.form_date and latest_results[obj.email].form_date:
                    if obj.form_date > latest_results[obj.email].form_date:
                        latest_results[obj.email] = obj
                else:
                    if obj.submitted_at > latest_results[obj.email].submitted_at:
                        latest_results[obj.email] = obj

        GoogleFormResult.objects.bulk_create(
            list(latest_results.values()),
            ignore_conflicts=True
        )
        print(f"✅ {exam.title} - تمت إضافة {len(latest_results)} نتيجة (آخر رد لكل إيميل فقط)")

        return list(latest_results.values())

    return []
