from django.conf import settings
from django.contrib.auth.models import User
from django.db.models import Sum, Min, Max, Q, Count
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination

from django_filters.rest_framework import DjangoFilterBackend

from .models import Run, AthleteInfo, Challenge, Position, CollectibleItem
from .serializers import RunSerializer, UserSerializer, UserDetailSerializer, ChallengeSerializer, PositionSerializer, CollectibleItemSerializer
from .utils import create_challenge, check_weight, calculate_distance

import openpyxl
from geopy.distance import geodesic


@api_view(["GET"])
def company_details_view(request):
    return Response({
        "company_name": settings.SITE_TITLE,
        "slogan": settings.SITE_SLOGAN,
        "contacts": settings.SITE_CONTACTS
    })


class SizePagination(PageNumberPagination):
    page_size_query_param = "size"


class RunViewSet(viewsets.ModelViewSet):
    queryset = Run.objects.all().select_related("athlete")
    serializer_class = RunSerializer
    pagination_class = SizePagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["status", "athlete"]
    ordering_fields = ["created_at"]


class RunStartView(APIView):
    def post(self, request, run_id):
        run = get_object_or_404(Run, pk=run_id)
        if run.status == "init":
            run.status = "in_progress"
            run.save()
        else:
            return Response({
                "message": "Невозможно начать забег, он уже начат или закончен",
            }, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "message": "Забег начат"
        })


class RunStopView(APIView):
    def post(self, request, run_id):
        run = get_object_or_404(Run, pk=run_id)
        if run.status == "in_progress":
            run.status = "finished"
            run.save()

            athlete = run.athlete
            finished_runs = athlete.runs.filter(status="finished")
            if finished_runs.count() == 10:
                create_challenge("Сделай 10 Забегов!", athlete)

            positions = run.positions.all()
            if positions.count() > 1:
                all_positions = []
                for position in positions:
                    coords = (position.latitude, position.longitude)
                    all_positions.append(coords)

                distance = calculate_distance(all_positions)
                run.distance = distance

                min_time = positions.aggregate(min_time=Min("date_time")).get("min_time")
                max_time = positions.aggregate(max_time=Max("date_time")).get("max_time")
                run_time = (max_time - min_time).total_seconds()
                run.run_time_seconds = run_time if run_time else 0
                run.save()

            total_distance = finished_runs.aggregate(total_distance=Sum("distance")).get("total_distance", 0)
            if total_distance and total_distance >= 50:
                create_challenge("Пробеги 50 километров!", athlete)
        else:
            return Response({
                "message": "Невозможно закончить забег, он не начат"
            }, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "message": "Забег закончен"
        })


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.exclude(is_superuser=True).order_by("id").annotate(runs_finished=Count("runs", filter=Q(runs__status="finished")))
    serializer_class = UserSerializer
    pagination_class = SizePagination
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["first_name", "last_name"]
    ordering_fields = ["date_joined"]

    def get_queryset(self):
        qs = self.queryset
        q_type = self.request.query_params.get("type", None)
        if q_type:
            if q_type == "coach":
                return qs.filter(is_staff=True)
            elif q_type == "athlete":
                return qs.filter(is_staff=False)

        return qs

    def get_serializer_class(self):
        if self.action == "list":
            return UserSerializer
        elif self.action == "retrieve":
            return UserDetailSerializer

        return super().get_serializer_class()


class AthleteInfoView(APIView):
    def get(self, request, user_id):
        user = get_object_or_404(User, pk=user_id)
        athlete_info, _ = AthleteInfo.objects.get_or_create(athlete=user)

        return Response({
            "goals": athlete_info.goals,
            "weight": athlete_info.weight,
            "user_id": user_id
        })

    def put(self, request, user_id):
        weight = request.data.get("weight", None)
        goals = request.data.get("goals", "")

        if weight:
            res = check_weight(weight)
            if not res:
                return Response({
                    "message": "Неверный вес"
                }, status=status.HTTP_400_BAD_REQUEST)

        user = get_object_or_404(User, pk=user_id)
        athlete_info, _ = AthleteInfo.objects.update_or_create(
            athlete=user,
            defaults={
                "weight": weight,
                "goals": goals,
            }
        )

        return Response({
            "goals": athlete_info.goals,
            "weight": athlete_info.weight,
            "user_id": user_id
        }, status=status.HTTP_201_CREATED)


class ChallengeListView(ListAPIView):
    serializer_class = ChallengeSerializer

    def get_queryset(self):
        athlete_id = self.request.query_params.get("athlete", None)
        if athlete_id:
            return Challenge.objects.filter(athlete__id=athlete_id).select_related("athlete")

        return Challenge.objects.all().select_related("athlete")


class PositionViewSet(viewsets.ModelViewSet):
    serializer_class = PositionSerializer

    def get_queryset(self):
        run_id = self.request.query_params.get("run", None)
        if run_id:
            return Position.objects.filter(run__id=run_id).select_related("run")

        return Position.objects.all().select_related("run")

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            position_latitude = serializer.validated_data["latitude"]
            position_longitude = serializer.validated_data["longitude"]
            position_coords = (position_latitude, position_longitude)
            position_date_time = serializer.validated_data["date_time"]

            last_position = Position.objects.filter(run=serializer.validated_data["run"]).last()
            if last_position:
                last_position_coords = (last_position.latitude, last_position.longitude)
                last_position_date_time = last_position.date_time

                dist_diff = geodesic(position_coords, last_position_coords).meters
                time_diff = (position_date_time - last_position_date_time).total_seconds()
                speed = round(dist_diff / time_diff, 2) if time_diff else 0

                position = serializer.save(speed=speed)
            else:
                position = serializer.save()

            run_positions = Position.objects.filter(run=serializer.validated_data["run"])

            if run_positions.count() > 1:
                all_positions = []
                for position in run_positions:
                    coords = (position.latitude, position.longitude)
                    all_positions.append(coords)

                total_distance = round(calculate_distance(all_positions), 2)
                position = serializer.save(distance=total_distance)

            user = position.run.athlete

            collectible_items = CollectibleItem.objects.all().prefetch_related("users")
            if collectible_items:
                for collectible in collectible_items:
                    latitude = collectible.latitude
                    longitude = collectible.longitude
                    collectible_coords = (collectible.latitude, collectible.longitude)

                    if latitude > 90 or latitude < -90 or longitude > 180 or longitude < -180:
                        continue

                    distance = geodesic(position_coords, collectible_coords).meters
                    if distance <= 100:
                        if user not in collectible.users.all():
                            collectible.users.add(user)
                            return Response({
                                "message": f"Вы нашли предмет {collectible.name}",
                                "item_id": collectible.id
                            }, status=status.HTTP_201_CREATED)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CollectibleItemView(ListAPIView):
    queryset = CollectibleItem.objects.all()
    serializer_class = CollectibleItemSerializer


class UploadCollectibleItemView(APIView):
    def post(self, request):
        file = request.data.get("file", None)
        if file:
            workbook = openpyxl.load_workbook(file)
            worksheet = workbook.active
            invalid_rows = []

            for row in worksheet.iter_rows(min_row=2, values_only=True):
                data = {
                    "name": row[0],
                    "uid": row[1],
                    "value": row[2],
                    "latitude": row[3],
                    "longitude": row[4],
                    "picture": row[5]
                }

                serializer = CollectibleItemSerializer(data=data)
                if serializer.is_valid():
                    serializer.save()
                else:
                    invalid_rows.append(list(data.values()))

            return Response(invalid_rows)

        return Response({
            "message": "Пожалуйста, загрузите Excel-файл"
        }, status=status.HTTP_400_BAD_REQUEST)
