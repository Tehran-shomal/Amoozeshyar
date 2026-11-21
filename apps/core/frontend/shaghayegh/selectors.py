from apps.core import models as m
from ..common import display, enrollment_rows, enrollments_table, table, form_for
from .forms import GradeAppealForm


def build(slug, student, term, request):
    if slug == "grade-appeal":
        rows = m.GradeAppeal.objects.filter(enrollment__student=student, enrollment__offering__term=term).select_related("enrollment__offering__lesson", "appeal_status")
        return {"form": form_for(GradeAppealForm, request, student, term), "tables": [
            table("پیگیری اعتراض‌ها", ["درس", "دلیل", "تاریخ", "وضعیت"],
                  ((x.enrollment.offering.lesson.title, x.appeal_reason, x.appeal_date, x.appeal_status) for x in rows))]}
    if slug in {"add-drop", "emergency-drop"}:
        # Only active enrollments get a real record ID and a drop action.
        rows = list(enrollment_rows(student, term).exclude(
            status__code__in=["dropped", "cancelled", "withdrawn"]))
        courses = table("انتخاب درس‌ها", ["نام درس", "کد درس", "واحد", "استاد",
            "زمان برگزاری", "زمان امتحان", "عملیات"], [])
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
                    offer.teacher.person.full_name, schedule, exam_time],
            })
        return {"course_change_table": courses, "course_change_units": total_units,
            "course_change_debt": display(student.tuition_debt)}

    data = {"tables": [enrollments_table(student, term)]}
    if slug == "add-drop":
        data["links"] = [("enrollment", "افزودن درس")]
    return data
