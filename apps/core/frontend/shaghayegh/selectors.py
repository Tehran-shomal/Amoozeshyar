from ..common import active_enrollment_rows, display, enrollments_table, table
from apps.core import models as m
from apps.core.enrollment.services import maximum_allowed_units


def build(slug, student, term, request):
    if slug == "enrollment":
        return {"enrollment_can_continue": bool(term)}
    if slug == "selected-courses":
        available = table(
            "دروس ارائه‌شده", ["کد", "درس", "استاد", "واحد", "زمان", "ظرفیت باقی‌مانده"], []
        )
        available["has_actions"] = True
        selected = list(active_enrollment_rows(student, term))
        selected_units = sum(
            row.offering.lesson.theory_units + row.offering.lesson.practical_units
            for row in selected
        )
        selected_table = table(
            "دروس ثبت‌نام‌شده",
            ["نام درس", "کد درس", "واحد", "استاد", "زمان برگزاری", "زمان امتحان", "وضعیت"],
            [],
        )
        for row in selected:
            offering = row.offering
            exam_time = "—"
            if offering.exam_date and offering.exam_time:
                exam_time = (
                    f"{display(offering.exam_date)} • "
                    f"{offering.exam_time.strftime('%H:%M')}"
                )
            selected_table["rows"].append({
                "cells": [
                    offering.lesson.title,
                    offering.lesson.lesson_code,
                    offering.lesson.theory_units + offering.lesson.practical_units,
                    offering.teacher.person.full_name,
                    f"{offering.day_of_week or ''} "
                    f"{offering.start_time:%H:%M}–{offering.end_time:%H:%M}",
                    exam_time,
                    display(row.status),
                ]
            })
        return {
            "tables": [selected_table, available],
            "selected_units": selected_units,
            "maximum_allowed_units": maximum_allowed_units(student),
            "tuition_breakdown_available": False,
        }
    if slug in {"add-drop", "emergency-drop"}:
        # Only active enrollments get a real record ID and a drop action.
        rows = list(active_enrollment_rows(student, term))
        available_offerings = table(
            "دروس ارائه‌شده",
            ["کد", "درس", "استاد", "واحد", "زمان", "ظرفیت باقی‌مانده"],
            [],
        )
        available_offerings["has_actions"] = True
        courses = table("انتخاب درس‌ها", ["نام درس", "کد درس", "واحد", "استاد",
            "زمان برگزاری", "زمان امتحان", "وضعیت", "عملیات"], [])
        courses["has_actions"] = True
        total_units = 0
        for row in rows:
            offer = row.offering
            units = offer.lesson.theory_units + offer.lesson.practical_units
            total_units += units
            schedule = f"{offer.day_of_week or ''} {offer.start_time:%H:%M}–{offer.end_time:%H:%M}"
            exam_time = f"{display(offer.exam_date)} • {display(offer.exam_time)}"
            courses["rows"].append({
                "id": row.pk,
                "action": "drop",
                "action_label": "حذف اضطراری" if slug == "emergency-drop" else "حذف درس",
                "course_name": offer.lesson.title,
                "course_code": offer.lesson.lesson_code,
                "units": units,
                "cells": [offer.lesson.title, offer.lesson.lesson_code, units,
                    offer.teacher.person.full_name, schedule, exam_time, display(row.status)],
            })
        raw_registration_id = request.GET.get("registration_id", "")
        try:
            registration_id = int(raw_registration_id)
        except (TypeError, ValueError):
            registration_id = None
        registration_result = (
            next((row for row in rows if row.pk == registration_id), None)
            if registration_id and 0 < registration_id <= 9_223_372_036_854_775_807
            else None
        )
        raw_dropped_id = request.GET.get("dropped_enrollment_id", "")
        try:
            dropped_id = int(raw_dropped_id)
        except (TypeError, ValueError):
            dropped_id = None
        drop_result = (
            m.Enrollment.objects.filter(
                pk=dropped_id,
                student=student,
                offering__term=term,
                status__code__iexact="dropped",
            ).select_related("status", "offering__lesson").first()
            if dropped_id and 0 < dropped_id <= 9_223_372_036_854_775_807
            else None
        )
        return {
            "course_change_table": courses,
            "course_offering_table": available_offerings,
            "course_change_units": total_units,
            "course_change_debt": display(student.tuition_debt),
            "maximum_allowed_units": maximum_allowed_units(student),
            "tuition_breakdown_available": False,
            "course_registration_result": registration_result,
            "course_drop_result": drop_result,
        }
    if slug == "registration-status":
        registrations = list(active_enrollment_rows(student, term))
        active_units = sum(
            row.offering.lesson.theory_units + row.offering.lesson.practical_units
            for row in registrations
        )
        debt = student.tuition_debt
        return {
            "registration_status_count": len(registrations),
            "registration_status_units": active_units,
            "registration_status_max_units": maximum_allowed_units(student),
            "registration_status_debt": debt,
            "registration_status_stages": [
                {
                    "stage": "بررسی اطلاعات دانشجو",
                    "status": "پرونده خوانده شد",
                    "description": "اطلاعات از Person و Student همین حساب نمایش داده شده است؛ تأیید هویت بیرونی ثبت نمی‌شود.",
                },
                {
                    "stage": "انتخاب درس‌ها",
                    "status": (
                        f"{len(registrations)} درس ثبت فعال"
                        if registrations else "ثبت فعالی وجود ندارد"
                    ),
                    "description": f"مجموع واحدهای ثبت فعال این نیمسال: {active_units}.",
                },
                {
                    "stage": "وضعیت شهریه",
                    "status": (
                        "بدهی ثبت‌شده در پرونده"
                        if debt > 0 else "بدهی در پرونده ثبت نشده"
                    ),
                    "description": (
                        f"ماندهٔ ثبت‌شده: {debt:,.0f} ریال."
                        if debt > 0 else
                        "پرونده بدهی ثبت‌شده ندارد؛ این به‌تنهایی رسید پرداخت یا تراکنش نیست."
                    ),
                },
                {
                    "stage": "تأیید نهایی",
                    "status": "وضعیت ثبت نشده",
                    "description": "تأیید نهایی در داده‌های فعلی ثبت نشده است؛ مدل گردش تأیید را نگه نمی‌دارد و نتیجه قابل استنتاج نیست.",
                },
            ],
        }

    data = {"tables": [enrollments_table(student, term)]}
    if slug == "add-drop":
        data["links"] = [("enrollment", "افزودن درس")]
    return data
