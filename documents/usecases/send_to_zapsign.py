# documents/usecases/send_to_zapsign.py
from .errors import ValidationError
from documents.services.zapsign import create_document as zs_create

class SendToZapSign:
    def __init__(self, repo):
        self.repo = repo

    def execute(self, document_id: int, *, pdf_url: str | None = None, markdown_text: str | None = None):
        doc = self.repo.get_document_with_signers(document_id) 
        if doc.status != "draft":
            raise ValidationError("Apenas documentos em 'draft' podem ser enviados.")

        if not doc.company.api_token:
            raise ValidationError("Empresa sem api_token configurado.")

        # 🔹 CONTEÚDO OBRIGATÓRIO: use markdown_text no sandbox
        markdown = (
            f"# {doc.name}\n\n"
            f"Criado por: {doc.created_by or 'sistema'}\n\n"
            f"Documento gerado para fins de teste via API."
        )

        payload = {
            "name": doc.name,
            "markdown_text": markdown,       # <<-- chave exigida pela API (ou url_pdf, base64_pdf, etc.)
            "signers": [{"name": s.name, "email": s.email} for s in doc.signers.all()],
        }


        doc = self.repo.get_document_with_signers(document_id)
        if doc.status != "draft":
            raise ValidationError("Apenas documentos em 'draft' podem ser enviados.")

        if not doc.company.api_token:
            raise ValidationError("Empresa sem api_token configurado.")

        # constrói conteúdo: prioriza PDF, senão markdown básico
        if pdf_url:
            payload = {
                "name": doc.name,
                "url_pdf": pdf_url,
                "signers": [{"name": s.name, "email": s.email} for s in doc.signers.all()],
            }
        else:
            markdown = markdown_text or f"# {doc.name}\n\nCriado por: {doc.created_by or 'sistema'}."
            payload = {
                "name": doc.name,
                "markdown_text": markdown,
                "signers": [{"name": s.name, "email": s.email} for s in doc.signers.all()],
            }

        data = zs_create(doc.company.api_token, payload)

        # Resposta típica: open_id, token, status, signers[...]  (vide docs)
        # https://docs.zapsign.com.br/english/documentos/criar-documento
        open_id = data.get("open_id") or data.get("id")
        token   = data.get("token") or ""
        status  = data.get("status") or "sent"

        return self.repo.save_document_fields(doc, open_id=open_id, token=token, status=status)
