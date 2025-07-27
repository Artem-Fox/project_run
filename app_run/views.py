from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination
from django.conf import settings
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

from django_filters.rest_framework import DjangoFilterBackend

from .models import Run
from .serializers import RunSerializer, UserSerializer


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
        else:
            return Response({
                "message": "Невозможно закончить забег, он не начат",
            }, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "message": "Забег закончен",
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
