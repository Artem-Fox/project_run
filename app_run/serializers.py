from rest_framework import serializers
from django.contrib.auth.models import User

from .models import Run, Challenge, Position, CollectibleItem


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


class ChallengeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Challenge
        fields = ["full_name", "athlete"]


class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Position
        fields = "__all__"

    def validate_run(self, value):
        if value.status != "in_progress":
            raise serializers.ValidationError("Забег должен быть в процессе")
        else:
            return value

    def validate_latitude(self, value):
        if value < -90 or value > 90:
            raise serializers.ValidationError("Широта должна быть в пределах от -90 до 90")
        else:
            return value

    def validate_longitude(self, value):
        if value < -180 or value > 180:
            raise serializers.ValidationError("Долгота должна быть в пределах от -180 до 180")
        else:
            return value


class CollectibleItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CollectibleItem
        fields = ["id", "name", "uid", "latitude", "longitude", "picture", "value"]

    def validate_latitude(self, value):
        if value < -90 or value > 90:
            raise serializers.ValidationError("Широта должна быть в пределах от -90 до 90")
        else:
            return value

    def validate_longitude(self, value):
        if value < -180 or value > 180:
            raise serializers.ValidationError("Долгота должна быть в пределах от -180 до 180")
        else:
            return value


class UserDetailSerializer(UserSerializer):
    items = CollectibleItemSerializer(many=True, read_only=True)

    class Meta(UserSerializer.Meta):
        model = User
        fields = UserSerializer.Meta.fields + ["items"]
