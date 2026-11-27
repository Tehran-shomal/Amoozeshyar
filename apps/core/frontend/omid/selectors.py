"""Student-scoped academic history and progress selectors for Omid."""

from django.db.models import Prefetch

from apps.core import models as m
from apps.core.enrollment.services import PASSING_GRADE, active_enrollments
from ..common import active_enrollment_rows, display, form_for, table, term_code_display
from .forms import GradeAppealForm


def build(slug, student, term, request):
    if slug == "grade-appeal":
        rows = m.GradeAppeal.objects.filter(
            enrollment__student=student, enrollment__offering__term=term
        ).select_related("enrollment__offering__lesson", "appeal_status")
        raw_request_id = request.GET.get("request_id", "")
        try:
            request_id = int(raw_request_id)
        except (TypeError, ValueError):
            request_id = None
        appeal = (
            rows.filter(pk=request_id).first()
            if request_id and 0 < request_id <= 9_223_372_036_854_775_807
            else None
        )
        operation_result = None
        if appeal:
            operation_result = {
                "heading": "اعتراض به نمره ثبت شد",
                "message": f"درخواست اعتراض برای درس «{appeal.enrollment.offering.lesson.title}» ثبت شد.",
                "status": display(appeal.appeal_status),
                "created_at": display(appeal.appeal_date),
                "note": "درخواست برای رسیدگی ثبت شده است؛ این ثبت به معنی تغییر نمره یا تأیید اعتراض نیست.",
            }
        return {
            "form": form_for(GradeAppealForm, request, student, term),
            "notice": (
                "مهلت مجاز اعتراض در مدل/API فعلی بررسی نمی‌شود و فرم امکان پیوست فایل ندارد؛ "
                "پیش از ثبت، مهلت را از آموزش تأیید کنید."
            ),
            "operation_result": operation_result,
            "tables": [table(
                "پیگیری اعتراض‌ها", ["درس", "دلیل", "تاریخ", "وضعیت"],
                ((row.enrollment.offering.lesson.title, row.appeal_reason,
                  row.appeal_date, row.appeal_status) for row in rows),
            )],
        }

    if slug == "curriculum":
        curriculum = list(m.Curriculum.objects.filter(
            field=student.field, is_active=True
        ).select_related("lesson", "requirement_type").order_by(
            "recommended_term", "lesson__lesson_code"
        ))
        lesson_ids = [row.lesson_id for row in curriculum]
        passed_lesson_ids = set(active_enrollments(m.Enrollment.objects.filter(
            student=student
        )).filter(
            offering__lesson_id__in=lesson_ids,
            grades__score__gte=PASSING_GRADE,
        ).values_list("offering__lesson_id", flat=True).distinct())
        current_lesson_ids = set()
        if term:
            current_lesson_ids = set(active_enrollment_rows(student, term).filter(
                offering__is_active=True,
                offering__lesson_id__in=lesson_ids,
            ).values_list("offering__lesson_id", flat=True).distinct())

        prerequisite_map = {}
        prerequisites = m.Prerequisite.objects.filter(
            lesson_id__in=lesson_ids
        ).select_related("prerequisite_lesson", "prerequisite_type")
        for prerequisite in prerequisites:
            label = prerequisite.prerequisite_lesson.title
            if prerequisite.prerequisite_type_id:
                label = f"{prerequisite.prerequisite_type.label}: {label}"
            prerequisite_map.setdefault(prerequisite.lesson_id, []).append(label)

        curriculum_rows = []
        passed_units = current_units = 0
        for row in curriculum:
            is_passed = row.lesson_id in passed_lesson_ids
            is_current = not is_passed and row.lesson_id in current_lesson_ids
            if is_passed:
                status, status_code = "گذرانده", "passed"
                passed_units += row.calculated_units
            elif is_current:
                status, status_code = "جاری", "current"
                current_units += row.calculated_units
            else:
                status, status_code = "باقی‌مانده", "remaining"
            curriculum_rows.append({
                "lesson": row.lesson.title,
                "units": row.calculated_units,
                "prerequisites": prerequisite_map.get(row.lesson_id, []),
                "status": status,
                "status_code": status_code,
                "group": display(row.requirement_type),
            })

        total_units = sum(row.calculated_units for row in curriculum)
        return {
            "curriculum_rows": curriculum_rows,
            "curriculum_summary": {
                "total": total_units,
                "passed": passed_units,
                "current": current_units,
                "remaining": max(total_units - passed_units - current_units, 0),
            },
        }

    if slug == "transcript":
        enrollments = list(
            active_enrollment_rows(student, term)
            .select_related("offering__lesson", "status")
            .prefetch_related(Prefetch(
                "grades",
                queryset=m.Grade.objects.filter(score__isnull=False).order_by("-pk"),
                to_attr="recorded_grades",
            ))
        )
        transcript_rows = []
        for enrollment in enrollments:
            score = enrollment.recorded_grades[0].score if enrollment.recorded_grades else None
            transcript_rows.append({
                "lesson_code": enrollment.offering.lesson.lesson_code,
                "lesson": enrollment.offering.lesson.title,
                "units": (
                    enrollment.offering.lesson.theory_units
                    + enrollment.offering.lesson.practical_units
                ),
                "score": display(score) if score is not None else "ثبت نشده",
                "status": display(enrollment.status),
            })
        current_units = sum(row["units"] for row in transcript_rows)
        return {
            "current_units": current_units,
            "transcript_summary": [
                ("واحدهای این نیمسال", current_units),
                ("معدل کل ثبت‌شده", display(student.total_gpa)),
                ("واحد گذرانده", student.passed_units),
                ("وضعیت تحصیلی", display(student.status)),
            ],
            "transcript_rows": transcript_rows,
            "notice": (
                "مدل نمره میان‌ترم و پایان‌ترم را جدا نمی‌کند و معدل اختصاصی این نیمسال "
                "در داده‌های فعلی قابل محاسبه نیست."
            ),
        }

    if slug == "academic-activities":
        active_enrollments = list(
            active_enrollment_rows(student, term).select_related("offering__lesson")
        )
        changes = m.EducationalChangeLog.objects.filter(student=student).select_related(
            "change_type"
        ).order_by("-changed_at")[:8]
        return {
            "page_subtitle": (
                f"نیمسال {term_code_display(term)} • {student.person.full_name} • اطلاعات ثبت‌شده"
            ),
            "activity_summary": [
                ("درس‌های ثبت‌شده", len(active_enrollments)),
                ("واحدهای فعال", sum(
                    row.offering.lesson.theory_units + row.offering.lesson.practical_units
                    for row in active_enrollments
                )),
                ("وضعیت دانشجو", display(student.status)),
            ],
            "recent_activities": changes,
            "activity_links": [
                {"slug": "schedule", "title": "برنامه هفتگی کامل", "text": "نمایش برنامهٔ نیمسال"},
                {"slug": "attendance", "title": "حضور و غیاب درس‌ها", "text": "وضعیت حضور در کلاس‌ها"},
                {"slug": "exam-card", "title": "کارت ورود به جلسه امتحان", "text": "برنامهٔ امتحانات"},
                {"slug": "calendar", "title": "تقویم آموزشی ترم", "text": "مهلت‌های ثبت‌نام و امتحان"},
            ],
        }

    return {"notice": "از منوی سامانه بخش موردنظر را انتخاب کنید."}
