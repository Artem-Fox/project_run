"""
URL configuration for project_run project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from rest_framework.routers import DefaultRouter

from debug_toolbar.toolbar import debug_toolbar_urls

from app_run.views import company_details_view, RunViewSet, UserViewSet, RunStartView, RunStopView

router = DefaultRouter()
router.register("runs", RunViewSet)
router.register("users", UserViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/company_details/', company_details_view),
    path("api/", include(router.urls)),
    path("api/runs/<int:run_id>/start/", RunStartView.as_view()),
    path("api/runs/<int:run_id>/stop/", RunStopView.as_view()),
]

if settings.DEBUG:
    urlpatterns += debug_toolbar_urls()

admin.site.site_header = "Панель администрирования"
admin.site.index_title = "Django RUN"
