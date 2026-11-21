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
        return {
            "form": form_for(ScholarshipForm, request, student, term),
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
        data["finance_actions"] = [
            {"slug": "payments", "label": "مشاهده سوابق پرداخت"},
            {"slug": "financial-aid", "label": "درخواست تسهیلات"},
        ]
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

    return data
