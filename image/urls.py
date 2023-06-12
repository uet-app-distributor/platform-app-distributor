from django.urls import path

from . import views

urlpatterns = [
    path("runtime", views.add_runtime, name="add-runtime"),
    path("database", views.add_database, name="add-database")
]
