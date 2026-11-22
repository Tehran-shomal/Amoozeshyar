from django.urls import path

from . import views

app_name = "attendance"

urlpatterns = [
    path(
        "my-attendance/",
        views.my_attendance_view,
        name="my-attendance",
    ),
    path(
        "offerings/<int:offering_id>/",
        views.offering_attendance_view,
        name="offering-attendance",
    ),
    path(
        "enrollments/<int:enrollment_id>/",
        views.record_attendance_view,
        name="record-attendance",
    ),
]