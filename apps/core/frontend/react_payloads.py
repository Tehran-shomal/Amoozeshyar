"""Explicit, authenticated view-model serialization for the React portal."""

from collections.abc import Mapping
from datetime import date, datetime, time
from decimal import Decimal
from math import isfinite

from django.utils import timezone

from .common import display
from .metadata import NAV_GROUPS, SIDEBAR_FOOTER
from .react_forms import serialize_form


COMMON_DATA_KEYS = frozenset({
    "notice", "facts", "tables", "form_title", "operation_result", "links",
    "printable",
})

# Only page-specific values already built as display dictionaries/lists or
# primitives are included here. Raw Django models/querysets are intentionally
# omitted until a page adapter explicitly maps the fields its UI needs.
PAGE_DATA_KEYS = {
    "home": {"dashboard"},
    "settings": {"settings_save_result", "notification_categories"},
    "student-card": set(),
    "enrollment": {"enrollment_can_continue"},
    "selected-courses": {
        "selected_units", "maximum_allowed_units", "tuition_breakdown_available",
    },
    "add-drop": {
        "course_change_table", "course_offering_table", "course_change_units",
        "course_change_debt", "maximum_allowed_units", "tuition_breakdown_available",
    },
    "emergency-drop": {
        "course_change_table", "course_offering_table", "course_change_units",
        "course_change_debt", "maximum_allowed_units", "tuition_breakdown_available",
    },
    "registration-status": {
        "registration_status_count", "registration_status_units",
        "registration_status_max_units", "registration_status_debt",
        "registration_status_stages",
    },
    "attendance": {
        "attendance_rows", "attendance_term", "attendance_active_course_count",
        "attendance_active_units", "attendance_session_count",
        "attendance_present_count", "attendance_absence_count",
        "attendance_late_count", "attendance_unclassified_count",
        "attendance_last_updated",
    },
    "exam-card": set(),
    "calendar": {
        "calendar_month_label", "calendar_days", "calendar_events",
        "calendar_term_code", "calendar_term_range", "calendar_next_deadline",
        "calendar_summary",
    },
    "schedule": {
        "schedule_summary", "schedule_days", "schedule_slots",
        "schedule_unassigned", "schedule_column_count",
    },
    "academic-activities": {"activity_summary", "activity_links"},
    "transcript": {"current_units", "transcript_summary", "transcript_rows"},
    "curriculum": {"curriculum_rows", "curriculum_summary"},
    "grade-appeal": set(),
    "payments": {"finance_summary", "finance_debt_display", "finance_term_label", "finance_actions"},
    "secure-payment": {
        "finance_summary", "finance_debt_display", "finance_term_label", "finance_notice",
    },
    "financial-aid": set(),
    "tuition": {
        "finance_summary", "finance_debt_display", "finance_term_label",
        "tuition_rows", "finance_actions",
    },
    "internship": set(),
    "guest-request": set(),
    "graduation": {"graduation_checks", "graduation_audit_count"},
    "graduation-certificate": {"certificate_curriculum_units", "certificate_steps"},
    "requests": set(),
    "education-certificate": set(),
    "announcements": {
        "announcement_count", "announcement_unread_count", "announcement_term_code",
        "announcement_scope_note",
    },
    "notifications": {
        "notification_count", "notification_type_filters", "notification_filter_code",
    },
    "evaluation": {
        "evaluation_course_count", "evaluation_completed_count",
        "evaluation_term_code", "evaluation_notice",
    },
    "evaluation-form": {"evaluation_submitted_ratings"},
    "messages": {"message_can_send", "message_count", "message_scope_note"},
    "guide": {"guide_topics", "guide_support_slug"},
    "support": {"support_attachment_note"},
}


class UnsupportedPayloadValue(TypeError):
    """Raised when a page adapter attempts to expose an unapproved object."""


def _json_value(value):
    if value is None or isinstance(value, (str, int, bool)):
        return value
    if isinstance(value, float):
        if not isfinite(value):
            raise UnsupportedPayloadValue("Non-finite numbers are not supported.")
        return value
    if isinstance(value, Decimal):
        return format(value, "f")
    if isinstance(value, (datetime, date, time)):
        return value.isoformat()
    if isinstance(value, Mapping):
        if not all(isinstance(key, str) for key in value):
            raise UnsupportedPayloadValue("Payload object keys must be strings.")
        return {key: _json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_value(item) for item in value]
    raise UnsupportedPayloadValue(f"Unsupported value: {type(value).__name__}")


def _navigation(groups):
    return [
        {
            "title": group.get("title", ""),
            "items": [
                {
                    "label": item.get("label", ""),
                    "slug": item.get("slug", ""),
                    "icon": item.get("icon", ""),
                }
                for item in group.get("items", [])
            ],
        }
        for group in groups
    ]


def _profile_option(profile):
    return {
        "student_code": str(profile.student_code),
        "educational_level": display(profile.educational_level),
    }


def _current_profile(student):
    if student is None:
        return None
    return {
        "student_code": str(student.student_code),
        "full_name": str(student.person.full_name),
        "field_name": display(student.field.field_name) if student.field_id else "—",
        "educational_level": display(student.educational_level),
    }


def _timestamp(value):
    if value is None:
        return {"iso": None, "display": ""}
    if isinstance(value, datetime) and timezone.is_aware(value):
        value = timezone.localtime(value)
    return {
        "iso": value.isoformat(),
        "display": value.strftime("%Y-%m-%d %H:%M"),
    }


def _date_display(value, format_string="%Y/%m/%d"):
    if value is None:
        return "—"
    if isinstance(value, datetime) and timezone.is_aware(value):
        value = timezone.localtime(value)
    return value.strftime(format_string)


def _student_card(student, term_label):
    if student is None:
        return None
    application_date = student.application_date
    return {
        "full_name": str(student.person.full_name),
        "student_code": str(student.student_code),
        "field_name": str(student.field.field_name) if student.field_id else "—",
        "educational_level": display(student.educational_level),
        "status": display(student.status),
        "application_date": (
            application_date.strftime("%Y/%m/%d") if application_date else "—"
        ),
        "term_display_code": str(term_label or "—"),
    }


def _announcement_rows(rows):
    return [
        {
            "communication_id": int(row.communication_id),
            "subject": str(row.subject or ""),
            "sender_name": str(row.sender.person.full_name),
            "message_body": str(row.message_body or ""),
            "sent_at": _timestamp(row.sent_at),
            "is_read": bool(row.is_read),
        }
        for row in rows
    ]


def _notification_rows(rows):
    return [
        {
            "notification_id": int(row.pk),
            "type_label": (
                str(row.notification_type.label)
                if row.notification_type_id
                else "بدون نوع"
            ),
            "title": str(row.title or ""),
            "message": str(row.message or ""),
            "is_read": bool(row.is_read),
        }
        for row in rows
    ]


def _payment_rows(rows):
    return [
        {
            "tracking_code": str(row.tracking_code),
            "payment_date": _timestamp(row.payment_date),
            "amount": format(row.amount, ",.0f"),
            "status": (
                str(row.status.label) if row.status_id else "نامشخص"
            ),
        }
        for row in rows
    ]


def _message_row(row, current_person_id):
    sent_at = _timestamp(row.sent_at)
    return {
        "subject": str(row.subject or ""),
        "message_body": str(row.message_body or ""),
        "sent_at": sent_at,
        "sender_name": str(row.sender.person.full_name),
        "receiver_name": str(row.receiver.person.full_name),
        "sender_is_current_user": row.sender.person_id == current_person_id,
    }


def _message_teachers(entries):
    result = []
    for entry in entries:
        teacher = entry.get("teacher")
        if teacher is None:
            continue
        lessons = []
        for lesson in entry.get("lessons", []):
            start, end = lesson.get("start"), lesson.get("end")
            classroom = lesson.get("classroom")
            lessons.append({
                "title": str(lesson.get("title") or ""),
                "day": str(lesson.get("day") or ""),
                "start": start.strftime("%H:%M") if start else "—",
                "end": end.strftime("%H:%M") if end else "—",
                "classroom": display(classroom),
            })
        result.append({
            "teacher_name": str(teacher.person.full_name),
            "lessons": lessons,
        })
    return result


def _support_ticket(ticket):
    reply = getattr(ticket, "latest_reply", None)
    return {
        "id": int(ticket.pk),
        "subject": str(ticket.subject or ""),
        "status": display(ticket.status),
        "created_at": _timestamp(ticket.created_at),
        "created_at_display": _date_display(
            ticket.created_at, "%Y/%m/%d %H:%M"
        ),
        "latest_reply": ({
            "content": str(reply.content or ""),
            "created_at": _timestamp(reply.created_at),
            "created_at_display": _date_display(reply.created_at),
        } if reply else None),
    }


def _evaluation_enrollment(enrollment):
    if enrollment is None:
        return None
    offering = enrollment.offering
    return {
        "id": int(enrollment.pk),
        "lesson": str(offering.lesson.title),
        "teacher": str(offering.teacher.person.full_name),
        "term": str(offering.term.term_code),
    }


def _evaluation_survey(survey):
    if survey is None:
        return None
    return {
        "overall_rating": survey.overall_rating,
        "ratings": {
            "teaching_quality": survey.teaching_quality,
            "behavior": survey.behavior,
        },
        "comment": str(survey.comment or ""),
    }


def serialize_page(slug, context):
    """Serialize only the React page contract and explicitly allowed data."""
    section = context.get("section") or {}
    selected_term = context.get("selected_term")
    current_student = context.get("current_student")
    raw_profile = context.get("api_profile") or {}
    profile_code = raw_profile.get("student_code")
    allowed_keys = COMMON_DATA_KEYS | PAGE_DATA_KEYS.get(slug, set())

    data = {}
    omitted_fields = []
    for key in sorted(allowed_keys):
        if key not in context:
            continue
        try:
            data[key] = _json_value(context[key])
        except UnsupportedPayloadValue:
            omitted_fields.append(key)

    # These page values originate as scoped Django models/querysets. Map only
    # the fields visible in each current template; never pass model objects on.
    if slug == "student-card":
        data["student_card"] = _student_card(
            current_student, context.get("term_display_code")
        )
    elif slug == "announcements":
        data["announcements"] = _announcement_rows(
            context.get("announcements", [])
        )
    elif slug == "notifications":
        data["notifications"] = _notification_rows(
            context.get("notifications", [])
        )
    elif slug == "payments":
        data["payment_rows"] = _payment_rows(context.get("payment_rows", []))
        failed_payment = context.get("failed_payment")
        data["failed_payment"] = (
            {"tracking_code": str(failed_payment.tracking_code)}
            if failed_payment is not None else None
        )
    elif slug == "messages":
        person_id = getattr(current_student, "person_id", None)
        data["message_teachers"] = _message_teachers(
            context.get("message_teachers", [])
        )
        data["message_history"] = [
            _message_row(row, person_id)
            for row in context.get("message_history", [])
        ]
        submission = context.get("message_submission_result")
        data["message_submission_result"] = (
            {
                **_message_row(submission, person_id),
                "receiver_name": str(submission.receiver.person.full_name),
            }
            if submission is not None else None
        )
    elif slug == "support":
        data["support_tickets"] = [
            _support_ticket(ticket)
            for ticket in context.get("support_tickets", [])
        ]
        submission = context.get("support_submission_result")
        data["support_submission_result"] = (
            _support_ticket(submission) if submission is not None else None
        )
    elif slug == "academic-activities":
        activities = context.get("recent_activities", [])
        data["recent_activities"] = [
            {
                "change_type": display(activity.change_type),
                "changed_at": _timestamp(activity.changed_at),
                "changed_at_display": _date_display(activity.changed_at),
                "description": str(activity.description or "ثبت‌شده"),
            }
            for activity in activities
        ]
    elif slug in {"enrollment", "selected-courses", "add-drop", "emergency-drop"}:
        if current_student is not None:
            active_max_units = context.get(
                "maximum_allowed_units", current_student.max_allowed_units
            )
            data["course_overview"] = {
                "full_name": str(current_student.person.full_name),
                "student_code": str(current_student.student_code),
                "field_name": (
                    str(current_student.field.field_name)
                    if current_student.field_id else "—"
                ),
                "educational_level": display(current_student.educational_level),
                "status": display(current_student.status),
                "maximum_allowed_units": int(active_max_units),
                "tuition_debt": _json_value(current_student.tuition_debt),
                "tuition_debt_display": format(current_student.tuition_debt, ",.0f"),
            }
        data["course_term"] = ({
            "academic_year": str(selected_term.academic_year),
            "semester": display(selected_term.semester),
        } if selected_term else None)
        registration = context.get("course_registration_result")
        data["course_registration_result"] = ({
            "enrollment_id": int(registration.pk),
            "lesson": str(registration.offering.lesson.title),
            "lesson_code": str(registration.offering.lesson.lesson_code),
            "status": display(registration.status) if registration.status_id else "ثبت‌شده",
        } if registration is not None else None)
        dropped = context.get("course_drop_result")
        data["course_drop_result"] = ({
            "enrollment_id": int(dropped.pk),
            "lesson": str(dropped.offering.lesson.title),
            "lesson_code": str(dropped.offering.lesson.lesson_code),
            "status": display(dropped.status),
            "drop_date": _date_display(dropped.drop_date),
        } if dropped is not None else None)
    elif slug == "evaluation":
        data["evaluation_course_entries"] = [
            {
                "enrollment": _evaluation_enrollment(entry["enrollment"]),
                "completed": entry.get("survey") is not None,
            }
            for entry in context.get("evaluation_course_entries", [])
        ]
    elif slug == "evaluation-form":
        selected_enrollment = context.get("evaluation_selected_enrollment")
        data["evaluation_selected_enrollment"] = _evaluation_enrollment(
            selected_enrollment
        )
        data["evaluation_selected_survey"] = _evaluation_survey(
            context.get("evaluation_selected_survey")
        )
        data["evaluation_enrollment_options"] = [
            _evaluation_enrollment(enrollment)
            for enrollment in context.get("evaluation_enrollment_options", [])
        ]
    elif slug in {"internship", "guest-request"}:
        result = context.get("submission_result")
        if result is not None and slug == "internship":
            data["service_submission_result"] = {
                "id": int(result.pk),
                "kind": "internship",
                "company_name": str(result.company_name or ""),
                "status": display(result.status),
                "created_at": _date_display(result.created_at, "%Y/%m/%d %H:%M"),
            }
        elif result is not None:
            data["service_submission_result"] = {
                "id": int(result.transfer_id),
                "kind": "guest-request",
                "destination": str(result.destination_university or ""),
                "status": display(result.review_status),
                "created_at": _date_display(result.created_at, "%Y/%m/%d %H:%M"),
            }
    elif slug == "graduation-certificate":
        if current_student is not None:
            data["certificate_student"] = {
                "full_name": str(current_student.person.full_name),
                "student_code": str(current_student.student_code),
                "field_name": (
                    str(current_student.field.field_name)
                    if current_student.field_id else "—"
                ),
                "educational_level": display(current_student.educational_level),
                "status": display(current_student.status),
                "passed_units": int(current_student.passed_units),
                "tuition_debt_display": format(current_student.tuition_debt, ",.0f"),
            }
    elif slug == "exam-card":
        exam_card = context.get("exam_card") or {}
        data["exam_card"] = {
            "blockers": [str(item) for item in exam_card.get("blockers", [])],
            "enrollments": [
                {
                    "lesson": str(row.offering.lesson.title),
                    "exam_date": _date_display(row.offering.exam_date),
                    "exam_time": (
                        row.offering.exam_time.strftime("%H:%M")
                        if row.offering.exam_time else ""
                    ),
                    "classroom": display(row.offering.classroom),
                    "status": display(row.status) if row.status_id else "ثبت‌شده",
                }
                for row in exam_card.get("enrollments", [])
            ],
        }
        data["exam_student"] = _student_card(
            current_student, context.get("term_display_code")
        )

    shell = {
        "nav_groups": _navigation(context.get("nav_groups", NAV_GROUPS)),
        "sidebar_footer": _json_value(context.get("sidebar_footer", SIDEBAR_FOOTER)),
        "profiles": [_profile_option(profile) for profile in context.get("profiles", [])],
        "current_profile": _current_profile(current_student),
        "student": _json_value(context.get("student", {})),
        "profile_notice": str(context.get("profile_notice") or ""),
        "term_options": _json_value(context.get("term_options", [])),
    }

    return {
        "schema_version": 1,
        "page": slug,
        "title": str(section.get("title") or context.get("page_title") or ""),
        "subtitle": str(context.get("page_subtitle") or section.get("subtitle") or ""),
        "owner": str(context.get("owner") or "mobina"),
        "profile": {"student_code": str(profile_code) if profile_code else None},
        "term": {
            "term_code": selected_term.term_code if selected_term else None,
            "display_label": str(context.get("term_display_code") or ""),
        },
        "shell": shell,
        "data": data,
        "form": serialize_form(context.get("form")),
        "omitted_fields": omitted_fields,
    }
