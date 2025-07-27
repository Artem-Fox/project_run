from django.contrib import admin

from .models import Run


@admin.register(Run)
class RunAdmin(admin.ModelAdmin):
    list_display = ["id", "created_at", "athlete", "status"]
    list_display_links = ["id", "created_at"]
    list_filter = ["status"]
    list_per_page = 10
    search_fields = ["athlete__username"]
