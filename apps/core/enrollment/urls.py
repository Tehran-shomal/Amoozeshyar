from django.urls import path

from apps.core.enrollment import views

app_name = "enrollment"
urlpatterns = [
    path("register/<int:offering_id>/", views.register_view, name="register"),
    path("drop/<int:enrollment_id>/", views.drop_view, name="drop"),
]
