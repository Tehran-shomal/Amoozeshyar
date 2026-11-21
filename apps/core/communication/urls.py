from django.urls import path

from apps.core.communication import views

app_name = "communication"

urlpatterns = [
    path("send/", views.send_view, name="send"),
    path("inbox/", views.inbox_view, name="inbox"),
    path("outbox/", views.outbox_view, name="outbox"),
    path("<int:communication_id>/", views.detail_view, name="detail"),
    path(
        "<int:communication_id>/read/",
        views.mark_read_view,
        name="mark_read",
    ),
    path(
        "<int:communication_id>/unread/",
        views.mark_unread_view,
        name="mark_unread",
    ),
]
