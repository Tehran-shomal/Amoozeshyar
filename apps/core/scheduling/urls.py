from django.urls import path
from apps.core.scheduling import views

app_name = "scheduling"

urlpatterns = [
    # Existing read endpoints
    path("active-term/", views.active_term_view, name="active-term"),
    path("offerings/", views.offerings_view, name="offerings"),

    # Course offering management
    path(
        "offerings/manage/",
        views.offerings_manage_list_view,
        name="offerings-manage-list",
    ),
    path(
        "offerings/create/",
        views.offering_create_view,
        name="offering-create",
    ),
    path(
        "offerings/<int:offering_id>/",
        views.offering_detail_view,
        name="offering-detail",
    ),
    path(
        "offerings/<int:offering_id>/update/",
        views.offering_update_view,
        name="offering-update",
    ),
    path(
        "offerings/<int:offering_id>/activate/",
        views.offering_activate_view,
        name="offering-activate",
    ),
    path(
        "offerings/<int:offering_id>/deactivate/",
        views.offering_deactivate_view,
        name="offering-deactivate",
    ),

    # Term management
    path("terms/", views.terms_list_view, name="terms-list"),
    path("terms/create/", views.term_create_view, name="term-create"),
    path("terms/<int:term_id>/", views.term_detail_view, name="term-detail"),
    path(
        "terms/<int:term_id>/update/",
        views.term_update_view,
        name="term-update",
    ),
    path(
        "terms/<int:term_id>/activate/",
        views.term_activate_view,
        name="term-activate",
    ),
    path(
        "terms/<int:term_id>/deactivate/",
        views.term_deactivate_view,
        name="term-deactivate",
    ),
]