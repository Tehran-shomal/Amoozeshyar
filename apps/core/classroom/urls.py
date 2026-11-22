from django.urls import path

from apps.core.classroom import views


app_name = "classroom"

urlpatterns = [
    path("", views.classroom_list_view, name="classroom-list"),
    path("create/", views.classroom_create_view, name="classroom-create"),
    path(
        "<int:classroom_id>/",
        views.classroom_detail_view,
        name="classroom-detail",
    ),
    path(
        "<int:classroom_id>/update/",
        views.classroom_update_view,
        name="classroom-update",
    ),
    path(
        "<int:classroom_id>/delete/",
        views.classroom_delete_view,
        name="classroom-delete",
    ),
]