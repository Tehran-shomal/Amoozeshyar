"""Read-only term and course-offering queries for the backend API."""

from apps.core.models import CourseOffering, Term


def get_active_term():
    """Return the single active term, or ``None`` when scheduling is not configured."""
    return Term.objects.filter(is_active=True).first()


def list_offerings(term=None):
    """List active offerings for the active term unless a term is explicitly supplied."""
    term = term or get_active_term()
    if term is None:
        return CourseOffering.objects.none()
    return (
        CourseOffering.objects.filter(term=term, is_active=True)
        .select_related("lesson", "day_of_week", "teacher__person", "classroom")
        .order_by("day_of_week__code", "start_time", "lesson__lesson_code")
    )
