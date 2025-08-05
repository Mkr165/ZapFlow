# documents/services/zapsign.py
from django.conf import settings
import requests
import uuid, random

BASE = settings.ZAPSIGN_BASE
MODE = settings.ZS_MODE
TIMEOUT = 20

class ExternalServiceError(Exception):
    pass

def _raise(r):
    try:
        body = r.json()
    except Exception:
        body = r.text
    raise ExternalServiceError(f"ZapSign {r.status_code}: {body}")

# -------- REAL --------
def _real_create_document(api_token: str, payload: dict) -> dict:
    r = requests.post(f"{BASE}/docs/", json=payload,
                      headers={"Authorization": f"Bearer {api_token}"}, timeout=TIMEOUT)
    if r.status_code >= 400:
        _raise(r)
    return r.json()

def _real_get_status(api_token: str, open_id: int) -> dict:
    r = requests.get(f"{BASE}/docs/{open_id}/",
                     headers={"Authorization": f"Bearer {api_token}"}, timeout=TIMEOUT)
    if r.status_code >= 400:
        _raise(r)
    return r.json()

# -------- MOCK --------
def _mock_create_document(_: str, payload: dict) -> dict:
    oid = random.randint(10_000, 99_999)
    return {
        "open_id": oid,
        "token": str(uuid.uuid4()),
        "status": "sent",
        "signers": [
            {"email": s["email"], "token": str(uuid.uuid4()), "status": "pending"}
            for s in payload.get("signers", [])
        ],
    }

def _mock_get_status(_: str, open_id: int) -> dict:
    return {"open_id": open_id, "status": "sent"}

# -------- Facades (usadas pelos use cases) --------
def create_document(api_token: str, payload: dict) -> dict:
    if MODE == "real":
        return _real_create_document(api_token, payload)
    if MODE == "off":
        return {"open_id": None, "token": "", "status": "draft"}
    return _mock_create_document(api_token, payload)

def get_status(api_token: str, open_id: int) -> dict:
    if MODE == "real":
        return _real_get_status(api_token, open_id)
    if MODE == "off":
        return {"open_id": open_id, "status": "draft"}
    return _mock_get_status(api_token, open_id)
