"""JSON endpoints for term and course-offering scheduling."""

from django.db.models import Q
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import (
    require_GET,
    require_http_methods,
    require_POST,
)

from apps.core.api import APIError, error_response, read_json
from apps.core.accounts.permissions import account_role_required
from apps.core.accounts.services import (
    current_account_role,
    current_academic_management_scope,
)
from apps.core.models import CourseOffering, Term
from apps.core.scheduling.services import (
    course_offering_payload,
    get_active_term,
    list_offerings,
    save_offering,
    save_term,
    set_offering_active,
    set_term_active,
    term_payload,
)


def _term_payload(term, now):
    """Preserve the response format of the existing active-term endpoint."""
    if term is None:
        return None

    return {
        "id": term.pk,
        "term_code": term.term_code,
        "academic_year": term.academic_year,
        "start_date": term.start_date.isoformat(),
        "end_date": term.end_date.isoformat(),
        "registration_open": term.registration_start <= now <= term.registration_end,
        "add_drop_open": term.add_drop_start <= now <= term.add_drop_end,
        "emergency_drop_open": (
            term.emergency_drop_start <= now <= term.emergency_drop_end
        ),
    }


def _authentication_error(request):
    """Keep portal read endpoints private to authenticated sessions."""
    if request.user.is_authenticated:
        return None

    return error_response(
        "authentication_required",
        "Authentication is required.",
        401,
    )


def _get_term_or_error(term_id):
    term = Term.objects.select_related("semester").filter(pk=term_id).first()

    if term is None:
        return None, error_response(
            "term_not_found",
            "The requested term does not exist.",
            404,
        )

    return term, None


def _pagination(request):
    try:
        page = int(request.GET.get("page", "1"))
        page_size = int(request.GET.get("page_size", "20"))
    except (TypeError, ValueError):
        raise APIError(
            "invalid_pagination",
            "page and page_size must be integers.",
        )

    if page < 1 or page_size < 1:
        raise APIError(
            "invalid_pagination",
            "page and page_size must be positive integers.",
        )

    return page, min(page_size, 100)


def _api_error_response(error):
    return error_response(
        error.code,
        error.message,
        error.status_code,
    )

def _offering_queryset_for_account(request):
    role = current_account_role(request)

    queryset = CourseOffering.objects.select_related(
        "lesson",
        "lesson__department",
        "lesson__department__faculty",
        "term",
        "teacher__person",
        "day_of_week",
        "classroom",
    )

    if role == "admin":
        return queryset

    if role == "faculty_manager":
        scope = current_academic_management_scope(request)

        if scope is None:
            raise APIError(
                "management_scope_required",
                "A valid faculty management scope is required.",
                403,
            )

        return queryset.filter(
            lesson__department__faculty_id=scope.faculty_id
        )

    if role == "department_manager":
        scope = current_academic_management_scope(request)

        if scope is None:
            raise APIError(
                "management_scope_required",
                "A valid department management scope is required.",
                403,
            )

        return queryset.filter(
            lesson__department_id=scope.department_id
        )

    if role == "professor":
        return queryset.filter(
            teacher__person=request.user
        )

    raise APIError(
        "permission_denied",
        "You do not have permission to access course offerings.",
        403,
    )


def _ensure_offering_write_scope(request, lesson):
    role = current_account_role(request)

    if role == "admin":
        return

    scope = current_academic_management_scope(request)

    if role == "faculty_manager" and scope is not None:
        if lesson.department.faculty_id == scope.faculty_id:
            return

    if role == "department_manager" and scope is not None:
        if lesson.department_id == scope.department_id:
            return

    raise APIError(
        "permission_denied",
        "You cannot manage course offerings outside your academic scope.",
        403,
    )
# --------------------------------------------------
# Existing read endpoints
# --------------------------------------------------

@require_GET
def active_term_view(request):
    authentication_error = _authentication_error(request)
    if authentication_error:
        return authentication_error

    term = get_active_term()

    return JsonResponse({
        "term": _term_payload(term, timezone.now()),
    })


@require_GET
def offerings_view(request):
    authentication_error = _authentication_error(request)
    if authentication_error:
        return authentication_error

    term_code = request.GET.get("term")

    if term_code:
        term = Term.objects.filter(term_code=term_code).first()

        if term is None:
            return error_response(
                "term_not_found",
                "The requested term does not exist.",
                404,
            )
    else:
        term = None

    offerings = list_offerings(term)

    payload = [
        {
            "id": offering.pk,
            "term_id": offering.term_id,
            "lesson_code": offering.lesson.lesson_code,
            "title": offering.lesson.title,
            "theory_units": offering.lesson.theory_units,
            "practical_units": offering.lesson.practical_units,
            "total_units": (
                offering.lesson.theory_units
                + offering.lesson.practical_units
            ),
            "teacher": offering.teacher.person.full_name,
            "day_of_week": (
                offering.day_of_week.code
                if offering.day_of_week else None
            ),
            "start_time": offering.start_time.isoformat(),
            "end_time": offering.end_time.isoformat(),
            "classroom": {
                "building": offering.classroom.building_name,
                "room": offering.classroom.room_number,
            },
            "capacity": offering.capacity,
            "remaining_capacity": offering.remaining_capacity,
            "exam_date": (
                offering.exam_date.isoformat()
                if offering.exam_date else None
            ),
            "exam_time": (
                offering.exam_time.isoformat()
                if offering.exam_time else None
            ),
        }
        for offering in offerings
    ]

    return JsonResponse({"offerings": payload})

# --------------------------------------------------
# Course offering management: list and detail
# --------------------------------------------------

@require_GET
@account_role_required(
    "admin",
    "faculty_manager",
    "department_manager",
    "professor",
)
def offerings_manage_list_view(request):
    try:
        queryset = _offering_queryset_for_account(request)

        search = request.GET.get("search", "").strip()

        if search:
            queryset = queryset.filter(
                Q(lesson__lesson_code__icontains=search)
                | Q(lesson__title__icontains=search)
                | Q(teacher__person__first_name__icontains=search)
                | Q(teacher__person__last_name__icontains=search)
                | Q(classroom__building_name__icontains=search)
                | Q(classroom__room_number__icontains=search)
                | Q(term__term_code__icontains=search)
            )

        term_id = request.GET.get("term_id")

        if term_id:
            try:
                term_id = int(term_id)
                if term_id < 1:
                    raise ValueError
            except (TypeError, ValueError):
                raise APIError(
                    "invalid_term_id",
                    "term_id must be a positive integer.",
                )

            queryset = queryset.filter(term_id=term_id)

        lesson_id = request.GET.get("lesson_id")

        if lesson_id:
            try:
                lesson_id = int(lesson_id)
                if lesson_id < 1:
                    raise ValueError
            except (TypeError, ValueError):
                raise APIError(
                    "invalid_lesson_id",
                    "lesson_id must be a positive integer.",
                )

            queryset = queryset.filter(lesson_id=lesson_id)

        active_filter = request.GET.get("is_active")

        if active_filter is not None:
            normalized = active_filter.strip().lower()

            if normalized not in ("true", "false"):
                raise APIError(
                    "invalid_is_active",
                    "is_active must be true or false.",
                )

            queryset = queryset.filter(
                is_active=(normalized == "true")
            )

        page, page_size = _pagination(request)

        queryset = queryset.order_by(
            "-term__start_date",
            "lesson__lesson_code",
            "pk",
        )

        total = queryset.count()
        start = (page - 1) * page_size
        end = start + page_size

        offerings = queryset[start:end]

        return JsonResponse({
            "offerings": [
                course_offering_payload(offering)
                for offering in offerings
            ],
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": total,
                "total_pages": (
                    (total + page_size - 1) // page_size
                ),
            },
        })

    except APIError as error:
        return _api_error_response(error)


@require_GET
@account_role_required(
    "admin",
    "faculty_manager",
    "department_manager",
    "professor",
)
def offering_detail_view(request, offering_id):
    try:
        offering = (
            _offering_queryset_for_account(request)
            .filter(pk=offering_id)
            .first()
        )

        if offering is None:
            return error_response(
                "offering_not_found",
                "The requested course offering does not exist.",
                404,
            )

        return JsonResponse({
            "offering": course_offering_payload(offering)
        })

    except APIError as error:
        return _api_error_response(error)
# --------------------------------------------------
# Course offering creation
# --------------------------------------------------

@require_POST
@account_role_required(
    "admin",
    "faculty_manager",
    "department_manager",
)
def offering_create_view(request):
    try:
        payload = read_json(request)

        lesson_id = payload.get("lesson_id")

        if lesson_id is None:
            raise APIError(
                "missing_lesson_id",
                "lesson_id is required.",
            )

        try:
            lesson_id = int(lesson_id)
            if lesson_id < 1:
                raise ValueError
        except (TypeError, ValueError):
            raise APIError(
                "invalid_lesson_id",
                "lesson_id must be a positive integer.",
            )

        from apps.core.models import Lesson

        lesson = (
            Lesson.objects
            .select_related("department", "department__faculty")
            .filter(pk=lesson_id)
            .first()
        )

        if lesson is None:
            return error_response(
                "lesson_not_found",
                "The requested lesson does not exist.",
                404,
            )

        if not lesson.is_active:
            raise APIError(
                "inactive_lesson",
                "An inactive lesson cannot be scheduled.",
            )

        _ensure_offering_write_scope(request, lesson)

        offering = save_offering(payload)

        return JsonResponse(
            {
                "message": "Course offering created successfully.",
                "offering": course_offering_payload(offering),
            },
            status=201,
        )

    except APIError as error:
        return _api_error_response(error)

    except Exception:
        raise

# --------------------------------------------------
# Course offering update and status management
# --------------------------------------------------

@require_http_methods(["PUT", "PATCH"])
@account_role_required(
    "admin",
    "faculty_manager",
    "department_manager",
)
def offering_update_view(request, offering_id):
    try:
        queryset = _offering_queryset_for_account(request)
        offering = queryset.filter(pk=offering_id).first()

        if offering is None:
            return error_response(
                "offering_not_found",
                "The requested course offering does not exist.",
                404,
            )

        payload = read_json(request)

        lesson_id = payload.get("lesson_id", offering.lesson_id)

        try:
            lesson_id = int(lesson_id)
            if lesson_id < 1:
                raise ValueError
        except (TypeError, ValueError):
            raise APIError(
                "invalid_lesson_id",
                "lesson_id must be a positive integer.",
            )

        from apps.core.models import Lesson

        lesson = (
            Lesson.objects
            .select_related("department", "department__faculty")
            .filter(pk=lesson_id)
            .first()
        )

        if lesson is None:
            return error_response(
                "lesson_not_found",
                "The requested lesson does not exist.",
                404,
            )

        if not lesson.is_active:
            raise APIError(
                "inactive_lesson",
                "An inactive lesson cannot be scheduled.",
            )

        _ensure_offering_write_scope(request, lesson)

        updated_offering = save_offering(
            payload,
            instance=offering,
            partial=(request.method == "PATCH"),
        )

        return JsonResponse({
            "message": "Course offering updated successfully.",
            "offering": course_offering_payload(updated_offering),
        })

    except APIError as error:
        return _api_error_response(error)


@require_POST
@account_role_required(
    "admin",
    "faculty_manager",
    "department_manager",
)
def offering_activate_view(request, offering_id):
    try:
        offering = (
            _offering_queryset_for_account(request)
            .filter(pk=offering_id)
            .first()
        )

        if offering is None:
            return error_response(
                "offering_not_found",
                "The requested course offering does not exist.",
                404,
            )

        set_offering_active(offering.pk, True)

        offering.refresh_from_db()

        return JsonResponse({
            "message": "Course offering activated successfully.",
            "offering": course_offering_payload(offering),
        })

    except APIError as error:
        return _api_error_response(error)


@require_POST
@account_role_required(
    "admin",
    "faculty_manager",
    "department_manager",
)
def offering_deactivate_view(request, offering_id):
    try:
        offering = (
            _offering_queryset_for_account(request)
            .filter(pk=offering_id)
            .first()
        )

        if offering is None:
            return error_response(
                "offering_not_found",
                "The requested course offering does not exist.",
                404,
            )

        set_offering_active(offering.pk, False)

        offering.refresh_from_db()

        return JsonResponse({
            "message": "Course offering deactivated successfully.",
            "offering": course_offering_payload(offering),
        })

    except APIError as error:
        return _api_error_response(error)
# --------------------------------------------------
# Term list and creation
# --------------------------------------------------

@require_GET
@account_role_required("admin")
def terms_list_view(request):
    try:
        page, page_size = _pagination(request)
    except APIError as error:
        return _api_error_response(error)

    queryset = Term.objects.select_related("semester").all()

    search = request.GET.get("search", "").strip()

    if search:
        queryset = queryset.filter(
            Q(term_code__icontains=search)
            | Q(academic_year__icontains=search)
            | Q(semester__code__icontains=search)
            | Q(semester__label__icontains=search)
        )

    active_filter = request.GET.get("is_active")

    if active_filter is not None:
        normalized = active_filter.strip().lower()

        if normalized not in ("true", "false"):
            return error_response(
                "invalid_is_active",
                "is_active must be true or false.",
            )

        queryset = queryset.filter(is_active=(normalized == "true"))

    queryset = queryset.order_by("-start_date", "-pk")

    total = queryset.count()
    start = (page - 1) * page_size
    terms = queryset[start:start + page_size]

    return JsonResponse({
        "terms": [term_payload(term) for term in terms],
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": (total + page_size - 1) // page_size,
        },
    })


@require_POST
@account_role_required("admin")
def term_create_view(request):
    try:
        payload = read_json(request)
        term = save_term(payload)
    except APIError as error:
        return _api_error_response(error)

    return JsonResponse(
        {
            "message": "Term created successfully.",
            "term": term_payload(term),
        },
        status=201,
    )


# --------------------------------------------------
# Term detail and update
# --------------------------------------------------

@require_GET
@account_role_required("admin")
def term_detail_view(request, term_id):
    term, error = _get_term_or_error(term_id)

    if error:
        return error

    return JsonResponse({"term": term_payload(term)})


@require_http_methods(["PUT", "PATCH"])
@account_role_required("admin")
def term_update_view(request, term_id):
    term, error = _get_term_or_error(term_id)

    if error:
        return error

    try:
        payload = read_json(request)
        updated_term = save_term(
            payload,
            instance=term,
            partial=(request.method == "PATCH"),
        )
    except APIError as error:
        return _api_error_response(error)

    return JsonResponse({
        "message": "Term updated successfully.",
        "term": term_payload(updated_term),
    })


# --------------------------------------------------
# Term activation and deactivation
# --------------------------------------------------

@require_POST
@account_role_required("admin")
def term_activate_view(request, term_id):
    try:
        term = set_term_active(term_id, True)
    except APIError as error:
        return _api_error_response(error)

    return JsonResponse({
        "message": "Term activated successfully.",
        "term": term_payload(term),
    })

@require_POST
@account_role_required("admin")
def term_deactivate_view(request, term_id):
    try:
        term = set_term_active(term_id, False)
    except APIError as error:
        return _api_error_response(error)

    return JsonResponse({
        "message": "Term deactivated successfully.",
        "term": term_payload(term),
    })
