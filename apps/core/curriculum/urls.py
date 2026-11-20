from django.urls import path

from apps.core.curriculum import views

app_name = "curriculum"

urlpatterns = [
    # GET: list curriculum records
    # POST: create a curriculum record (admin only)
    path(
        "",
        views.curriculum_list_view,
        name="curriculum-list",
    ),
    path(
        "create/",
        views.curriculum_create_view,
        name="curriculum-create",
    ),
    path(
        "<int:curriculum_id>/",
        views.curriculum_detail_view,
        name="curriculum-detail",
    ),
    path(
        "<int:curriculum_id>/update/",
        views.curriculum_update_view,
        name="curriculum-update",
    ),
    path(
        "<int:curriculum_id>/activate/",
        views.curriculum_activate_view,
        name="curriculum-activate",
    ),
    path(
        "<int:curriculum_id>/deactivate/",
        views.curriculum_deactivate_view,
        name="curriculum-deactivate",
    ),
]
