"""Student-scoped schedule and class selectors for Niousha."""

from datetime import date, datetime, timedelta

from apps.core import models as m
from django.utils import timezone

from ..common import active_enrollment_rows, display, table, term_code_display


_JALALI_MONTHS = (
    "فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور",
    "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند",
)
_PERSIAN_DIGITS = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")
_WEEKDAY_CODES = (
    "saturday", "sunday", "monday", "tuesday", "wednesday", "thursday", "friday"
)


def _gregorian_to_jalali(value):
    """Convert a Gregorian date to Jalali for the calendar's Persian UI."""
    gy, gm, gd = value.year, value.month, value.day
    month_offsets = (0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334)
    if gy > 1600:
        jy, gy = 979, gy - 1600
    else:
        jy, gy = 0, gy - 621
    gy2 = gy + 1 if gm > 2 else gy
    days = (
        365 * gy + (gy2 + 3) // 4 - (gy2 + 99) // 100
        + (gy2 + 399) // 400 - 80 + gd + month_offsets[gm - 1]
    )
    jy += 33 * (days // 12053)
    days %= 12053
    jy += 4 * (days // 1461)
    days %= 1461
    if days > 365:
        jy += (days - 1) // 365
        days = (days - 1) % 365
    if days < 186:
        jm, jd = 1 + days // 31, 1 + days % 31
    else:
        jm, jd = 7 + (days - 186) // 30, 1 + (days - 186) % 30
    return jy, jm, jd


def _calendar_event(title, value, detail=""):
    if value is None:
        return None
    if isinstance(value, datetime):
        local_value = timezone.localtime(value) if timezone.is_aware(value) else value
        event_date = local_value.date()
        time_label = local_value.strftime("%H:%M")
    else:
        event_date = value
        time_label = ""
    jalali_year, jalali_month, jalali_day = _gregorian_to_jalali(event_date)
    jalali_label = f"{jalali_year:04d}/{jalali_month:02d}/{jalali_day:02d}"
    return {
        "date": event_date,
        "iso_date": event_date.isoformat(),
        "date_label": jalali_label.translate(_PERSIAN_DIGITS),
        "time_label": time_label,
        "title": title,
        "detail": detail,
    }


def _calendar_window(start, end):
    if not start or not end:
        return "ثبت نشده"
    start_event = _calendar_event("", start)
    end_event = _calendar_event("", end)
    return f"{start_event['date_label']} تا {end_event['date_label']}"


def _calendar_page(student, term):
    if not term:
        return {"notice": "نیمسال تحصیلی ثبت نشده است."}

    today = timezone.localdate()
    month_date = today if term.start_date <= today <= term.end_date else term.start_date
    jalali_year, jalali_month, _ = _gregorian_to_jalali(month_date)
    calendar_start = month_date
    for _ in range(32):
        year, month, day = _gregorian_to_jalali(calendar_start)
        if (year, month, day) == (jalali_year, jalali_month, 1):
            break
        calendar_start -= timedelta(days=1)
    calendar_end = calendar_start
    while True:
        next_day = calendar_end + timedelta(days=1)
        if _gregorian_to_jalali(next_day)[:2] != (jalali_year, jalali_month):
            break
        calendar_end = next_day
    days_in_month = (calendar_end - calendar_start).days + 1
    leading_cells = (calendar_start.weekday() + 2) % 7

    events = [
        _calendar_event("شروع نیمسال", term.start_date),
        _calendar_event("پایان نیمسال", term.end_date),
        _calendar_event("آغاز انتخاب واحد", term.registration_start),
        _calendar_event("پایان مهلت انتخاب واحد", term.registration_end),
        _calendar_event("آغاز حذف و اضافه", term.add_drop_start),
        _calendar_event("پایان حذف و اضافه", term.add_drop_end),
        _calendar_event("آغاز حذف اضطراری", term.emergency_drop_start),
        _calendar_event("پایان حذف اضطراری", term.emergency_drop_end),
    ]

    enrollments = list(active_enrollment_rows(student, term).select_related(
        "offering__lesson"
    ).order_by("offering__exam_date", "offering__lesson__title", "pk"))
    enrollment_ids = [row.pk for row in enrollments]
    exam_dates = []
    for enrollment in enrollments:
        exam_date = enrollment.offering.exam_date
        if exam_date:
            exam_dates.append(exam_date)
            events.append(_calendar_event(
                f"امتحان {enrollment.offering.lesson.title}", exam_date,
                enrollment.offering.exam_time.strftime("%H:%M")
                if enrollment.offering.exam_time else "",
            ))

    if enrollment_ids:
        sessions = m.Attendance.objects.filter(
            enrollment_id__in=enrollment_ids,
            session_date__gte=calendar_start,
            session_date__lte=calendar_end,
        ).select_related("enrollment__offering__lesson").order_by(
            "session_date", "session_number", "pk"
        )
        for session in sessions:
            events.append(_calendar_event(
                f"جلسهٔ درس {session.enrollment.offering.lesson.title}",
                session.session_date,
                f"جلسهٔ {session.session_number}",
            ))

    events = [event for event in events if event]
    month_events = sorted(
        (event for event in events if calendar_start <= event["date"] <= calendar_end),
        key=lambda event: (event["date"], event["time_label"], event["title"]),
    )
    event_dates = {event["date"] for event in month_events}
    calendar_days = [None] * leading_cells
    for offset in range(days_in_month):
        day_date = calendar_start + timedelta(days=offset)
        _, _, day_number = _gregorian_to_jalali(day_date)
        calendar_days.append({
            "number": str(day_number).translate(_PERSIAN_DIGITS),
            "iso_date": day_date.isoformat(),
            "is_event_day": day_date in event_dates,
            "is_today": day_date == today,
        })
    calendar_days.extend([None] * ((-len(calendar_days)) % 7))

    now = timezone.now()
    upcoming_deadlines = [
        (_calendar_event("پایان مهلت انتخاب واحد", term.registration_end), term.registration_end),
        (_calendar_event("پایان حذف و اضافه", term.add_drop_end), term.add_drop_end),
        (_calendar_event("پایان حذف اضطراری", term.emergency_drop_end), term.emergency_drop_end),
    ]
    upcoming_deadlines = [
        (event, value) for event, value in upcoming_deadlines
        if event and value >= now
    ]
    next_deadline = min(upcoming_deadlines, key=lambda item: item[1])[0] if upcoming_deadlines else None

    exam_range = (
        f"{_calendar_event('', min(exam_dates))['date_label']} تا "
        f"{_calendar_event('', max(exam_dates))['date_label']}"
        if exam_dates else "زمان امتحانی ثبت نشده"
    )
    term_range = _calendar_window(term.start_date, term.end_date)
    registration_range = _calendar_window(term.registration_start, term.registration_end)
    add_drop_range = _calendar_window(term.add_drop_start, term.add_drop_end)
    emergency_drop_range = _calendar_window(term.emergency_drop_start, term.emergency_drop_end)

    return {
        "calendar_month_label": (
            f"{_JALALI_MONTHS[jalali_month - 1]} {str(jalali_year).translate(_PERSIAN_DIGITS)}"
        ),
        "calendar_days": calendar_days,
        "calendar_events": month_events,
        "calendar_term_code": term_code_display(term),
        "calendar_term_range": term_range,
        "calendar_next_deadline": next_deadline,
        "calendar_summary": [
            ("بازهٔ نیمسال", term_range),
            ("بازه انتخاب واحد", registration_range),
            ("حذف و اضافه", add_drop_range),
            ("حذف اضطراری", emergency_drop_range),
            ("بازه امتحانات", exam_range),
        ],
    }


def _schedule_page(student, term):
    enrollments = list(active_enrollment_rows(student, term).select_related(
        "status", "offering__day_of_week", "offering__lesson",
        "offering__teacher__person", "offering__classroom",
    ).order_by("offering__start_time", "offering__end_time", "pk"))

    day_labels = dict(m.Constant.objects.filter(
        category="day_of_week", is_active=True
    ).values_list("code", "label"))
    used_day_codes = set()
    slot_courses = {}
    unassigned = []
    offerings = []
    total_units = 0

    for enrollment in enrollments:
        offering = enrollment.offering
        offerings.append(offering)
        total_units += (offering.lesson.theory_units or 0) + (offering.lesson.practical_units or 0)
        course = {
            "lesson": offering.lesson.title,
            "teacher": offering.teacher.person.full_name,
            "room": str(offering.classroom),
        }
        day = offering.day_of_week
        if day is None:
            unassigned.append({
                **course,
                "start_time": offering.start_time,
                "end_time": offering.end_time,
            })
            continue

        day_labels[day.code] = day.label
        used_day_codes.add(day.code)
        slot = slot_courses.setdefault(
            (offering.start_time, offering.end_time), {}
        )
        slot.setdefault(day.code, []).append(course)

    day_codes = [code for code in _WEEKDAY_CODES[:-1] if code in day_labels]
    if "friday" in used_day_codes:
        day_codes.append("friday")
    day_codes.extend(sorted(
        used_day_codes - set(_WEEKDAY_CODES), key=lambda code: day_labels[code]
    ))
    days = [{"code": code, "label": day_labels[code]} for code in day_codes]

    time_slots = sorted(slot_courses)
    schedule_slots = [
        {
            "start_time": start,
            "end_time": end,
            "cells": [
                {"courses": slot_courses[(start, end)].get(day["code"], [])}
                for day in days
            ],
        }
        for start, end in time_slots
    ]

    has_conflicts = any(
        left.day_of_week_id is not None
        and left.day_of_week_id == right.day_of_week_id
        and left.start_time < right.end_time
        and left.end_time > right.start_time
        for index, left in enumerate(offerings)
        for right in offerings[index + 1:]
    )

    return {
        "schedule_summary": {
            "term": term_code_display(term),
            "units": total_units,
            "sessions": len(enrollments),
            "has_conflicts": has_conflicts,
            "conflict_label": "تداخل ثبت‌شده" if has_conflicts else "بدون تداخل",
        },
        "schedule_days": days,
        "schedule_slots": schedule_slots,
        "schedule_unassigned": unassigned,
        "schedule_column_count": len(days) + 1,
        "printable": True,
    }


def build(slug, student, term, request):
    if slug == "attendance":
        enrollments = list(active_enrollment_rows(student, term).select_related(
            "status", "offering__lesson", "offering__teacher__person"
        ).order_by("offering__lesson__title", "pk"))
        enrollment_ids = [row.pk for row in enrollments]
        attendance_records = list(m.Attendance.objects.filter(
            enrollment_id__in=enrollment_ids
        ).select_related("attendance_status").order_by(
            "session_number", "session_date", "pk"
        )) if enrollment_ids else []
        records_by_enrollment = {enrollment_id: [] for enrollment_id in enrollment_ids}
        totals = {"present": 0, "absent": 0, "late": 0, "unclassified": 0}
        for record in attendance_records:
            records_by_enrollment[record.enrollment_id].append(record)
            code = record.attendance_status.code.casefold() if record.attendance_status else ""
            if code in totals and code != "unclassified":
                totals[code] += 1
            else:
                totals["unclassified"] += 1

        course_rows = []
        for enrollment in enrollments:
            records = records_by_enrollment[enrollment.pk]
            counts = {"present": 0, "absent": 0, "late": 0, "unclassified": 0}
            for record in records:
                code = record.attendance_status.code.casefold() if record.attendance_status else ""
                if code in counts and code != "unclassified":
                    counts[code] += 1
                else:
                    counts["unclassified"] += 1
            course_rows.append({
                "enrollment_id": enrollment.pk,
                "lesson": enrollment.offering.lesson.title,
                "teacher": enrollment.offering.teacher.person.full_name,
                "session_count": len(records),
                "present_count": counts["present"],
                "absent_count": counts["absent"],
                "late_count": counts["late"],
                "unclassified_count": counts["unclassified"],
                "enrollment_status": enrollment.status.label if enrollment.status else "—",
            })

        last_updated = max(
            (record.created_at for record in attendance_records), default=None
        )
        return {
            "attendance_rows": course_rows,
            "attendance_term": term_code_display(term),
            "attendance_active_course_count": len(enrollments),
            "attendance_active_units": sum(
                enrollment.offering.lesson.theory_units
                + enrollment.offering.lesson.practical_units
                for enrollment in enrollments
            ),
            "attendance_session_count": len(attendance_records),
            "attendance_present_count": totals["present"],
            "attendance_absence_count": totals["absent"],
            "attendance_late_count": totals["late"],
            "attendance_unclassified_count": totals["unclassified"],
            "attendance_last_updated": display(last_updated),
        }

    if slug == "exam-card":
        active_enrollments = active_enrollment_rows(student, term)
        evaluated_ids = m.TeacherSurvey.objects.filter(
            enrollment__in=active_enrollments
        ).values_list("enrollment_id", flat=True)
        unfinished_evaluation = active_enrollments.exclude(pk__in=evaluated_ids).exists()
        exam_enrollments = active_enrollments.select_related(
            "status", "offering__lesson", "offering__classroom", "offering__term"
        ).order_by("offering__exam_date", "offering__exam_time", "offering__lesson__lesson_code")
        blockers = []
        if student.tuition_debt and student.tuition_debt > 0:
            blockers.append(
                f"بدهی شهریهٔ {student.tuition_debt:,.0f} ریال در پرونده ثبت شده است."
            )
        if unfinished_evaluation:
            blockers.append("ارزشیابی یک یا چند درس تکمیل نشده است.")
        if exam_enrollments.filter(offering__exam_date__isnull=True).exists():
            blockers.append("زمان امتحان یک یا چند درس هنوز در سامانه ثبت نشده است.")
        return {
            "exam_card": {"enrollments": exam_enrollments, "blockers": blockers},
            "printable": True,
        }

    if slug == "schedule":
        return _schedule_page(student, term)

    if slug == "calendar":
        return _calendar_page(student, term)

    if not term:
        return {"notice": "نیمسال تحصیلی ثبت نشده است."}
    return {"facts": [("نیمسال", str(term)), ("کد", term.term_code)], "tables": [table(
        "تقویم نیمسال", ["بازه", "شروع", "پایان"], [
            ("نیمسال", term.start_date, term.end_date),
            ("انتخاب واحد", term.registration_start, term.registration_end),
            ("حذف و اضافه", term.add_drop_start, term.add_drop_end),
            ("حذف اضطراری", term.emergency_drop_start, term.emergency_drop_end),
        ],
    )]}
