from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("generate-configuration", views.generate_configuration, name="generate-configuration"),
]
