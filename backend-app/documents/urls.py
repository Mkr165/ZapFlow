# documents/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CompanyViewSet, DocumentViewSet, SignerViewSet
from .views_automation import (
    AutomationCreateSendView,
    AutomationAnalysisView,
    AutomationReportView,
)

router = DefaultRouter()
router.register(r"companies", CompanyViewSet)
router.register(r"documents", DocumentViewSet)
router.register(r"signers", SignerViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("automations/create_send/", AutomationCreateSendView.as_view(), name="automation-create-send"),
    path("automations/analysis/<int:pk>/", AutomationAnalysisView.as_view(), name="automation-analysis"),
    path("automations/reports/documents/", AutomationReportView.as_view(), name="automation-report-docs"),
]
