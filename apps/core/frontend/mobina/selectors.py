"""داده‌های واقعی داشبورد و انتخاب واحد؛ شناسهٔ ارائه مستقیم به API فرستاده می‌شود."""
from apps.core import models as m
from ..common import display, active_enrollment_rows
from .forms import SettingsForm


def build(slug, student, term, request):
    if slug == "settings":
        return {"form": SettingsForm(
            request.POST if request.method == "POST" else None,
            student=student,
            person=request.user,
            term=term,
        ), "settings_save_result": (
            request.method == "GET" and request.GET.get("settings_saved") == "1"
        ), "notification_categories": [
            "اطلاعیه‌های آموزشی",
            "مهلت‌ها و پرداخت شهریه",
            "پیام و اطلاعیه استاد",
            "وضعیت درخواست‌ها",
        ]}
    if slug == "student-card":
        return {"printable": True}
    return {"notice": "از منوی سامانه بخش موردنظر را انتخاب کنید."}


def dashboard(student, term, person):
    details = [("شماره دانشجویی", student.student_code), ("رشته", student.field.field_name),
               ("مقطع", display(student.educational_level))] if student else []
    classes = []
    if student:
        for row in active_enrollment_rows(student, term):
            offer = row.offering
            classes.append({"day_time": f"{offer.day_of_week or ''} {offer.start_time:%H:%M}",
                "name": offer.lesson.title, "teacher": offer.teacher.person.full_name,
                "room": f"{offer.classroom.building_name} / {offer.classroom.room_number}"})
    notices = m.Notification.objects.filter(user__person=person).order_by("-created_at")[:5]
    financial_summary = []
    if student:
        debt = student.tuition_debt or 0
        debt_is_clear = debt == 0
        financial_summary.append({
            "label": "بدهی شهریه",
            "value": f"{int(debt):,} ریال",
            "status": "تسویه" if debt_is_clear else "بدهی دارد",
            "state": "success" if debt_is_clear else "warning",
        })

        payment = (
            m.Payment.objects.filter(student=student, term=term)
            .select_related("status")
            .order_by("-payment_date", "-pk")
            .first()
            if term
            else None
        )
        if payment:
            payment_succeeded = bool(payment.status_id and payment.status.code == "successful")
            financial_summary.append({
                "label": "پرداخت خدمات آموزشی",
                "value": f"{payment.amount:,.0f} ریال",
                "status": payment.status.label if payment.status_id else "وضعیت نامشخص",
                "state": "success" if payment_succeeded else "warning",
            })
        else:
            financial_summary.append({
                "label": "پرداخت خدمات آموزشی",
                "value": "—",
                "status": "پرداختی ثبت نشده",
                "state": "muted",
            })

    return {"welcome": f"{person.full_name}، خوش آمدید", "intro": "خدمات آموزشی و دانشجویی",
        "university": "دانشگاه آزاد اسلامی", "student_details": details,
        "quick_actions": [{"slug": s, "title": t, "icon": i} for s,t,i in [
            ("enrollment", "انتخاب واحد", "+"), ("transcript", "کارنامه", "▤"),
            ("tuition", "وضعیت مالی", "◈"), ("requests", "درخواست‌ها", "✉")]],
        "classes_title": "برنامهٔ کلاس‌ها", "classes_link": "مشاهده برنامه", "classes": classes,
        "classes_columns": ["زمان", "درس", "استاد", "کلاس"],
        "notices_title": "اعلان‌ها", "notices_link": "مشاهده همه",
        "notices": [{"title": x.title, "date": display(x.created_at)} for x in notices],
        "academic_title": "وضعیت تحصیلی", "academic_link": "مشاهده کارنامه", "academic_average_label": "معدل کل",
        "academic_summary": [("معدل کل", display(student.total_gpa)), ("واحد گذرانده", student.passed_units),
                             ("وضعیت", display(student.status))] if student else [],
        "financial_title": "وضعیت مالی", "financial_link": "سوابق پرداخت",
        "financial_summary": financial_summary,
        "financial_note": "مبالغ و وضعیت پرداخت از اطلاعات همین نیمسال خوانده می‌شود."}
