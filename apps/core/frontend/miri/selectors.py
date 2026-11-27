"""Student/account-scoped faculty and general service selectors for Miri."""

from django.db.models import Count, Prefetch, Q
from django.http import Http404

from apps.core import models as m
from ..common import active_enrollment_rows, form_for, term_code_display
from .forms import EVALUATION_CRITERIA, MessageForm, SupportForm, SurveyForm


def build(slug, student, term, request):
    if slug == "announcements":
        rows = m.Communication.objects.filter(
            receiver__person=request.user,
            communication_type__category="communication_type",
            communication_type__code="announcement",
        ).select_related(
            "sender__person", "communication_type", "status"
        ).order_by("-sent_at", "-communication_id")
        return {
            "announcements": rows,
            "announcement_count": rows.count(),
            "announcement_unread_count": rows.filter(is_read=False).count(),
            "announcement_term_code": term_code_display(term),
            "announcement_scope_note": (
                "مکاتبه‌های نوع اطلاعیه برای حساب شما؛ مدل فعلی ارتباط مستقیم با درس یا نیمسال ندارد."
            ),
        }

    if slug == "notifications":
        rows = m.Notification.objects.filter(user__person=request.user)
        type_counts = rows.values(
            "notification_type__code", "notification_type__label"
        ).annotate(count=Count("pk")).order_by("notification_type__label")
        filters = []
        for item in type_counts:
            filters.append({
                "code": item["notification_type__code"] or "__untyped__",
                "label": item["notification_type__label"] or "بدون نوع",
                "count": item["count"],
            })
        requested_filter = request.GET.get("notification_type", "")
        available_codes = {item["code"] for item in filters}
        active_filter = requested_filter if requested_filter in available_codes else ""
        visible_rows = rows
        if active_filter == "__untyped__":
            visible_rows = visible_rows.filter(notification_type__isnull=True)
        elif active_filter:
            visible_rows = visible_rows.filter(notification_type__code=active_filter)
        return {
            "notifications": visible_rows.select_related("notification_type").order_by(
                "-sent_at", "-created_at", "-pk"
            ),
            "notification_count": rows.count(),
            "notification_type_filters": filters,
            "notification_filter_code": active_filter,
        }

    if slug == "evaluation":
        enrollments = list(active_enrollment_rows(student, term).select_related(
            "offering__lesson", "offering__teacher__person", "offering__term"
        ))
        surveys = m.TeacherSurvey.objects.filter(enrollment__in=enrollments)
        survey_by_enrollment = {survey.enrollment_id: survey for survey in surveys}
        return {
            "evaluation_course_entries": [
                {
                    "enrollment": enrollment,
                    "survey": survey_by_enrollment.get(enrollment.pk),
                }
                for enrollment in enrollments
            ],
            "evaluation_course_count": len(enrollments),
            "evaluation_completed_count": len(survey_by_enrollment),
            "evaluation_term_code": term_code_display(term),
            "evaluation_notice": (
                "هر معیار ارزشیابی از ۱ تا ۵ است. پاسخ‌ها به ثبت‌نام دانشجو پیوند دارند "
                "و ناشناس بودن تضمین نشده است."
            ),
        }

    if slug == "evaluation-form":
        enrollments = active_enrollment_rows(student, term).select_related(
            "offering__lesson", "offering__teacher__person", "offering__term"
        )
        raw_enrollment_id = request.POST.get("enrollment") or request.GET.get("enrollment")
        selected_enrollment = None
        if raw_enrollment_id:
            try:
                enrollment_id = int(raw_enrollment_id)
            except (TypeError, ValueError):
                raise Http404("درس انتخاب‌شده پیدا نشد.")
            selected_enrollment = enrollments.filter(pk=enrollment_id).first()
            if selected_enrollment is None:
                raise Http404("درس انتخاب‌شده پیدا نشد.")
        else:
            pending = enrollments.exclude(teacher_surveys__isnull=False)
            if pending.count() == 1:
                selected_enrollment = pending.first()

        selected_survey = None
        form = None
        if selected_enrollment is not None:
            selected_survey = m.TeacherSurvey.objects.filter(
                enrollment=selected_enrollment
            ).first()
            if selected_survey is None:
                form = SurveyForm(
                    request.POST if request.method == "POST" else None,
                    student=student,
                    person=request.user,
                    term=term,
                    selected_enrollment=selected_enrollment,
                )

        return {
            "form": form,
            "evaluation_selected_enrollment": selected_enrollment,
            "evaluation_selected_survey": selected_survey,
            "evaluation_enrollment_options": enrollments.exclude(
                teacher_surveys__isnull=False
            ),
            "evaluation_rating_fields": (
                [(label, form[name]) for name, label in EVALUATION_CRITERIA]
                if form is not None else []
            ),
            "evaluation_submitted_ratings": (
                [(label, getattr(selected_survey, name)) for name, label in EVALUATION_CRITERIA]
                if selected_survey is not None else []
            ),
        }

    if slug == "messages":
        rows = m.Communication.objects.filter(
            Q(sender__person=request.user) | Q(receiver__person=request.user)
        ).select_related(
            "sender__person", "receiver__person", "communication_type", "status"
        ).order_by("-sent_at", "-communication_id")
        raw_request_id = request.GET.get("request_id", "")
        try:
            request_id = int(raw_request_id)
        except (TypeError, ValueError):
            request_id = None
        submission_result = (
            rows.filter(pk=request_id, sender__person=request.user).first()
            if request_id and 0 < request_id <= 9_223_372_036_854_775_807
            else None
        )
        message_form = form_for(MessageForm, request, student, term)
        teachers_by_id = {}
        enrolled_lessons = active_enrollment_rows(student, term).filter(
            offering__is_active=True
        ).select_related(
            "offering__teacher__person", "offering__lesson",
            "offering__day_of_week", "offering__classroom",
        ).order_by(
            "offering__teacher__person__last_name",
            "offering__teacher__person__first_name",
            "offering__lesson__title",
        )
        for enrollment in enrolled_lessons:
            offering = enrollment.offering
            teacher = offering.teacher
            teacher_entry = teachers_by_id.setdefault(teacher.pk, {
                "teacher": teacher,
                "lessons": [],
            })
            teacher_entry["lessons"].append({
                "title": offering.lesson.title,
                "day": offering.day_of_week.label if offering.day_of_week_id else "روز ثبت نشده",
                "start": offering.start_time,
                "end": offering.end_time,
                "classroom": offering.classroom,
            })
        return {
            "form": message_form,
            "message_can_send": bool(
                message_form and message_form.fields["receiver"].queryset.exists()
            ),
            "message_teachers": list(teachers_by_id.values()),
            "message_history": rows[:8],
            "message_count": rows.count(),
            "message_submission_result": submission_result,
            "message_scope_note": (
                "فهرست استادها از ثبت‌نام‌های فعال همین نیمسال است؛ تاریخچه از مکاتبات حساب جاری می‌آید. "
                "ثبت در پایگاه داده به معنی تحویل بیرونی یا پیامک/ایمیل نیست."
            ),
        }

    if slug == "support":
        owned_tickets = m.Ticket.objects.filter(
            creator=request.user, parent__isnull=True
        ).select_related(
            "status", "category"
        ).prefetch_related(Prefetch(
            "replies",
            queryset=m.Ticket.objects.order_by("-created_at", "-pk"),
            to_attr="ordered_replies",
        )).order_by("-created_at", "-pk")
        rows = list(owned_tickets)
        for ticket in rows:
            ticket.latest_reply = ticket.ordered_replies[0] if ticket.ordered_replies else None
        raw_request_id = request.GET.get("request_id", "")
        try:
            request_id = int(raw_request_id)
        except (TypeError, ValueError):
            request_id = None
        submission_result = (
            owned_tickets.filter(pk=request_id).first()
            if request_id and 0 < request_id <= 9_223_372_036_854_775_807
            else None
        )
        form = SupportForm(
            request.POST if request.method == "POST" else None,
            student=student,
            person=request.user,
            term=term,
        )
        return {
            "form": form,
            "support_tickets": rows,
            "support_submission_result": submission_result,
            "support_attachment_note": "بارگذاری فایل در این نسخه پشتیبانی نمی‌شود.",
        }

    if slug == "guide":
        return {
            "guide_topics": [
                {
                    "title": "چطور انتخاب واحد کنم؟",
                    "description": "اطلاعات دانشجو را بررسی کنید، بدهی را تسویه و پس از کنترل پیش‌نیاز و سقف واحد، گروه درس را انتخاب کنید.",
                    "slug": "enrollment",
                    "link_label": "ورود به بخش",
                },
                {
                    "title": "چرا ثبت‌نام مسدود است؟",
                    "description": "بدهی شهریه، بازهٔ زمانی یا محدودیت آموزشی را در وضعیت ثبت‌نام بررسی کنید.",
                    "implementation_note": "صفحهٔ وضعیت فعلی علت انسداد را به‌صورت مستقل گزارش نمی‌کند؛ بدهی و بازه را از بخش‌های مربوط بررسی کنید.",
                    "slug": "registration-status",
                    "link_label": "ورود به بخش",
                },
                {
                    "title": "حذف اضطراری چه محدودیتی دارد؟",
                    "description": "تعداد واحد پس از حذف نباید از حداقل مجاز تعریف‌شده در سیستم کمتر باشد؛ عدد ثابت معیار نیست.",
                    "implementation_note": "تفاوت با مرجع: API فعلی حذف اضطراری حداقل واحد را کنترل نمی‌کند؛ فقط مالکیت ثبت‌نام و بازهٔ مجاز را بررسی می‌کند.",
                    "slug": "emergency-drop",
                    "link_label": "ورود به بخش",
                },
                {
                    "title": "اعلان و پیام استاد را کجا ببینیم؟",
                    "description": "اطلاعیه‌های درسی در گروه اساتید و همهٔ رویدادها در مرکز اعلان‌ها قرار دارند.",
                    "slug": "messages",
                    "link_label": "ورود به بخش",
                },
            ],
            "guide_support_slug": "support",
        }

    return {"notice": "راهنمای بخش‌ها از منوی اصلی در دسترس است."}
