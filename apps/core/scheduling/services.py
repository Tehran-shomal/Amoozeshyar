"""Business services for term and course-offering scheduling."""
from django.utils.dateparse import parse_date, parse_datetime, parse_time
from apps.core.models import (
    Classroom,
    Constant,
    CourseOffering,
    Lesson,
    Teacher,
    Term,
)
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.utils import timezone
from django.utils.dateparse import parse_date, parse_datetime

from apps.core.api import APIError
from apps.core.models import Constant, CourseOffering, Term


# --------------------------------------------------
# Existing read services
# --------------------------------------------------

def get_active_term():
    """Return the single active term, or None."""
    return Term.objects.filter(is_active=True).first()


def list_offerings(term=None):
    """List active offerings for the active term unless a term is supplied."""
    term = term or get_active_term()

    if term is None:
        return CourseOffering.objects.none()

    return (
        CourseOffering.objects.filter(term=term, is_active=True)
        .select_related("lesson", "day_of_week", "teacher__person", "classroom")
        .order_by("day_of_week__code", "start_time", "lesson__lesson_code")
    )


# --------------------------------------------------
# Term serialization
# --------------------------------------------------

def term_payload(term):
    if term is None:
        return None

    now = timezone.now()

    return {
        "id": term.pk,
        "term_code": term.term_code,
        "semester": (
            {
                "id": term.semester_id,
                "code": term.semester.code,
                "label": term.semester.label,
            }
            if term.semester else None
        ),
        "academic_year": term.academic_year,
        "start_date": term.start_date.isoformat(),
        "end_date": term.end_date.isoformat(),
        "registration_start": term.registration_start.isoformat(),
        "registration_end": term.registration_end.isoformat(),
        "add_drop_start": term.add_drop_start.isoformat(),
        "add_drop_end": term.add_drop_end.isoformat(),
        "emergency_drop_start": term.emergency_drop_start.isoformat(),
        "emergency_drop_end": term.emergency_drop_end.isoformat(),
        "is_active": term.is_active,
        "registration_open": term.registration_start <= now <= term.registration_end,
        "add_drop_open": term.add_drop_start <= now <= term.add_drop_end,
        "emergency_drop_open": (
            term.emergency_drop_start <= now <= term.emergency_drop_end
        ),
    }


# --------------------------------------------------
# Term input validation
# --------------------------------------------------

_TERM_DATETIME_FIELDS = (
    "registration_start",
    "registration_end",
    "add_drop_start",
    "add_drop_end",
    "emergency_drop_start",
    "emergency_drop_end",
)

_TERM_REQUIRED_FIELDS = (
    "term_code",
    "academic_year",
    "start_date",
    "end_date",
    *_TERM_DATETIME_FIELDS,
)

_TERM_ALLOWED_FIELDS = set(_TERM_REQUIRED_FIELDS) | {"semester_id"}


def _parse_term_date(value, field):
    if not isinstance(value, str):
        raise APIError("invalid_field", f"{field} must use YYYY-MM-DD format.")

    result = parse_date(value)

    if result is None or result.isoformat() != value:
        raise APIError("invalid_field", f"{field} must use YYYY-MM-DD format.")

    return result


def _parse_term_datetime(value, field):
    if not isinstance(value, str):
        raise APIError(
            "invalid_field",
            f"{field} must be an ISO 8601 date-time string.",
        )

    result = parse_datetime(value)

    if result is None:
        raise APIError(
            "invalid_field",
            f"{field} must be an ISO 8601 date-time string.",
        )

    if timezone.is_naive(result):
        result = timezone.make_aware(
            result,
            timezone.get_current_timezone(),
        )

    return result


def _term_values(payload, instance=None, partial=False):
    unknown_fields = set(payload) - _TERM_ALLOWED_FIELDS

    if unknown_fields:
        raise APIError(
            "unknown_fields",
            f"Unknown fields: {', '.join(sorted(unknown_fields))}.",
        )

    if not partial:
        missing_fields = set(_TERM_REQUIRED_FIELDS) - set(payload)

        if missing_fields:
            raise APIError(
                "missing_fields",
                f"Required fields are missing: {', '.join(sorted(missing_fields))}.",
            )

    values = {}

    for field in ("term_code", "academic_year"):
        if field in payload:
            value = payload[field]

            if not isinstance(value, str) or not value.strip():
                raise APIError(
                    "invalid_field",
                    f"{field} must be a non-empty string.",
                )

            values[field] = value.strip()
        elif instance is not None:
            values[field] = getattr(instance, field)

    for field in ("start_date", "end_date"):
        if field in payload:
            values[field] = _parse_term_date(payload[field], field)
        elif instance is not None:
            values[field] = getattr(instance, field)

    for field in _TERM_DATETIME_FIELDS:
        if field in payload:
            values[field] = _parse_term_datetime(payload[field], field)
        elif instance is not None:
            values[field] = getattr(instance, field)

    if "semester_id" in payload:
        semester_id = payload["semester_id"]

        if semester_id is None or semester_id == "":
            values["semester"] = None
        else:
            if isinstance(semester_id, bool):
                raise APIError("invalid_semester", "semester_id must be an integer.")

            try:
                parsed_id = int(semester_id)
            except (TypeError, ValueError):
                raise APIError("invalid_semester", "semester_id must be an integer.")

            if str(parsed_id) != str(semester_id).strip() or parsed_id < 1:
                raise APIError("invalid_semester", "semester_id must be a positive integer.")

            semester = Constant.objects.filter(
                pk=parsed_id,
                category="semester",
                is_active=True,
            ).first()

            if semester is None:
                raise APIError(
                    "semester_not_found",
                    "The selected active semester does not exist.",
                    404,
                )

            values["semester"] = semester

    elif instance is not None:
        values["semester"] = instance.semester
    else:
        values["semester"] = None

    return values


def _raise_term_validation(error):
    details = getattr(error, "message_dict", None)

    if details:
        message = "; ".join(
            f"{field}: {', '.join(messages)}"
            for field, messages in details.items()
        )
    else:
        message = "; ".join(error.messages)

    raise APIError("invalid_term", message)


# --------------------------------------------------
# Create and update
# --------------------------------------------------

def save_term(payload, instance=None, partial=False):
    """Validate and atomically create or update a term."""

    values = _term_values(
        payload,
        instance=instance,
        partial=partial,
    )

    try:
        with transaction.atomic():
            term = instance or Term()

            for field, value in values.items():
                setattr(term, field, value)

            # New terms are created inactive. Activation has its own operation.
            if instance is None:
                term.is_active = False

            term.full_clean()
            term.save()

    except ValidationError as error:
        _raise_term_validation(error)
    except IntegrityError as error:
        raise APIError(
            "term_conflict",
            "A term with conflicting unique values already exists.",
            409,
        ) from error

    return Term.objects.select_related("semester").get(pk=term.pk)


# --------------------------------------------------
# Term activation
# --------------------------------------------------

def set_term_active(term_id, is_active):
    """Activate one term while atomically deactivating any previously active term."""

    try:
        with transaction.atomic():
            terms = Term.objects.select_for_update()
            term = terms.filter(pk=term_id).first()

            if term is None:
                raise APIError(
                    "term_not_found",
                    "The requested term does not exist.",
                    404,
                )

            if is_active:
                terms.filter(is_active=True).exclude(pk=term.pk).update(
                    is_active=False
                )

            term.is_active = is_active
            term.full_clean()
            term.save(update_fields=["is_active"])

    except ValidationError as error:
        _raise_term_validation(error)
    except IntegrityError as error:
        raise APIError(
            "term_activation_conflict",
            "The term status conflicts with another active term.",
            409,
        ) from error

    return Term.objects.select_related("semester").get(pk=term.pk)

# --------------------------------------------------
# Course offering serialization
# --------------------------------------------------

def course_offering_payload(offering):
    return {
        "id": offering.pk,
        "lesson": {
            "id": offering.lesson_id,
            "code": offering.lesson.lesson_code,
            "title": offering.lesson.title,
        },
        "term": {
            "id": offering.term_id,
            "code": offering.term.term_code,
            "academic_year": offering.term.academic_year,
        },
        "teacher": {
            "id": offering.teacher_id,
            "code": offering.teacher.teacher_code,
            "name": offering.teacher.person.full_name,
        },
        "capacity": offering.capacity,
        "remaining_capacity": offering.remaining_capacity,
        "day_of_week": (
            {
                "id": offering.day_of_week_id,
                "code": offering.day_of_week.code,
                "label": offering.day_of_week.label,
            }
            if offering.day_of_week_id else None
        ),
        "start_time": offering.start_time.isoformat(),
        "end_time": offering.end_time.isoformat(),
        "duration_minutes": offering.duration_minutes,
        "classroom": {
            "id": offering.classroom_id,
            "building_name": offering.classroom.building_name,
            "room_number": offering.classroom.room_number,
            "capacity": offering.classroom.capacity,
            "classroom_type": offering.classroom.classroom_type,
        },
        "exam_date": (
            offering.exam_date.isoformat() if offering.exam_date else None
        ),
        "exam_time": (
            offering.exam_time.isoformat() if offering.exam_time else None
        ),
        "is_active": offering.is_active,
        "created_at": offering.created_at.isoformat(),
    }


# --------------------------------------------------
# Course offering input validation
# --------------------------------------------------

_OFFERING_REQUIRED_FIELDS = {
    "lesson_id",
    "term_id",
    "teacher_id",
    "capacity",
    "start_time",
    "end_time",
    "classroom_id",
}

_OFFERING_ALLOWED_FIELDS = _OFFERING_REQUIRED_FIELDS | {
    "day_of_week_id",
    "exam_date",
    "exam_time",
}


def _offering_positive_id(value, field):
    if isinstance(value, bool):
        raise APIError(
            "invalid_field",
            f"{field} must be a positive integer.",
        )

    try:
        parsed = int(value)
    except (TypeError, ValueError):
        raise APIError(
            "invalid_field",
            f"{field} must be a positive integer.",
        )

    if str(parsed) != str(value).strip() or parsed < 1:
        raise APIError(
            "invalid_field",
            f"{field} must be a positive integer.",
        )

    return parsed


def _offering_capacity(value):
    capacity = _offering_positive_id(value, "capacity")
    return capacity


def _offering_time(value, field):
    if not isinstance(value, str):
        raise APIError(
            "invalid_time",
            f"{field} must use HH:MM or HH:MM:SS format.",
        )

    result = parse_time(value)

    if result is None:
        raise APIError(
            "invalid_time",
            f"{field} must use HH:MM or HH:MM:SS format.",
        )

    return result


def _offering_date(value, field):
    if value is None or value == "":
        return None

    if not isinstance(value, str):
        raise APIError(
            "invalid_date",
            f"{field} must use YYYY-MM-DD format.",
        )

    result = parse_date(value)

    if result is None or result.isoformat() != value:
        raise APIError(
            "invalid_date",
            f"{field} must use YYYY-MM-DD format.",
        )

    return result


def _offering_values(payload, instance=None, partial=False):
    unknown_fields = set(payload) - _OFFERING_ALLOWED_FIELDS

    if unknown_fields:
        raise APIError(
            "unknown_fields",
            f"Unknown fields: {', '.join(sorted(unknown_fields))}.",
        )

    if not partial:
        missing_fields = _OFFERING_REQUIRED_FIELDS - set(payload)

        if missing_fields:
            raise APIError(
                "missing_fields",
                "Required fields are missing: "
                + ", ".join(sorted(missing_fields)),
            )

    values = {}

    foreign_keys = {
        "lesson_id": ("lesson", Lesson),
        "term_id": ("term", Term),
        "teacher_id": ("teacher", Teacher),
        "classroom_id": ("classroom", Classroom),
    }

    for field, (attribute, model) in foreign_keys.items():
        if field in payload:
            object_id = _offering_positive_id(payload[field], field)
            related_object = model.objects.filter(pk=object_id).first()

            if related_object is None:
                raise APIError(
                    f"{attribute}_not_found",
                    f"The selected {attribute} does not exist.",
                    404,
                )

            values[attribute] = related_object

        elif instance is not None:
            values[attribute] = getattr(instance, attribute)

    if "capacity" in payload:
        values["capacity"] = _offering_capacity(payload["capacity"])
    elif instance is not None:
        values["capacity"] = instance.capacity

    for field in ("start_time", "end_time"):
        if field in payload:
            values[field] = _offering_time(payload[field], field)
        elif instance is not None:
            values[field] = getattr(instance, field)

    if "day_of_week_id" in payload:
        day_id = payload["day_of_week_id"]

        if day_id is None or day_id == "":
            values["day_of_week"] = None
        else:
            day_id = _offering_positive_id(day_id, "day_of_week_id")

            day = Constant.objects.filter(
                pk=day_id,
                category="day_of_week",
                is_active=True,
            ).first()

            if day is None:
                raise APIError(
                    "day_not_found",
                    "The selected active day of week does not exist.",
                    404,
                )

            values["day_of_week"] = day

    elif instance is not None:
        values["day_of_week"] = instance.day_of_week
    else:
        values["day_of_week"] = None

    for field in ("exam_date", "exam_time"):
        if field in payload:
            if field == "exam_date":
                values[field] = _offering_date(payload[field], field)
            elif payload[field] is None or payload[field] == "":
                values[field] = None
            else:
                values[field] = _offering_time(payload[field], field)

        elif instance is not None:
            values[field] = getattr(instance, field)
        else:
            values[field] = None

    if (values["exam_date"] is None) != (values["exam_time"] is None):
        raise APIError(
            "invalid_exam_schedule",
            "exam_date and exam_time must either both be provided or both be empty.",
        )

    return values


# --------------------------------------------------
# Course offering business validation
# --------------------------------------------------

def _validate_offering_relationships(values):
    lesson = values["lesson"]
    teacher = values["teacher"]
    classroom = values["classroom"]
    capacity = values["capacity"]
    start_time = values["start_time"]
    end_time = values["end_time"]

    if not lesson.is_active:
        raise APIError(
            "inactive_lesson",
            "An inactive lesson cannot be scheduled.",
            400,
        )

    if lesson.department_id != teacher.department_id:
        raise APIError(
            "teacher_department_mismatch",
            "The teacher and lesson must belong to the same department.",
            400,
        )

    if classroom.capacity <= 0:
        raise APIError(
            "invalid_classroom_capacity",
            "The classroom capacity must be greater than zero.",
            400,
        )

    if capacity > classroom.capacity:
        raise APIError(
            "capacity_exceeds_classroom",
            "Offering capacity cannot exceed classroom capacity.",
            400,
        )

    if end_time <= start_time:
        raise APIError(
            "invalid_time_range",
            "The end time must be later than the start time.",
            400,
        )


def _check_offering_schedule_conflicts(values, instance=None):
    day = values["day_of_week"]

    # Without a selected weekday, recurring schedule conflicts
    # cannot be determined.
    if day is None:
        return

    conflicts = CourseOffering.objects.filter(
        term=values["term"],
        day_of_week=day,
        is_active=True,
        start_time__lt=values["end_time"],
        end_time__gt=values["start_time"],
    )

    if instance is not None:
        conflicts = conflicts.exclude(pk=instance.pk)

    teacher_conflict = conflicts.filter(
        teacher=values["teacher"]
    ).exists()

    if teacher_conflict:
        raise APIError(
            "teacher_schedule_conflict",
            "The teacher already has an active offering during this time.",
            409,
        )

    classroom_conflict = conflicts.filter(
        classroom=values["classroom"]
    ).exists()

    if classroom_conflict:
        raise APIError(
            "classroom_schedule_conflict",
            "The classroom is already occupied during this time.",
            409,
        )


def _raise_offering_validation(error):
    details = getattr(error, "message_dict", None)

    if details:
        message = "; ".join(
            f"{field}: {', '.join(messages)}"
            for field, messages in details.items()
        )
    else:
        message = "; ".join(error.messages)

    raise APIError("invalid_offering", message)


# --------------------------------------------------
# Course offering create and update
# --------------------------------------------------

def save_offering(payload, instance=None, partial=False):
    """Create or update a course offering after business validation."""

    values = _offering_values(
        payload,
        instance=instance,
        partial=partial,
    )

    try:
        with transaction.atomic():
            # Lock the related scheduling resources before checking conflicts.
            Term.objects.select_for_update().get(pk=values["term"].pk)
            Teacher.objects.select_for_update().get(pk=values["teacher"].pk)
            Classroom.objects.select_for_update().get(pk=values["classroom"].pk)

            _validate_offering_relationships(values)

            offering = instance or CourseOffering()

            for field, value in values.items():
                setattr(offering, field, value)

            _check_offering_schedule_conflicts(values, instance=instance)

            offering.full_clean()

            if instance is None:
                offering.is_active = True

            offering.save()

    except ValidationError as error:
        _raise_offering_validation(error)

    except IntegrityError as error:
        raise APIError(
            "offering_conflict",
            "The offering conflicts with an existing record or database constraint.",
            409,
        ) from error

    return (
        CourseOffering.objects
        .select_related(
            "lesson",
            "term",
            "teacher__person",
            "day_of_week",
            "classroom",
        )
        .get(pk=offering.pk)
    )


# --------------------------------------------------
# Course offering activation
# --------------------------------------------------

def set_offering_active(offering_id, is_active):
    """Activate or deactivate a course offering."""

    try:
        with transaction.atomic():
            offering = (
                CourseOffering.objects
                .select_for_update()
                .select_related(
                    "lesson",
                    "term",
                    "teacher",
                    "classroom",
                    "day_of_week",
                )
                .filter(pk=offering_id)
                .first()
            )

            if offering is None:
                raise APIError(
                    "offering_not_found",
                    "The requested course offering does not exist.",
                    404,
                )

            if is_active:
                values = {
                    "lesson": offering.lesson,
                    "term": offering.term,
                    "teacher": offering.teacher,
                    "classroom": offering.classroom,
                    "capacity": offering.capacity,
                    "start_time": offering.start_time,
                    "end_time": offering.end_time,
                    "day_of_week": offering.day_of_week,
                }

                _validate_offering_relationships(values)
                _check_offering_schedule_conflicts(values, instance=offering)

            offering.is_active = is_active
            offering.save(update_fields=["is_active"])

    except ValidationError as error:
        _raise_offering_validation(error)

    except IntegrityError as error:
        raise APIError(
            "offering_status_conflict",
            "The offering status conflicts with an existing record.",
            409,
        ) from error

    return (
        CourseOffering.objects
        .select_related(
            "lesson",
            "term",
            "teacher__person",
            "day_of_week",
            "classroom",
        )
        .get(pk=offering.pk)
    )