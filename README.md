# ZapSign App — README (dev friendly)

## 0) Pré-requisitos
- Python 3.11+ (recomendado)  
- Docker + Docker Compose  
- `curl/postman ou outro client`  (para testar endpoints) 

---

## 1) Pasta e ambiente
```bash
mkdir zapsign-app && cd zapsign-app

python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install Django==4.2.14 djangorestframework==3.15.2 psycopg2-binary==2.9.9 python-dotenv==1.0.1 requests==2.32.3
```

---

## 2) Banco (Docker)
> Se você já usa Postgres local (ex.: Supabase) e a porta 5432 está ocupada, mapeie **5434** no compose.

```bash
docker compose up -d
```

Configure o Postgres no `backend/settings.py` / `.env` (exemplo):
```
DB_HOST=127.0.0.1
DB_PORT=5434
DB_NAME=zapsign
DB_USER=zapsign
DB_PASSWORD=zapsign
```

---

## 3) Projeto Django + app
```bash
django-admin startproject backend .
python manage.py startapp documents
```

Adicione o app em **`backend/settings.py`**:
```python
INSTALLED_APPS = [
  # ...
  'rest_framework',
  'documents',
]
```

---

## 4) Variáveis de ambiente (carregadas via `.env`)
Crie **`.env`** na raiz do projeto (mesmo nível do `manage.py`):

```
# Postgres
DB_HOST=127.0.0.1
DB_PORT=5434
DB_NAME=zapsign
DB_USER=zapsign
DB_PASSWORD=zapsign

# ZapSign
ZS_MODE=mock                   # mock | real | off
ZAPSIGN_BASE=https://sandbox.api.zapsign.com.br/api/v1

# IA
AI_MODE=mock                   # mock | openai
OPENAI_API_KEY=                # preencha somente se usar AI_MODE=openai
```

E em **`backend/settings.py`**:
```python
from pathlib import Path
import os
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

ZS_MODE = os.getenv("ZS_MODE", "mock").lower()
ZAPSIGN_BASE = os.getenv("ZAPSIGN_BASE", "https://sandbox.api.zapsign.com.br/api/v1")
AI_MODE = os.getenv("AI_MODE", "mock").lower()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
```

> **Importante:** sempre **reinicie** o `runserver` após mudar o `.env`.

---

## 5) Migrações e servidor
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

**Se você acabou de criar os models do `documents`:**
```bash
python manage.py makemigrations documents
python manage.py migrate
```

---

## 6) Arquitetura **CA-ready** (Clean Architecture pronta para evoluir)
Separação de responsabilidades (sem reescrever o mundo):

```
documents/
  models.py                # Company, Document, Signer (diagrama 1→N)
  serializers.py           # JSON <-> objetos
  views.py                 # ViewSets DRF (só orquestram)
  urls.py
  repo/
    orm.py                 # adapter do ORM (repositorio)
  services/
    zapsign.py             # client/facade ZapSign (mock|real|off via settings)
    ai.py                  # análise (mock|openai via settings)
  usecases/
    errors.py              # exceções de domínio
    create_document.py     # validações de criação
    send_to_zapsign.py     # envia p/ ZapSign, atualiza open_id/token/status
    get_status.py          # consulta status na ZapSign
    analyze_document.py    # análise de conteúdo (IA)
```

- **Views** chamam **use cases** → **Repos/Services** → Models.  
- **Regra de negócio** fica nos **use cases** (não na view).  
- **ZapSign/IA** alternam **mock/real** por `ZS_MODE`/`AI_MODE`.

---

## 7) Fluxo principal (2 passos)

### 7.1 Criar empresa (Company)
```bash
curl -X POST http://127.0.0.1:8000/api/companies/   -H "Content-Type: application/json"   -d '{"name":"Minha Empresa","api_token":"SEU_TOKEN_SANDBOX_OU_CHAVE_DEV"}'
```

### 7.2 Criar documento (local: **status=draft**)
```bash
curl -X POST http://127.0.0.1:8000/api/documents/   -H "Content-Type: application/json"   -d '{
    "company": 1,
    "name": "Contrato de Serviços",
    "created_by": "samuel",
    "external_id": "ext-001",
    "signers": [
      {"name":"João","email":"joao@ex.com"},
      {"name":"Maria","email":"maria@ex.com"}
    ]
  }'
```
> O serializer marca `status/open_id/token/created_at/last_updated_at` como **read-only**; o model inicia `status="draft"`.

### 7.3 Enviar para ZapSign (manual; **não gasta quota em `ZS_MODE=mock`**)
> **Atenção à barra final!** (`APPEND_SLASH=True`)
- **Usando markdown** (sandbox):
```bash
curl -X POST http://127.0.0.1:8000/api/documents/3/send_to_zapsign/   -H "Content-Type: application/json"   -d '{"markdown_text":"# Contrato

Gerado para testes."}'
```
- **Ou usando PDF público**:
```bash
curl -X POST http://127.0.0.1:8000/api/documents/3/send_to_zapsign/   -H "Content-Type: application/json"   -d '{"pdf_url":"https://exemplo.com/arquivo.pdf"}'
```

### 7.4 Status
```bash
curl http://127.0.0.1:8000/api/documents/3/status/
```

---

## 8) IA — análise de conteúdo (mock por padrão)
- **Endpoint:** `POST /api/documents/{id}/analysis/`  
- Se `AI_MODE=openai` e `OPENAI_API_KEY` presente → usa OpenAI; senão → **mock** (heurística local).

Exemplo:
```bash
curl -X POST http://127.0.0.1:8000/api/documents/3/analysis/   -H "Content-Type: application/json"   -d '{"text":"Contrato de prestação de serviços por 12 meses entre ACME e Cliente."}'
```

Resposta (mock):
```json
{ "summary": "...", "topics": ["prestação","serviços","meses"], "risk_score": 20 }
```

---

## 9) **n8n** — endpoints REST autenticados (X-API-Key)
Usa **`Company.api_token`** como chave.

Headers:
```
X-API-Key: <api_token_da_Company>
Content-Type: application/json
```

### 9.1 Criar documento (força company pelo header)
```bash
curl -X POST http://127.0.0.1:8000/api/automations/create_doc  -H "X-API-Key: SEU_TOKEN" -H "Content-Type: application/json"  -d '{"name":"Contrato via n8n","signers":[{"name":"João","email":"joao@ex.com"}]}'
```

### 9.2 Enviar para ZapSign (mock/real depende de `ZS_MODE`)
```bash
curl -X POST http://127.0.0.1:8000/api/automations/send  -H "X-API-Key: SEU_TOKEN" -H "Content-Type: application/json"  -d '{"document_id": 3, "markdown_text":"# Demo

Corpo."}'
```

### 9.3 Status
```bash
curl 'http://127.0.0.1:8000/api/automations/status?document_id=3'  -H "X-API-Key: SEU_TOKEN"
```

### 9.4 Análise (IA)
```bash
curl -X POST http://127.0.0.1:8000/api/automations/analyze  -H "X-API-Key: SEU_TOKEN" -H "Content-Type: application/json"  -d '{"document_id": 3, "text":"Contrato de suporte mensal."}'
```

---

## 10) Dicas & troubleshooting

- **Trailing slash**: `POST /send_to_zapsign/` precisa da **barra final**.  
- **400 ZapSign**: inclua **`markdown_text`** **ou** `pdf_url` no envio.  
- **403 ZapSign**: cheque `Company.api_token` e `ZAPSIGN_BASE`.  
- **Evitar gastar cota**: use `ZS_MODE=mock`. Para demo real, troque para `real` e envie **um** doc.  
- **Reenvio bloqueado**: só envia quando `status="draft"`. Para testar novamente:
  ```python
  python manage.py shell
  >>> from documents.models import Document, DocumentStatus
  >>> d = Document.objects.get(id=3)
  >>> d.status = DocumentStatus.DRAFT; d.open_id=None; d.token=""
  >>> d.save(update_fields=["status","open_id","token"])
  ```
- **Mudei `.env` e nada mudou**: reinicie o `runserver`.

---
