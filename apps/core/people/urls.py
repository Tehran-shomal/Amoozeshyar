from django.urls import path

from apps.core.people import views

app_name = "people"

urlpatterns = [
    # Student APIs
    path(
        "students/me/",
        views.my_student_profiles_view,
        name="my-student-profiles",
    ),
    path(
        "students/",
        views.students_list_view,
        name="students-list",
    ),
    path(
        "students/<int:student_id>/",
        views.student_detail_view,
        name="student-detail",
    ),

    # Teacher APIs
    path(
        "teachers/me/",
        views.my_teacher_profile_view,
        name="my-teacher-profile",
    ),
    path(
        "teachers/",
        views.teachers_list_view,
        name="teachers-list",
    ),
    path(
        "teachers/<int:teacher_id>/",
        views.teacher_detail_view,
        name="teacher-detail",
    ),
]