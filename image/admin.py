from django.contrib import admin

from .models import Runtime
from .models import Database


admin.site.register(Runtime)
admin.site.register(Database)