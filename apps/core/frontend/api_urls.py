from django.urls import path

from .api import portal_page_api

app_name = "portal_api"

urlpatterns = [
    path("pages/<slug:slug>/", portal_page_api, name="page"),
]
