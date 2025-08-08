# backend-app/tests/conftest.py
import pytest
from rest_framework.test import APIClient
from documents.models import Company

@pytest.fixture
def api():
    return APIClient()

@pytest.fixture
def company(db):
    return Company.objects.create(name="Acme", api_token="secret-token-123")

@pytest.fixture
def auth_headers(company):
    # "X-API-Key" -> "HTTP_X_API_KEY" no APIClient
    return {"HTTP_X_API_KEY": company.api_token}

# ⚠️ Mock global, roda em TODOS os testes
@pytest.fixture(autouse=True)
def mock_zapsign(monkeypatch):
    """
    Evita chamadas externas à ZapSign nos testes.
    O usecase faz: from documents.services.zapsign import create_document as zs_create
    Então precisamos monkeypatch em documents.usecases.send_to_zapsign.zs_create
    """
    def fake_create_document(api_token, payload):
        # simula retorno mínimo esperado pelo fluxo
        return {
            "open_id": 999,
            "token": "doc-token",
            "status": "sent",
            "signers": [
                {"email": s["email"], "token": "sign-token"} for s in payload.get("signers", [])
            ],
        }

    monkeypatch.setattr(
        "documents.usecases.send_to_zapsign.zs_create",
        fake_create_document
    ) 

from documents.models import Company, Document   

@pytest.fixture
def company_b(db):
    return Company.objects.create(name="Acme B", api_token="secret-token-456")

@pytest.fixture
def make_document(db):
    def _mk(company, name="Doc", status="draft"):
        # ⚠️ Ajuste os campos conforme seu modelo Document
        doc = Document.objects.create(
            company=company,
            name=name,
            status=status,
            created_by="tests",
        ) 
        return doc
    return _mk
