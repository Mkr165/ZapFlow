# documents/usecases/send_to_zapsign.py
from .errors import ValidationError
from documents.services.zapsign import create_document as zs_create

class SendToZapSign:
    def __init__(self, repo): self.repo = repo

    def execute(self, document_id: int):
        doc = self.repo.get_document_with_signers(document_id)
        if doc.status != "draft":
            raise ValidationError("Apenas documentos em 'draft' podem ser enviados.")
        if not doc.company.api_token:
            raise ValidationError("Empresa sem api_token configurado.")

        signers = [{'sandbox': True, "name": s.name, "email": s.email, "send_automatic_email": True} for s in doc.signers.all()]
        if not signers:
            raise ValidationError("Documento sem signatários.")

        content = getattr(doc, "content", None)
        if not content:
            raise ValidationError("Defina o conteúdo do documento via /content antes de enviar.")
        if content.content_type == "url_pdf" and not content.pdf_url:
            raise ValidationError("pdf_url não definido.")
        if content.content_type == "markdown" and not content.markdown_text:
            raise ValidationError("markdown_text não definido.")

        chosen = ({"url_pdf": content.pdf_url} if content.content_type == "url_pdf"
                  else {"markdown_text": content.markdown_text})

        payload = {"name": doc.name, "signers": signers, **chosen}
        data = zs_create(doc.company.api_token, payload)
        print('data return   ', data)
        open_id = data.get("open_id") or data.get("id")
        token   = data.get("token") or ""
        status  = data.get("status") or "sent"

        self.repo.save_document_fields(doc, open_id=open_id, token=token, status=status)

        # Atualiza cada signer (caso a API tenha retornado tokens individuais)
        signers_data = data.get("signers", [])
        if signers_data:
            for s_data in signers_data:
                email = s_data.get("email")
                signer_token = s_data.get("token")
                if not (email and signer_token):
                    continue
                # Atualiza o signer com base no email
                self.repo.update_signer_token_by_email(doc.id, email, signer_token)

        return doc