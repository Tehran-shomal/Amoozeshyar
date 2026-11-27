from django.urls import path

from .api import portal_page_api, portal_ui_page_api

app_name = "portal_api"

urlpatterns = [
    path("ui/pages/<slug:slug>/", portal_ui_page_api, name="ui-page"),
    path("pages/<slug:slug>/", portal_page_api, name="page"),
]
