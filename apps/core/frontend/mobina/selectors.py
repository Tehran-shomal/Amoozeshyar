"""داده‌های واقعی داشبورد و انتخاب واحد؛ شناسهٔ ارائه مستقیم به API فرستاده می‌شود."""
from apps.core import models as m
from ..common import table, display, enrollments_table, active_enrollment_rows


def build(slug, student, term, request):
    # Step one confirms the live student/term record before opening course selection.
    if slug == "enrollment":
        return {"enrollment_can_continue": bool(term)}
    if slug == "curriculum":
        return {"tables": [table("چارت انتخاب واحد", ["درس", "نوع", "ترم پیشنهادی", "واحد"],
            ((x.lesson.title, x.requirement_type, x.recommended_term, x.calculated_units)
             for x in m.Curriculum.objects.filter(field=student.field, is_active=True).select_related("lesson", "requirement_type")))]}
    offers = m.CourseOffering.objects.filter(term=term, is_active=True).select_related("lesson", "teacher__person", "day_of_week", "classroom") if term else []
    available = table("دروس ارائه‌شده", ["کد", "درس", "استاد", "واحد", "زمان", "ظرفیت باقی‌مانده"], [])
    available["has_actions"] = True
    for offer in offers:
        available["rows"].append({"cells": [offer.lesson.lesson_code, offer.lesson.title,
            offer.teacher.person.full_name, offer.lesson.theory_units+offer.lesson.practical_units,
            f"{offer.day_of_week or ''} {offer.start_time:%H:%M}–{offer.end_time:%H:%M}", offer.remaining_capacity],
            "id": offer.pk, "action": "register", "action_label": "انتخاب درس"})
    selected = active_enrollment_rows(student, term)
    selected_units = sum(row.offering.lesson.theory_units + row.offering.lesson.practical_units
                         for row in selected)
    return {"tables": [enrollments_table(student, term, queryset=selected), available],
            "selected_units": selected_units, "available_offerings": offers}


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
