from django.contrib import admin

from .models import Run, AthleteInfo, Challenge, Position, CollectibleItem


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


admin.site.register(Position)


@admin.register(CollectibleItem)
class CollectibleItemAdmin(admin.ModelAdmin):
    list_display = ["uid", "name"]
    list_display_links = ["uid", "name"]
    list_per_page = 10
    search_fields = ["uid", "name"]
