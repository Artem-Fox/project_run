from rest_framework import serializers
from django.contrib.auth.models import User
from django.db.models import Avg

from .models import Run, Challenge, Position, CollectibleItem, Subscribe, Rating


class UserSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()
    runs_finished = serializers.IntegerField()
    rating = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "date_joined", "username", "last_name", "first_name", "type", "runs_finished", "rating"]

    def get_type(self, obj):
        if obj.is_staff:
            return "coach"

        return "athlete"

    def get_rating(self, obj):
        avg_rating = Rating.objects.filter(rated=obj).aggregate(avg_rating=Avg("rating"))["avg_rating"]
        return avg_rating


class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ["rater", "rated", "rating"]

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Рейтинг должен быть в пределах от 1 до 5")
        else:
            return value


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
    date_time = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S.%f")

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
    coach = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        model = User
        fields = UserSerializer.Meta.fields + ["items", "coach"]

    def get_coach(self, obj):
        try:
            subscribe = Subscribe.objects.get(subscriber=obj)
            return subscribe.subscribed_to_id
        except Subscribe.DoesNotExist:
            return None


class CoachDetailSerializer(UserSerializer):
    athletes = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        model = User
        fields = UserSerializer.Meta.fields + ["athletes"]

    def get_athletes(self, obj):
        return Subscribe.objects.filter(subscribed_to=obj).values_list("subscriber_id", flat=True)
