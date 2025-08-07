from django.contrib import admin
from main_app import models

# Register your models here.

# admin.site.register(models.RoleUser)


class SchedulerAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'family']
    exclude = ['owner']


admin.site.register(models.Scheduler, SchedulerAdmin)


class BookerAdmin(admin.ModelAdmin):
    exclude = ['owner']


admin.site.register(models.Booker, BookerAdmin)


class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['booker', 'scheduler', 'id']


admin.site.register(models.Appointment, AppointmentAdmin)
