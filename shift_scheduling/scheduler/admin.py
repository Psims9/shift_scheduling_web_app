from django.contrib import admin

# Register your models here.

from .models import Worker, Schedule

admin.site.register(Worker)
admin.site.register(Schedule)