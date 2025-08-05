from django.contrib import admin

from .models import Run, AthleteInfo


@admin.register(Run)
class RunAdmin(admin.ModelAdmin):
    list_display = ["id", "created_at", "athlete", "status"]
    list_display_links = ["id", "created_at"]
    list_filter = ["status"]
    list_per_page = 10
    search_fields = ["athlete__username"]


@admin.register(AthleteInfo)
class AthleteInfoAdmin(admin.ModelAdmin):
    list_display = ["user", "goals", "weight"]
    list_per_page = 10
    search_fields = ["user__username"]
