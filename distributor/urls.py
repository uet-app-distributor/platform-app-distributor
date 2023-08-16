from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("distribute", views.distribute, name="distribute"),
]
