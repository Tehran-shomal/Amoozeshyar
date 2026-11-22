from django.urls import path

from apps.core.academic_structure import views


app_name = "academic_structure"


urlpatterns = [
    # Faculty
    path(
        "faculties/",
        views.faculty_list_view,
        name="faculty-list",
    ),
    path(
        "faculties/create/",
        views.faculty_create_view,
        name="faculty-create",
    ),
    path(
        "faculties/<int:faculty_id>/",
        views.faculty_detail_view,
        name="faculty-detail",
    ),
    path(
        "faculties/<int:faculty_id>/update/",
        views.faculty_update_view,
        name="faculty-update",
    ),
    path(
        "faculties/<int:faculty_id>/activate/",
        views.faculty_activate_view,
        name="faculty-activate",
    ),
    path(
        "faculties/<int:faculty_id>/deactivate/",
        views.faculty_deactivate_view,
        name="faculty-deactivate",
    ),

    # Department
    path(
        "departments/",
        views.department_list_view,
        name="department-list",
    ),
    path(
        "departments/create/",
        views.department_create_view,
        name="department-create",
    ),
    path(
        "departments/<int:department_id>/",
        views.department_detail_view,
        name="department-detail",
    ),
    path(
        "departments/<int:department_id>/update/",
        views.department_update_view,
        name="department-update",
    ),
    path(
        "departments/<int:department_id>/activate/",
        views.department_activate_view,
        name="department-activate",
    ),
    path(
        "departments/<int:department_id>/deactivate/",
        views.department_deactivate_view,
        name="department-deactivate",
    ),

    # Field
    path(
        "fields/",
        views.field_list_view,
        name="field-list",
    ),
    path(
        "fields/create/",
        views.field_create_view,
        name="field-create",
    ),
    path(
        "fields/<int:field_id>/",
        views.field_detail_view,
        name="field-detail",
    ),
    path(
        "fields/<int:field_id>/update/",
        views.field_update_view,
        name="field-update",
    ),
    path(
        "fields/<int:field_id>/activate/",
        views.field_activate_view,
        name="field-activate",
    ),
    path(
        "fields/<int:field_id>/deactivate/",
        views.field_deactivate_view,
        name="field-deactivate",
    ),
    # Lesson
    path(
        "lessons/",
        views.lesson_list_view,
        name="lesson-list",
    ),
    path(
        "lessons/create/",
        views.lesson_create_view,
        name="lesson-create",
    ),
    path(
        "lessons/<int:lesson_id>/",
        views.lesson_detail_view,
        name="lesson-detail",
    ),
    path(
        "lessons/<int:lesson_id>/update/",
        views.lesson_update_view,
        name="lesson-update",
    ),
    path(
        "lessons/<int:lesson_id>/activate/",
        views.lesson_activate_view,
        name="lesson-activate",
    ),
    path(
        "lessons/<int:lesson_id>/deactivate/",
        views.lesson_deactivate_view,
        name="lesson-deactivate",
    ),

    # Prerequisite / Corequisite
    path(
        "prerequisites/",
        views.prerequisite_list_view,
        name="prerequisite-list",
    ),
    path(
        "prerequisites/create/",
        views.prerequisite_create_view,
        name="prerequisite-create",
    ),
    path(
        "prerequisites/<int:prerequisite_id>/",
        views.prerequisite_detail_view,
        name="prerequisite-detail",
    ),
    path(
        "prerequisites/<int:prerequisite_id>/update/",
        views.prerequisite_update_view,
        name="prerequisite-update",
    ),
    path(
        "prerequisites/<int:prerequisite_id>/delete/",
        views.prerequisite_delete_view,
        name="prerequisite-delete",
    ),
]