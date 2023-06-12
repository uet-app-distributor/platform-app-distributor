from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("add-configuration", views.add_configuration, name="add-configuration"),
]
