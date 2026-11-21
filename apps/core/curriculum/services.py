"""Business services for curriculum API."""

from django.db.models import Q

from apps.core.models import Curriculum


def curriculum_queryset_for_user(user):
    """
    Return curriculum records accessible to the authenticated user.

    Admin:
        All active and inactive curriculum records.

    Student:
        Only active curriculum records belonging to the student's own fields.

    Professor:
        Only active curriculum records belonging to fields in the professor's
        department.
    """

    queryset = Curriculum.objects.select_related(
        "field",
        "field__department",
        "field__department__faculty",
        "lesson",
        "lesson__department",
        "lesson__lesson_type",
        "requirement_type",
    )

    from apps.core.accounts.services import role_codes_for

    roles = role_codes_for(user)

    # Administrators can access all curriculum records.
    if user.is_superuser or "admin" in roles:
        return queryset

    # Non-administrators can only access active curriculum records.
    queryset = queryset.filter(is_active=True)

    access_filter = Q(pk__in=[])

    # Students can access curricula belonging to their own fields.
    if "student" in roles:
        access_filter |= Q(field__students__person=user)

    # Professors can access curricula belonging to their department.
    if "professor" in roles:
        access_filter |= Q(field__department__teachers__person=user)

    return queryset.filter(access_filter).distinct()


def curriculum_payload(curriculum):
    """Serialize one curriculum record without exposing sensitive data."""

    field = curriculum.field
    department = field.department
    faculty = department.faculty

    lesson = curriculum.lesson
    lesson_type = lesson.lesson_type
    requirement_type = curriculum.requirement_type

    return {
        "id": curriculum.curriculum_id,
        "field": {
            "id": field.pk,
            "name": field.field_name,
            "code": field.field_code,
        },
        "department": {
            "id": department.pk,
            "name": department.department_name,
            "code": department.department_code,
        },
        "faculty": {
            "id": faculty.pk,
            "name": faculty.faculty_name,
            "code": faculty.faculty_code,
        },
        "lesson": {
            "id": lesson.pk,
            "code": lesson.lesson_code,
            "title": lesson.title,
            "theory_units": lesson.theory_units,
            "practical_units": lesson.practical_units,
            "total_units": (
                lesson.theory_units + lesson.practical_units
            ),
            "type": (
                {
                    "id": lesson_type.pk,
                    "code": lesson_type.code,
                    "label": lesson_type.label,
                }
                if lesson_type else None
            ),
        },
        "requirement_type": (
            {
                "id": requirement_type.pk,
                "code": requirement_type.code,
                "label": requirement_type.label,
            }
            if requirement_type else None
        ),
        "recommended_term": curriculum.recommended_term,
        "calculated_units": curriculum.calculated_units,
        "is_active": curriculum.is_active,
        "created_at": curriculum.created_at.isoformat(),
    }
