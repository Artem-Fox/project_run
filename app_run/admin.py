from django.contrib import admin

from .models import Run, AthleteInfo, Challenge


@admin.register(Run)
class RunAdmin(admin.ModelAdmin):
    list_display = ["id", "created_at", "athlete", "status"]
    list_display_links = ["id", "created_at"]
    list_filter = ["status"]
    list_per_page = 10
    search_fields = ["athlete__username"]


@admin.register(AthleteInfo)
class AthleteInfoAdmin(admin.ModelAdmin):
    list_display = ["athlete", "goals", "weight"]
    list_per_page = 10
    search_fields = ["athlete__username"]


@admin.register(Challenge)
class ChallengeAdmin(admin.ModelAdmin):
    list_display = ["full_name", "athlete"]
    list_per_page = 10
    search_fields = ["full_name", "athlete__username"]
