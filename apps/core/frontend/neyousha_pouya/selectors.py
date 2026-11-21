from apps.core import models as m
from ..common import table, display, form_for, enrollment_rows
from .forms import InternshipForm, SettingsForm


def build(slug, student, term, request):
    if slug == "internship":
        rows = m.Internship.objects.filter(student=student).select_related("status")
        return {"form": form_for(InternshipForm, request, student, term), "tables": [table(
            "پیگیری کارآموزی", ["سازمان", "شروع", "ساعت", "وضعیت"],
            ((x.company_name, x.intern_start_date, x.duration_hours, x.status) for x in rows))]}
    if slug in {"notifications", "announcements"}:
        rows = m.Notification.objects.filter(user__person=request.user).order_by("-created_at")
        return {"notifications": rows, "notice": "اعلان‌های حساب شما"}
    if slug == "settings":
        return {"form": SettingsForm(request.POST if request.method == "POST" else None,
                                     student=student, person=request.user, term=term)}
    if slug == "schedule":
        rows = enrollment_rows(student, term).exclude(status__code__in=["dropped", "cancelled", "withdrawn"])
        return {"printable": True, "tables": [table("برنامه هفتگی", ["درس", "استاد", "روز", "شروع", "پایان", "کلاس"],
            ((x.offering.lesson.title, x.offering.teacher.person.full_name, x.offering.day_of_week,
              x.offering.start_time, x.offering.end_time, x.offering.classroom) for x in rows))]}
    if not term:
        return {"notice": "نیمسال تحصیلی ثبت نشده است."}
    return {"facts": [("نیمسال", str(term)), ("کد", term.term_code)], "tables": [table(
        "تقویم نیمسال", ["بازه", "شروع", "پایان"], [
            ("نیمسال", term.start_date, term.end_date),
            ("انتخاب واحد", term.registration_start, term.registration_end),
            ("حذف و اضافه", term.add_drop_start, term.add_drop_end),
            ("حذف اضطراری", term.emergency_drop_start, term.emergency_drop_end)])]}
