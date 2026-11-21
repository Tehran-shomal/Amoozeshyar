"""Database-backed page contexts for Shahsavand's and Omid's routes."""

from django.db.models import Q

from apps.core import models as m
from ..common import display, enrollment_rows, form_for, table, term_code_display
from .forms import (
    CertificateForm,
    GraduationReviewForm,
    GuestRequestForm,
    MessageForm,
    ServiceRequestForm,
    SupportForm,
    SurveyForm,
)
from .pages import OMID_PAGES, SHAHSAVAND_PAGES


def _omid_page(slug, student, term, request):
    if slug in {"requests", "education-certificate", "graduation-certificate"}:
        rows = m.StudentServiceRequest.objects.filter(service_requester=student).select_related(
            "service_request_kind", "service_decision_state")
        form_class = ServiceRequestForm
        if slug != "requests":
            rows = rows.filter(service_request_kind__code="certificate")
            form_class = CertificateForm
        return {"form": form_for(form_class, request, student, term), "tables": [table(
            "پیگیری درخواست‌ها", ["شناسه", "نوع درخواست", "توضیحات", "وضعیت"],
            ((x.pk, x.service_request_kind, x.service_request_data, x.service_decision_state)
             for x in rows))]}

    if slug == "transcript":
        grades = m.Grade.objects.filter(
            enrollment__student=student, enrollment__offering__term=term
        ).select_related("enrollment__offering__lesson").order_by(
            "enrollment__offering__lesson__lesson_code")
        return {
            "transcript_summary": [
                ("معدل کل", display(student.total_gpa)),
                ("واحد گذرانده", student.passed_units),
                ("وضعیت تحصیلی", display(student.status)),
            ],
            "grades": grades,
        }

    if slug == "attendance":
        rows = m.Attendance.objects.filter(
            enrollment__student=student, enrollment__offering__term=term
        ).select_related("enrollment__offering__lesson", "attendance_status")
        return {"tables": [table("حضور و غیاب", ["درس", "جلسه", "تاریخ", "وضعیت", "توضیحات"],
            ((x.enrollment.offering.lesson.title, x.session_number, x.session_date,
              x.attendance_status, x.description) for x in rows))]}

    if slug == "academic-activities":
        active_enrollments = list(enrollment_rows(student, term).exclude(
            status__code__in=["dropped", "cancelled", "withdrawn"]
        ).select_related("offering__lesson"))
        changes = m.EducationalChangeLog.objects.filter(student=student).select_related(
            "change_type").order_by("-changed_at")[:8]
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

    if slug == "exam-card":
        active_enrollments = m.Enrollment.objects.filter(student=student)
        if term:
            active_enrollments = active_enrollments.filter(offering__term=term)
        else:
            active_enrollments = active_enrollments.none()
        active_enrollments = active_enrollments.exclude(
            status__code__in=["dropped", "cancelled", "withdrawn"])
        evaluated_ids = m.TeacherSurvey.objects.filter(
            enrollment__in=active_enrollments).values_list("enrollment_id", flat=True)
        unfinished_evaluation = active_enrollments.exclude(pk__in=evaluated_ids).exists()
        exam_enrollments = active_enrollments.select_related(
            "status", "offering__lesson", "offering__classroom", "offering__term"
        ).order_by("offering__exam_date", "offering__exam_time", "offering__lesson__lesson_code")
        blockers = []
        if student.tuition_debt and student.tuition_debt > 0:
            blockers.append("بدهی شهریه در پرونده ثبت شده است.")
        if unfinished_evaluation:
            blockers.append("ارزشیابی یک یا چند درس تکمیل نشده است.")
        if exam_enrollments.filter(offering__exam_date__isnull=True).exists():
            blockers.append("زمان امتحان یک یا چند درس هنوز در سامانه ثبت نشده است.")
        return {
            "exam_card": {"enrollments": exam_enrollments, "blockers": blockers},
            "printable": True,
        }

    if slug == "student-card":
        return {"printable": True}

    if slug == "support":
        rows = m.Ticket.objects.filter(creator=request.user).select_related("status", "category")
        return {"form": form_for(SupportForm, request, student, term), "tables": [table(
            "پیگیری پشتیبانی", ["شناسه", "موضوع", "متن", "وضعیت"],
            ((x.pk, x.subject, x.content, x.status) for x in rows))]}

    return {"notice": "از منوی سامانه بخش موردنظر را انتخاب کنید."}


def _shahsavand_page(slug, student, term, request):
    if slug == "guest-request":
        rows = m.TransferRequest.objects.filter(student=student).select_related("review_status")
        return {"form": form_for(GuestRequestForm, request, student, term), "tables": [table(
            "درخواست‌های مهمانی", ["مقصد", "تاریخ", "وضعیت"],
            ((x.destination_university, x.created_at, x.review_status) for x in rows))]}
    if slug in {"evaluation", "evaluation-form"}:
        rows = m.TeacherSurvey.objects.filter(
            enrollment__student=student, enrollment__offering__term=term
        ).select_related("enrollment__offering__teacher__person", "enrollment__offering__lesson")
        return {"form": form_for(SurveyForm, request, student, term), "tables": [table(
            "ارزشیابی‌های ثبت‌شده", ["درس", "استاد", "امتیاز", "دیدگاه"],
            ((x.enrollment.offering.lesson.title, x.enrollment.offering.teacher.person.full_name,
              x.overall_rating, x.comment) for x in rows))]}
    if slug == "messages":
        rows = m.Communication.objects.filter(
            Q(sender__person=request.user) | Q(receiver__person=request.user)
        ).select_related("sender__person", "receiver__person")
        return {"form": form_for(MessageForm, request, student, term), "tables": [table(
            "مکاتبات", ["فرستنده", "گیرنده", "موضوع", "متن", "تاریخ"],
            ((x.sender.person.full_name, x.receiver.person.full_name, x.subject,
              x.message_body, x.sent_at) for x in rows))]}
    rows = m.GraduationAudit.objects.filter(student=student).select_related(
        "graduation_status", "curriculum")
    return {"form": form_for(GraduationReviewForm, request, student, term),
        "form_title": "درخواست بررسی فارغ‌التحصیلی",
        "notice": "ثبت درخواست به معنی تأیید فارغ‌التحصیلی نیست؛ نتیجه توسط آموزش اعلام می‌شود.",
        "tables": [table("نتیجه بررسی آموزش", ["تاریخ", "واحد باقیمانده", "وضعیت"],
            ((x.audit_date, x.remaining_units, x.graduation_status) for x in rows))]}


def build(slug, student, term, request):
    """Dispatch pages to the contributor's existing selectors in this group."""
    if slug in OMID_PAGES:
        return _omid_page(slug, student, term, request)
    if slug in SHAHSAVAND_PAGES:
        return _shahsavand_page(slug, student, term, request)
    return {"notice": "از منوی سامانه بخش موردنظر را انتخاب کنید."}
