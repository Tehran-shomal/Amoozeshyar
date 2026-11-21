
from django.urls import path

from .views import HomeView, LoginPreviewView, PortalSectionView, PortalLogoutView

app_name = 'core'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path("login/", LoginPreviewView.as_view(), name="login-preview"),
    path("logout/", PortalLogoutView.as_view(), name="web-logout"),
    path("portal/<slug:slug>/", PortalSectionView.as_view(), name="section"),
]

