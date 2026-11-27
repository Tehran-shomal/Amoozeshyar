"""Student-scoped financial data for Parsa's portal pages."""

from django.db.models import Sum

from apps.core import models as m
from ..common import display, form_for, table, term_code_display
from .forms import ScholarshipForm


def _money(value):
    """Use the amount unit already used by the portal's financial summary."""
    return f"{value or 0:,.0f} ریال"


def build(slug, student, term, request):
    if slug == "financial-aid":
        rows = m.ScholarshipApplication.objects.filter(
            scholarship_applicant=student
        ).select_related("scholarship_status")
        raw_request_id = request.GET.get("request_id", "")
        try:
            request_id = int(raw_request_id)
        except (TypeError, ValueError):
            request_id = None
        application = (
            rows.filter(pk=request_id).first()
            if request_id and 0 < request_id <= 9_223_372_036_854_775_807
            else None
        )
        operation_result = None
        if application:
            operation_result = {
                "heading": "درخواست تسهیلات ثبت شد",
                "message": f"درخواست «{application.scholarship_type}» با شناسهٔ {application.pk} برای این پرونده ثبت شد.",
                "status": display(application.scholarship_status),
                "created_at": display(application.scholarship_submitted_at),
                "note": "این ثبت درخواست به معنی تخصیص یا تأیید نهایی وام نیست؛ تصمیم نهایی به بررسی مدارک و منابع موجود وابسته است.",
            }
        return {
            "form": form_for(ScholarshipForm, request, student, term),
            "notice": (
                "این فرم فقط نوع تسهیلات و دلیل را در پروندهٔ محلی ثبت می‌کند؛ "
                "مبلغ درخواستی، شمارهٔ شبا و پیوست در مدل/API فعلی پشتیبانی نمی‌شوند. "
                "ثبت درخواست به معنی تأیید یا پرداخت نیست."
            ),
            "operation_result": operation_result,
            "tables": [table(
                "پیگیری تسهیلات",
                ["نوع", "دلیل", "تاریخ", "وضعیت"],
                ((row.scholarship_type, row.scholarship_reason,
                  row.scholarship_submitted_at, row.scholarship_status)
                 for row in rows),
            )],
        }

    # Every query stays scoped to the signed-in student's selected profile.
    all_payments = m.Payment.objects.filter(student=student).select_related(
        "term", "status", "term__semester"
    )
    term_payments = all_payments.filter(term=term) if term else all_payments
    successful = term_payments.filter(status__code="successful")
    paid_total = successful.aggregate(total=Sum("amount"))["total"] or 0
    data = {
        "finance_summary": [
            {"label": "پرداخت موفق", "value": _money(paid_total)},
            {"label": "بدهی ثبت‌شده در پرونده", "value": _money(student.tuition_debt)},
        ],
        "finance_debt_display": _money(student.tuition_debt),
        "finance_term_label": term_code_display(term) if term else "همهٔ نیمسال‌ها",
    }

    if slug == "payments":
        data["payment_rows"] = term_payments.order_by("-payment_date", "-pk")
        data["failed_payment"] = term_payments.filter(status__code="failed").order_by(
            "-payment_date", "-pk"
        ).first()
        data["finance_actions"] = [
            {"slug": "secure-payment", "label": "پرداخت مانده"},
            {"slug": "support", "label": "گزارش مغایرت"},
        ]
    elif slug == "secure-payment":
        data["finance_notice"] = (
            "درگاه پرداخت به سامانه متصل نیست؛ امکان پرداخت آنلاین وجود ندارد. "
            "هیچ مبلغی کسر یا تراکنش پرداختی ثبت نمی‌شود."
        )
    elif slug == "tuition":
        totals = m.Term.objects.filter(
            payments__student=student, payments__status__code="successful"
        ).select_related("semester").annotate(
            total=Sum("payments__amount")
        ).order_by("term_code")
        data["tuition_rows"] = [
            {
                "term_code": term_code_display(item),
                "academic_year": item.academic_year,
                "semester": item.semester.label if item.semester_id else "نیمسال",
                "total": _money(item.total),
            }
            for item in totals
        ]
        data["notice"] = (
            "تعرفه و ریزبدهی ثابت/متغیر در داده‌های فعلی موجود نیست؛ "
            "این صفحه فقط بدهی پرونده و جمع پرداخت‌های موفق ثبت‌شده را نشان می‌دهد."
        )
        data["finance_actions"] = [
            {"slug": "secure-payment", "label": "پرداخت بدهی"},
            {"slug": "payments", "label": "سوابق تراکنش‌ها"},
        ]

    return data
