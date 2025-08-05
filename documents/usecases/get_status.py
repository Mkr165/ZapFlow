# documents/usecases/get_status.py
from .errors import ValidationError
from documents.services.zapsign import get_status as zs_status

class GetZapSignStatus:
    def __init__(self, repo): self.repo = repo
    def execute(self, document_id: int):
        doc = self.repo.get_document_with_signers(document_id)
        if not doc.open_id:
            raise ValidationError("Documento ainda não possui open_id.")
        data = zs_status(doc.company.api_token, int(doc.open_id))
        new_status = data.get("status")
        if new_status and new_status != doc.status:
            self.repo.save_document_fields(doc, status=new_status)
        return {"status": new_status or doc.status, "raw": data}
