from django.urls import path

from apps.core.requests import views

app_name = "requests"
urlpatterns = [
    path("<slug:request_type>/<int:request_id>/review/", views.review_view, name="review"),
]
