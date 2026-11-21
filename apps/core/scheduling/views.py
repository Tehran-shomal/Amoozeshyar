"""JSON read endpoints for term and offering data."""

from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_GET

from apps.core.api import error_response
from apps.core.models import Term
from apps.core.scheduling.services import get_active_term, list_offerings


def _term_payload(term, now):
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
        "emergency_drop_open": term.emergency_drop_start <= now <= term.emergency_drop_end,
    }


def _authentication_error(request):
    """Keep portal read endpoints private to authenticated sessions."""
    if request.user.is_authenticated:
        return None
    return error_response(
        "authentication_required", "Authentication is required.", 401
    )


@require_GET
def active_term_view(request):
    authentication_error = _authentication_error(request)
    if authentication_error:
        return authentication_error

    term = get_active_term()
    return JsonResponse({"term": _term_payload(term, timezone.now())})


@require_GET
def offerings_view(request):
    authentication_error = _authentication_error(request)
    if authentication_error:
        return authentication_error

    term_code = request.GET.get("term")
    if term_code:
        term = Term.objects.filter(term_code=term_code).first()
        if term is None:
            return error_response("term_not_found", "The requested term does not exist.", 404)
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
            "total_units": offering.lesson.theory_units + offering.lesson.practical_units,
            "teacher": offering.teacher.person.full_name,
            "day_of_week": offering.day_of_week.code if offering.day_of_week else None,
            "start_time": offering.start_time.isoformat(),
            "end_time": offering.end_time.isoformat(),
            "classroom": {
                "building": offering.classroom.building_name,
                "room": offering.classroom.room_number,
            },
            "capacity": offering.capacity,
            "remaining_capacity": offering.remaining_capacity,
            "exam_date": offering.exam_date.isoformat() if offering.exam_date else None,
            "exam_time": offering.exam_time.isoformat() if offering.exam_time else None,
        }
        for offering in offerings
    ]
    return JsonResponse({"offerings": payload})
