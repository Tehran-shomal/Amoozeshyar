from django.urls import path

from apps.core.scheduling import views

app_name = "scheduling"
urlpatterns = [
    path("active-term/", views.active_term_view, name="active-term"),
    path("offerings/", views.offerings_view, name="offerings"),
]
