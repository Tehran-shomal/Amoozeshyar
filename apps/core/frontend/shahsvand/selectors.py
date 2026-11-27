"""Student-scoped student request selectors for Shahsvand."""

from apps.core import models as m
from ..common import form_for, table
from .forms import (
    CertificateForm,
    GuestRequestForm,
    InternshipForm,
    ServiceRequestForm,
)


def build(slug, student, term, request):
    if slug == "internship":
        rows = m.Internship.objects.filter(student=student).select_related("status").order_by("-pk")
        raw_request_id = request.GET.get("request_id", "")
        try:
            request_id = int(raw_request_id)
        except (TypeError, ValueError):
            request_id = None
        submission_result = (
            rows.filter(pk=request_id).first()
            if request_id and 0 < request_id <= 9_223_372_036_854_775_807
            else None
        )
        return {"form": form_for(InternshipForm, request, student, term), "tables": [table(
            "پیگیری کارآموزی", ["سازمان", "شروع", "ساعت", "وضعیت"],
            ((row.company_name, row.intern_start_date, row.duration_hours, row.status)
             for row in rows),
        )], "submission_result": submission_result}

    if slug == "guest-request":
        rows = m.TransferRequest.objects.filter(student=student).select_related(
            "review_status"
        ).order_by("-pk")
        raw_request_id = request.GET.get("request_id", "")
        try:
            request_id = int(raw_request_id)
        except (TypeError, ValueError):
            request_id = None
        submission_result = (
            rows.filter(pk=request_id).first()
            if request_id and 0 < request_id <= 9_223_372_036_854_775_807
            else None
        )
        return {"form": form_for(GuestRequestForm, request, student, term), "tables": [table(
            "آخرین درخواست‌ها", ["شناسه", "مقصد", "تاریخ ثبت", "وضعیت بررسی"],
            ((row.transfer_id, row.destination_university, row.created_at, row.review_status)
             for row in rows),
        )], "submission_result": submission_result}

    if slug == "graduation":
        audits = list(m.GraduationAudit.objects.filter(student=student).select_related(
            "graduation_status", "curriculum"
        ).order_by("-audit_date"))
        latest_audit = audits[0] if audits else None
        if latest_audit is None:
            latest_result = "بررسی رسمی برای این پرونده ثبت نشده است"
            latest_remaining_units = "—"
        else:
            latest_result = (
                "آخرین بررسی، پرونده را واجد شرایط اعلام کرده است"
                if latest_audit.is_graduation_eligible
                else display(latest_audit.graduation_status)
            )
            latest_remaining_units = latest_audit.remaining_units
        return {
            "notice": (
                "این صفحه فقط اطلاعات پرونده و نتیجهٔ بررسی‌های ذخیره‌شده را نشان می‌دهد. "
                "نوع درخواست معتبر فارغ‌التحصیلی در داده‌های سامانه تعریف نشده؛ ثبت نهایی ممکن نیست."
            ),
            "graduation_checks": [
                {
                    "label": "پروندهٔ دانشجویی",
                    "value": f"{student.person.full_name} · {student.student_code}",
                    "status": "اطلاعات ثبت‌شده",
                    "state": "recorded",
                },
                {
                    "label": "واحد گذرانده در پرونده",
                    "value": f"{student.passed_units} واحد",
                    "status": "عدد ثبت‌شده؛ نه ارزیابی کامل‌شدن چارت",
                    "state": "review",
                },
                {
                    "label": "معدل کل",
                    "value": display(student.total_gpa),
                    "status": "حدنصاب رسمی در داده‌ها تعریف نشده",
                    "state": "review",
                },
                {
                    "label": "ماندهٔ بدهی شهریه",
                    "value": f"{student.tuition_debt:,.0f} ریال",
                    "status": "مبلغ ثبت‌شده؛ شرط تسویه قابل استنتاج نیست",
                    "state": "review",
                },
                {
                    "label": "آخرین بررسی آموزش",
                    "value": latest_result,
                    "status": f"{latest_remaining_units} واحد باقیمانده",
                    "state": "recorded" if latest_audit and latest_audit.is_graduation_eligible else "review",
                },
                {
                    "label": "تسویهٔ کتابخانه",
                    "value": "در این نسخه قابل بررسی نیست",
                    "status": "سرویس/مدل متصل در سامانه موجود نیست",
                    "state": "unavailable",
                },
            ],
            "graduation_audit_count": len(audits),
            "tables": [table(
                "سوابق بررسی آموزش", ["شناسه", "تاریخ بررسی", "چارت", "واحد باقیمانده", "نتیجه"],
                ((row.audit_id, row.audit_date, row.curriculum, row.remaining_units,
                  row.graduation_status) for row in audits),
            )],
        }

    if slug == "graduation-certificate":
        data = build("graduation", student, term, request)
        latest_audit = m.GraduationAudit.objects.filter(
            student=student
        ).select_related("graduation_status").first()
        curriculum_units = list(m.Curriculum.objects.filter(
            field=student.field, is_active=True
        ).values_list("calculated_units", flat=True))
        data.update({
            "notice": (
                "گواهی دانش‌آموختگی فقط پس از احراز شرایط، تسویه و تأیید رسمی صادر می‌شود. "
                "در این نسخه نوع درخواست معتبر و سرویس صدور متصل نیست؛ ثبت یا صدور مدرک انجام نمی‌شود."
            ),
            "certificate_curriculum_units": (
                f"{sum(curriculum_units)} واحد" if curriculum_units
                else "در چارت فعال ثبت نشده"
            ),
            "certificate_steps": [
                {
                    "title": "احراز شرایط فراغت",
                    "status": (
                        f"آخرین بررسی: {display(latest_audit.graduation_status)}"
                        if latest_audit else "بررسی رسمی برای این پرونده ثبت نشده"
                    ),
                },
                {
                    "title": "تسویهٔ مالی و کتابخانه",
                    "status": (
                        f"بدهی پرونده: {student.tuition_debt:,.0f} ریال؛ "
                        "وضعیت کتابخانه در این نسخه قابل بررسی نیست."
                    ),
                },
                {
                    "title": "تأیید آموزش",
                    "status": "وضعیت تأیید رسمی فقط از آخرین audit ذخیره‌شده قابل مشاهده است؛ تأیید تازه ثبت نمی‌شود.",
                },
                {
                    "title": "صدور و تحویل مدرک",
                    "status": "صدور رسمی به سرویس متصل نیاز دارد؛ این صفحه فایل مدرک صادر نمی‌کند.",
                },
            ],
        })
        return data

    rows = m.StudentServiceRequest.objects.filter(
        service_requester=student
    ).select_related("service_request_kind", "service_decision_state").order_by("-pk")
    form = form_for(ServiceRequestForm, request, student, term)
    operation_result = None
    if slug == "requests":
        raw_request_id = request.GET.get("request_id", "")
        try:
            request_id = int(raw_request_id)
        except (TypeError, ValueError):
            request_id = None
        service_request = (
            rows.filter(pk=request_id).first()
            if request_id and 0 < request_id <= 9_223_372_036_854_775_807
            else None
        )
        if service_request:
            operation_result = {
                "heading": "درخواست دانشجویی ثبت شد",
                "message": f"درخواست «{display(service_request.service_request_kind)}» با شناسهٔ {service_request.pk} برای این پرونده ثبت شد.",
                "status": display(service_request.service_decision_state),
                "note": "ارسال به سامانهٔ دانشگاهی انجام نشده است؛ این نتیجه فقط ثبت درخواست در پایگاه محلی را تأیید می‌کند.",
            }
    notice = ""
    if slug == "education-certificate":
        rows = rows.filter(service_request_kind__code="employment_certificate")
        notice = (
            "این فرم فقط درخواست محلی گواهی اشتغال و توضیح تکمیلی را ثبت می‌کند؛ "
            "مخاطب، تعداد نسخه و روش تحویل در مدل/API فعلی ثبت نمی‌شوند و گواهی رسمی صادر نمی‌شود."
        )
        form = CertificateForm(
            request.POST if request.method == "POST" else None,
            student=student,
            person=request.user,
            term=term,
            allowed_codes=("employment_certificate",),
        )
        if not form.fields["service_request_kind"].queryset.exists():
            form = None
            notice += " نوع درخواست گواهی اشتغال در lookup فعال این پایگاه داده پیدا نشد؛ فرمی ارسال نمی‌شود."
        raw_request_id = request.GET.get("request_id", "")
        try:
            request_id = int(raw_request_id)
        except (TypeError, ValueError):
            request_id = None
        certificate_request = (
            rows.filter(pk=request_id).first()
            if request_id and 0 < request_id <= 9_223_372_036_854_775_807
            else None
        )
        if certificate_request:
            operation_result = {
                "heading": "درخواست گواهی آموزشی ثبت شد",
                "message": f"درخواست گواهی اشتغال برای پروندهٔ شما ثبت شد؛ شناسهٔ درخواست {certificate_request.pk} است.",
                "status": display(certificate_request.service_decision_state),
                "note": "گواهی رسمی صادر نشده است؛ برای دریافت گواهی معتبر به سامانهٔ رسمی دانشگاه مراجعه کنید.",
            }
    elif slug == "requests":
        notice = (
            "این فرم نوع درخواست و توضیحات را فقط در پایگاه محلی ثبت می‌کند؛ "
            "شمارهٔ تماس و پیوست در مدل/API فعلی پشتیبانی نمی‌شوند و درخواست به سامانهٔ دانشگاه ارسال نمی‌شود."
        )
    return {"form": form, "notice": notice, "operation_result": operation_result, "tables": [table(
        "پیگیری درخواست‌ها", ["شناسه", "نوع درخواست", "توضیحات", "وضعیت"],
        ((row.pk, row.service_request_kind, row.service_request_data,
          row.service_decision_state) for row in rows),
    )]}
