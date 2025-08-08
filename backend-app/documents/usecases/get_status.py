# documents/usecases/get_status.py
import logging
from .errors import ValidationError
from documents.services.zapsign import get_status as zs_status
from documents.models import DocumentStatus, SignerStatus  # aproveitando enums já existentes

logger = logging.getLogger(__name__)

STATUS_MAP = {
    "draft": DocumentStatus.DRAFT,
    "sent": DocumentStatus.SENT,
    "opened": DocumentStatus.SENT,     # ZapSign às vezes retorna "opened"
    "signed": DocumentStatus.SIGNED,
    "canceled": DocumentStatus.CANCELED,
    "rejected": DocumentStatus.CANCELED,  # normalizamos como cancelado
}

SIGNER_STATUS_MAP = {
    "pending": SignerStatus.PENDING,
    "signed": SignerStatus.SIGNED,
    "rejected": SignerStatus.REJECTED,
}

class GetZapSignStatus:
    def __init__(self, repo):
        self.repo = repo

    def execute(self, document_id: int):
        doc = self.repo.get_document_with_signers(document_id)

        if not doc.company.api_token:
            raise ValidationError("Empresa sem api_token configurado.")
        if not (doc.token or doc.open_id):
            raise ValidationError("Documento não possui identificadores remotos (open_id/token).")

        try:
            remote_id = doc.token or str(doc.open_id)
            data = zs_status(doc.company.api_token, remote_id)
        except Exception as e:
            logger.exception("Falha ao consultar status na ZapSign (doc_id=%s)", document_id)
            raise ValidationError(f"Falha ao consultar status na ZapSign: {e}")

        logger.info("Status retornado ZapSign (doc_id=%s): %s", document_id, data)

        # Normaliza status
        raw_status = (data or {}).get("status") or doc.status
        new_status = STATUS_MAP.get(raw_status.lower(), raw_status)

        # Atualiza documento se status mudou
        if new_status and new_status != doc.status:
            self.repo.save_document_fields(doc, status=new_status)

        # Atualiza signatários
        for s in (data or {}).get("signers", []):
            email = (s.get("email") or "").strip()
            if not email:
                continue
            signer_status = SIGNER_STATUS_MAP.get((s.get("status") or "").lower())
            signer_token = s.get("token")
            self.repo.update_signer_status_token_by_email(
                document_id=doc.id,
                email=email,
                status=signer_status,
                token=signer_token
            )

        return {
            "document_id": doc.id,
            "status": new_status,
            "raw": data,
        }
