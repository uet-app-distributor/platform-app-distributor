from django.contrib import admin

from .models import App
from .models import Database


admin.site.register(App)
admin.site.register(Database)
