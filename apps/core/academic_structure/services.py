"""Access-control services for academic structure APIs."""

from apps.core.api import APIError
from apps.core.accounts.services import (
    current_account_role,
    current_academic_management_scope,
)
from apps.core.models import (
    AcademicManagementScope,
    Department,
    Faculty,
    Field,
    Lesson,
    Prerequisite,
    Student,
    Teacher,
)


MANAGEMENT_ROLES = {
    "admin",
    "faculty_manager",
    "department_manager",
}

READ_ONLY_ROLES = {
    "student",
    "professor",
}


def resolve_academic_structure_access(request, write=False):
    """
    Resolve the exact role and academic scope of the authenticated session.

    Management permissions are based on the exact UserAccount stored
    in the session, never on all roles belonging to the Person.
    """

    user = request.user

    if not user.is_authenticated:
        raise APIError(
            "authentication_required",
            "Authentication is required.",
            401,
        )

    # Django superusers have unrestricted access.
    if user.is_superuser:
        return {
            "role": "admin",
            "scope": None,
        }

    # Resolve the role from the exact authenticated UserAccount.
    role = current_account_role(request)

    if role is None:
        raise APIError(
            "permission_denied",
            "No valid active role account was found in this session.",
            403,
        )

    allowed_roles = MANAGEMENT_ROLES | READ_ONLY_ROLES

    if role not in allowed_roles:
        raise APIError(
            "permission_denied",
            "This role cannot access academic structure.",
            403,
        )

    if write and role not in MANAGEMENT_ROLES:
        raise APIError(
            "permission_denied",
            "This role has read-only access to academic structure.",
            403,
        )

    # Faculty and department managers must have a valid scope.
    if role in {"faculty_manager", "department_manager"}:
        scope = current_academic_management_scope(request)

        if scope is None:
            raise APIError(
                "academic_scope_not_configured",
                "No valid academic management scope is configured.",
                403,
            )

        return {
            "role": role,
            "scope": scope,
        }

    return {
        "role": role,
        "scope": None,
    }


def academic_department_queryset(request, access=None):
    """Return departments accessible to the current user."""

    access = access or resolve_academic_structure_access(request)
    role = access["role"]
    scope = access["scope"]

    queryset = Department.objects.select_related("faculty")

    if role == "admin":
        return queryset

    if role == "faculty_manager":
        return queryset.filter(faculty_id=scope.faculty_id)

    if role in {"department_manager", "professor"}:
        if role == "department_manager":
            department_ids = [scope.department_id]
        else:
            department_ids = (
                Teacher.objects
                .filter(person=request.user)
                .values("department_id")
            )

        return queryset.filter(pk__in=department_ids)

    if role == "student":
        student_departments = (
            Student.objects
            .filter(person=request.user)
            .values("field__department_id")
        )

        return queryset.filter(pk__in=student_departments).distinct()

    return queryset.none()


def academic_faculty_queryset(request, access=None):
    """Return faculties accessible to the current user."""

    access = access or resolve_academic_structure_access(request)
    role = access["role"]
    scope = access["scope"]

    queryset = Faculty.objects.all()

    if role == "admin":
        return queryset

    if role == "faculty_manager":
        return queryset.filter(pk=scope.faculty_id)

    departments = academic_department_queryset(
        request,
        access=access,
    )

    return queryset.filter(
        departments__in=departments
    ).distinct()


def academic_field_queryset(request, access=None):
    """Return fields accessible to the current user."""

    access = access or resolve_academic_structure_access(request)
    role = access["role"]
    scope = access["scope"]

    queryset = Field.objects.select_related(
        "department",
        "department__faculty",
    )

    if role == "admin":
        return queryset

    if role == "faculty_manager":
        return queryset.filter(
            department__faculty_id=scope.faculty_id
        )

    if role in {"department_manager", "professor"}:
        if role == "department_manager":
            department_ids = [scope.department_id]
        else:
            department_ids = (
                Teacher.objects
                .filter(person=request.user)
                .values("department_id")
            )

        return queryset.filter(
            department_id__in=department_ids
        )

    if role == "student":
        student_fields = Student.objects.filter(
            person=request.user
        ).values("field_id")

        return queryset.filter(
            pk__in=student_fields
        ).distinct()

    return queryset.none()


def academic_lesson_queryset(request, access=None):
    """Return lessons accessible to the current user."""

    access = access or resolve_academic_structure_access(request)
    role = access["role"]
    scope = access["scope"]

    queryset = Lesson.objects.select_related(
        "department",
        "department__faculty",
        "lesson_type",
    )

    if role == "admin":
        return queryset

    if role == "faculty_manager":
        return queryset.filter(
            department__faculty_id=scope.faculty_id
        )

    if role == "department_manager":
        return queryset.filter(
            department_id=scope.department_id
        )

    if role == "student":
        return queryset.filter(
            curriculums__field__students__person=request.user,
            curriculums__field__is_active=True,
            curriculums__is_active=True,
        ).distinct()

    if role == "professor":
        departments = academic_department_queryset(
            request,
            access=access,
        )
        return queryset.filter(
            department__in=departments
        ).distinct()

    return queryset.none()


def academic_prerequisite_queryset(request, access=None):
    """
    Return prerequisites only when both related lessons are accessible.

    Checking both sides prevents users from discovering an inaccessible
    lesson through its prerequisite relationship.
    """

    access = access or resolve_academic_structure_access(request)

    lessons = academic_lesson_queryset(
        request,
        access=access,
    )

    return (
        Prerequisite.objects
        .select_related(
            "lesson",
            "lesson__department",
            "lesson__department__faculty",
            "prerequisite_lesson",
            "prerequisite_lesson__department",
            "prerequisite_type",
        )
        .filter(
            lesson__in=lessons,
            prerequisite_lesson__in=lessons,
        )
    )