from django.db import IntegrityError
from django.conf import settings
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination

from django_filters.rest_framework import DjangoFilterBackend

from .models import Run, AthleteInfo, Challenge, Position
from .serializers import RunSerializer, UserSerializer, ChallengeSerializer, PositionSerializer
from .utils import check_weight, calculate_distance


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
            finished_runs = athlete.runs.filter(status="finished").count()
            if finished_runs == 10:
                challenge_name = "Сделай 10 Забегов!"
                challenge_athlete = athlete

                try:
                    Challenge.objects.create(
                        full_name=challenge_name,
                        athlete=challenge_athlete
                    )
                except IntegrityError:
                    pass

            positions = run.positions.all()
            if positions.count() > 1:
                all_positions = []
                for position in positions:
                    coords = (position.latitude, position.longitude)
                    all_positions.append(coords)

                distance = calculate_distance(all_positions)
                run.distance = distance
                run.save()

        else:
            return Response({
                "message": "Невозможно закончить забег, он не начат"
            }, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "message": "Забег закончен"
        })


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.exclude(is_superuser=True).order_by("id")
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
