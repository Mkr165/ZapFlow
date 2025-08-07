import pytest
from rest_framework.test import APIClient
from documents.models import Company

pytestmark = pytest.mark.django_db

def test_health():
    c = APIClient()
    r = c.get("/health/")
    assert r.status_code == 200

def test_create_document_starts_draft():
    c = Company.objects.create(name="ACME", api_token="TOK")
    r = APIClient().post("/api/documents/", {
        "company": c.id, "name": "Contrato",
        "signers": [{"name":"João","email":"joao@ex.com"}]
    }, format="json")
    assert r.status_code == 201
    assert r.json()["status"] == "draft"
