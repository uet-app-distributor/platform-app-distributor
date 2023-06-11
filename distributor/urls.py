from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("generate-app-configuration", views.generate_app_configuration, name="generate-app-configuration"),
]
