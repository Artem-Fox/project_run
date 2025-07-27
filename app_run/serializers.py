from rest_framework import serializers
from django.contrib.auth.models import User

from .models import Run


class UserSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()
    runs_finished = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "date_joined", "username", "last_name", "first_name", "type", "runs_finished"]

    def get_type(self, obj):
        if obj.is_staff:
            return "coach"

        return "athlete"

    def get_runs_finished(self, obj):
        return obj.runs.filter(status="finished").count()


class AthleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "last_name", "first_name"]


class RunSerializer(serializers.ModelSerializer):
    athlete_data = AthleteSerializer(source="athlete", read_only=True)

    class Meta:
        model = Run
        fields = "__all__"
