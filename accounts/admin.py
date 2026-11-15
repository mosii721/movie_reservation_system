from django.contrib import admin
from . import models

# Register your models here.
@admin.register(models.Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user__first_name','user__last_name','user__email','phone_number','created_at']
    list_select_related = ['user']
    ordering = ['created_at']
    search_fields = ['user__username','phone_number','user__last_name','user__email']
    list_per_page = 10


