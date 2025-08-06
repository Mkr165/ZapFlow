from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CompanyViewSet, DocumentViewSet, SignerViewSet

router = DefaultRouter()
router.register(r"companies", CompanyViewSet)
router.register(r"documents", DocumentViewSet)
router.register(r"signers", SignerViewSet)

urlpatterns = [path("", include(router.urls))]
