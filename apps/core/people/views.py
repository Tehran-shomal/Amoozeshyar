from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_GET

from apps.core.accounts.permissions import role_required
from apps.core.api import error_response
from apps.core.system_settings.reader import get_pagination_settings
from apps.core.models import Student, Teacher


def constant_payload(value):
    if value is None:
        return None

    return {
        "id": value.pk,
        "code": value.code,
        "label": value.label,
    }


@require_GET
@role_required("student")
def my_student_profiles_view(request):
    """
    Return the authenticated student's educational profiles.
    """

    students = (
        Student.objects
        .filter(person=request.user)
        .select_related(
            "person",
            "educational_level",
            "field",
            "field__department",
            "status",
            "admission_type",
        )
        .order_by("student_code")
    )

    results = []

    for student in students:
        results.append({
            "id": student.id,
            "student_code": student.student_code,

            "person": {
                "id": student.person_id,
                "full_name": student.person.full_name,
            },

            "educational_level": constant_payload(
                student.educational_level
            ),

            "field": {
                "id": student.field_id,
                "name": student.field.field_name,
                "code": student.field.field_code,
                "department": {
                    "id": student.field.department_id,
                    "name": student.field.department.department_name,
                    "code": student.field.department.department_code,
                },
            },

            "status": constant_payload(student.status),
            "admission_type": constant_payload(student.admission_type),

            "academic": {
                "previous_term_gpa": student.previous_term_gpa,
                "total_gpa": student.total_gpa,
                "passed_units": student.passed_units,
                "completed_terms": student.completed_terms,
                "remaining_terms": student.remaining_terms,
                "is_on_probation": student.is_on_probation,
                "max_allowed_units": student.max_allowed_units,
            },

            "financial": {
                "tuition_debt": student.tuition_debt,
                "can_register_courses": student.can_register_courses,
            },

            "application_date": student.application_date,
        })

    return JsonResponse({
        "success": True,
        "count": len(results),
        "results": results,
    })
@require_GET
@role_required("admin")
def students_list_view(request):
    """
    Return a searchable, filterable and paginated list of students.

    Supported query parameters:
        search
        student_code
        educational_level
        status
        field
        department
        page
        page_size
    """

    students = (
        Student.objects
        .select_related(
            "person",
            "educational_level",
            "field",
            "field__department",
            "status",
            "admission_type",
        )
        .order_by("student_code")
    )

    # General search: student code, first name, last name,
    # username and email.
    search = request.GET.get("search", "").strip()

    if search:
        students = students.filter(
            Q(student_code__icontains=search)
            | Q(person__first_name__icontains=search)
            | Q(person__last_name__icontains=search)
            | Q(person__username__icontains=search)
            | Q(person__email__icontains=search)
        )

    # Exact student code filter.
    student_code = request.GET.get("student_code", "").strip()

    if student_code:
        students = students.filter(student_code__iexact=student_code)

    # Educational level: accepts database ID or constant code/label.
    educational_level = request.GET.get("educational_level", "").strip()

    if educational_level:
        level_filter = Q(educational_level__code__iexact=educational_level)

        if educational_level.isdigit():
            level_filter |= Q(educational_level_id=int(educational_level))

        level_filter |= Q(educational_level__label__iexact=educational_level)
        students = students.filter(level_filter)

    # Student status: accepts database ID or constant code/label.
    status = request.GET.get("status", "").strip()

    if status:
        status_filter = (
            Q(status__code__iexact=status)
            | Q(status__label__iexact=status)
        )

        if status.isdigit():
            status_filter |= Q(status_id=int(status))

        students = students.filter(status_filter)

    # Field: accepts database ID, field code or field name.
    field = request.GET.get("field", "").strip()

    if field:
        field_filter = (
            Q(field__field_code__iexact=field)
            | Q(field__field_name__icontains=field)
        )

        if field.isdigit():
            field_filter |= Q(field_id=int(field))

        students = students.filter(field_filter)

    # Department: accepts database ID, department code or department name.
    department = request.GET.get("department", "").strip()

    if department:
        department_filter = (
            Q(field__department__department_code__iexact=department)
            | Q(field__department__department_name__icontains=department)
        )

        if department.isdigit():
            department_filter |= Q(field__department_id=int(department))

        students = students.filter(department_filter)

    # Read pagination limits from persisted system settings.
    default_page_size, max_page_size = get_pagination_settings()

    # Validate pagination parameters.
    try:
        page_number = int(request.GET.get("page", "1"))
        page_size = int(
            request.GET.get("page_size", str(default_page_size))
        )
    except (TypeError, ValueError):
        return error_response(
            "invalid_pagination",
            "Page and page_size must be valid integers.",
            400,
        )

    if page_number < 1:
        return error_response(
            "invalid_pagination",
            "Page must be greater than zero.",
            400,
        )

    if page_size < 1 or page_size > max_page_size:
        return error_response(
            "invalid_pagination",
            "Page size must be between 1 and 100.",
            400,
        )

    paginator = Paginator(students, page_size)

    try:
        current_page = paginator.page(page_number)
    except (EmptyPage, PageNotAnInteger):
        return error_response(
            "page_not_found",
            "The requested page does not exist.",
            404,
        )

    results = []

    for student in current_page.object_list:
        results.append({
            "id": student.id,
            "student_code": student.student_code,

            "person": {
                "id": student.person_id,
                "username": student.person.username,
                "full_name": student.person.full_name,
                "email": student.person.email,
            },

            "educational_level": constant_payload(
                student.educational_level
            ),

            "field": {
                "id": student.field_id,
                "name": student.field.field_name,
                "code": student.field.field_code,
                "department": {
                    "id": student.field.department_id,
                    "name": student.field.department.department_name,
                    "code": student.field.department.department_code,
                },
            },

            "status": constant_payload(student.status),
            "admission_type": constant_payload(student.admission_type),

            "academic": {
                "total_gpa": student.total_gpa,
                "passed_units": student.passed_units,
                "completed_terms": student.completed_terms,
            },

            "financial": {
                "tuition_debt": student.tuition_debt,
            },

            "application_date": student.application_date,
        })

    return JsonResponse({
        "success": True,
        "count": len(results),
        "total_count": paginator.count,
        "pagination": {
            "page": current_page.number,
            "page_size": page_size,
            "total_pages": paginator.num_pages,
            "has_next": current_page.has_next(),
            "has_previous": current_page.has_previous(),
        },
        "results": results,
    })

@require_GET
@role_required("admin")
def student_detail_view(request, student_id):
    student = get_object_or_404(
        Student.objects.select_related(
            "person",
            "educational_level",
            "field",
            "field__department",
            "status",
            "admission_type",
        ),
        pk=student_id,
    )

    return JsonResponse({
        "success": True,
        "student": {
            "id": student.id,
            "student_code": student.student_code,

            "person": {
                "id": student.person_id,
                "username": student.person.username,
                "full_name": student.person.full_name,
                "email": student.person.email,
            },

            "educational_level": constant_payload(
                student.educational_level
            ),

            "field": {
                "id": student.field_id,
                "name": student.field.field_name,
                "code": student.field.field_code,
                "department": {
                    "id": student.field.department_id,
                    "name": student.field.department.department_name,
                    "code": student.field.department.department_code,
                },
            },

            "status": constant_payload(student.status),
            "admission_type": constant_payload(student.admission_type),

            "academic": {
                "previous_term_gpa": student.previous_term_gpa,
                "total_gpa": student.total_gpa,
                "passed_units": student.passed_units,
                "completed_terms": student.completed_terms,
                "remaining_terms": student.remaining_terms,
                "is_on_probation": student.is_on_probation,
                "max_allowed_units": student.max_allowed_units,
            },

            "financial": {
                "tuition_debt": student.tuition_debt,
                "can_register_courses": student.can_register_courses,
            },

            "application_date": student.application_date,
        },
    })



# =========================================================
# TEACHER APIs
# =========================================================

def teacher_payload(teacher):
    """
    Serialize a teacher without exposing sensitive personal data.
    """

    return {
        "id": teacher.pk,
        "teacher_code": teacher.teacher_code,

        "person": {
            "id": teacher.person_id,
            "username": teacher.person.username,
            "full_name": teacher.person.full_name,
            "email": teacher.person.email,
        },

        "department": {
            "id": teacher.department_id,
            "name": teacher.department.department_name,
            "code": teacher.department.department_code,

            "faculty": {
                "id": teacher.department.faculty_id,
                "name": teacher.department.faculty.faculty_name,
                "code": teacher.department.faculty.faculty_code,
            },
        },

        "academic_rank": constant_payload(teacher.academic_rank),

        "hire_date": teacher.hire_date,
        "years_of_service": teacher.years_of_service,
    }


@require_GET
@role_required("professor")
def my_teacher_profile_view(request):
    """
    Return the authenticated professor's profile.
    """

    teacher = get_object_or_404(
        Teacher.objects.select_related(
            "person",
            "department",
            "department__faculty",
            "academic_rank",
        ),
        person=request.user,
    )

    return JsonResponse({
        "success": True,
        "teacher": teacher_payload(teacher),
    })


@require_GET
@role_required("admin")
def teachers_list_view(request):
    """
    Return a searchable, filterable and paginated list of teachers.

    Supported query parameters:
        search
        teacher_code
        department
        academic_rank
        page
        page_size
    """

    teachers = (
        Teacher.objects
        .select_related(
            "person",
            "department",
            "department__faculty",
            "academic_rank",
        )
        .order_by("teacher_code")
    )

    # General search.
    search = request.GET.get("search", "").strip()

    if search:
        teachers = teachers.filter(
            Q(teacher_code__icontains=search)
            | Q(person__first_name__icontains=search)
            | Q(person__last_name__icontains=search)
            | Q(person__username__icontains=search)
            | Q(person__email__icontains=search)
        )

    # Exact teacher code filter.
    teacher_code = request.GET.get("teacher_code", "").strip()

    if teacher_code:
        teachers = teachers.filter(
            teacher_code__iexact=teacher_code
        )

    # Department filter: accepts ID, department code or department name.
    department = request.GET.get("department", "").strip()

    if department:
        department_filter = (
            Q(department__department_code__iexact=department)
            | Q(department__department_name__icontains=department)
        )

        if department.isdigit():
            department_filter |= Q(department_id=int(department))

        teachers = teachers.filter(department_filter)

    # Academic rank filter: accepts ID, constant code or label.
    academic_rank = request.GET.get("academic_rank", "").strip()

    if academic_rank:
        rank_filter = (
            Q(academic_rank__code__iexact=academic_rank)
            | Q(academic_rank__label__iexact=academic_rank)
        )

        if academic_rank.isdigit():
            rank_filter |= Q(academic_rank_id=int(academic_rank))

        teachers = teachers.filter(rank_filter)

    # Read pagination limits from persisted system settings.
    default_page_size, max_page_size = get_pagination_settings()

    # Validate pagination parameters.
    try:
        page_number = int(request.GET.get("page", "1"))
        page_size = int(
            request.GET.get("page_size", str(default_page_size))
        )
    except (TypeError, ValueError):
        return error_response(
            "invalid_pagination",
            "Page and page_size must be valid integers.",
            400,
        )

    if page_number < 1:
        return error_response(
            "invalid_pagination",
            "Page must be greater than zero.",
            400,
        )

    if page_size < 1 or page_size > max_page_size:
        return error_response(
            "invalid_pagination",
            "Page size must be between 1 and 100.",
            400,
        )

    paginator = Paginator(teachers, page_size)

    try:
        current_page = paginator.page(page_number)
    except (EmptyPage, PageNotAnInteger):
        return error_response(
            "page_not_found",
            "The requested page does not exist.",
            404,
        )

    results = [
        teacher_payload(teacher)
        for teacher in current_page.object_list
    ]

    return JsonResponse({
        "success": True,
        "count": len(results),
        "total_count": paginator.count,
        "pagination": {
            "page": current_page.number,
            "page_size": page_size,
            "total_pages": paginator.num_pages,
            "has_next": current_page.has_next(),
            "has_previous": current_page.has_previous(),
        },
        "results": results,
    })


@require_GET
@role_required("admin")
def teacher_detail_view(request, teacher_id):
    """
    Return the details of a specific teacher.
    """

    teacher = get_object_or_404(
        Teacher.objects.select_related(
            "person",
            "department",
            "department__faculty",
            "academic_rank",
        ),
        pk=teacher_id,
    )

    return JsonResponse({
        "success": True,
        "teacher": teacher_payload(teacher),
    })

# =========================================================
# TEACHER APIs
# =========================================================
