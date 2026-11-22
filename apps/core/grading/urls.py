from django.urls import path

from . import views

app_name = "grading"

urlpatterns = [
    path("my-grades/", views.my_grades_view, name="my-grades"),
    path(
        "offerings/<int:offering_id>/grades/",
        views.offering_grades_view,
        name="offering-grades",
    ),
    path(
        "enrollments/<int:enrollment_id>/grade/",
        views.set_grade_view,
        name="set-grade",
    ),
    path(
        "my-appeals/",
        views.my_grade_appeals_view,
        name="my-appeals",
    ),
    path(
        "enrollments/<int:enrollment_id>/appeals/",
        views.create_grade_appeal_view,
        name="create-appeal",
    ),
    path(
        "my-surveys/",
        views.my_teacher_surveys_view,
        name="my-surveys",
    ),
    path(
        "enrollments/<int:enrollment_id>/survey/",
        views.create_teacher_survey_view,
        name="create-survey",
    ),
]