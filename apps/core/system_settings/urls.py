from django.urls import path

from apps.core.system_settings import views

app_name = "system_settings"

urlpatterns = [
    path("", views.system_setting_list_view, name="setting-list"),
    path("create/", views.system_setting_create_view, name="setting-create"),
    path(
        "<int:setting_id>/",
        views.system_setting_detail_view,
        name="setting-detail",
    ),
    path(
        "<int:setting_id>/update/",
        views.system_setting_update_view,
        name="setting-update",
    ),
]
