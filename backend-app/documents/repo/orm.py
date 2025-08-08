from documents.models import Company, Document, DocumentContent, Signer
from documents.usecases.errors import NotFoundError

class DocumentRepoORM:
    def create_document_with_signers(self, data: dict) -> Document:
        company = Company.objects.filter(id=data["company"]).first()
        if not company:
            raise NotFoundError("Empresa não encontrada.")

        doc = Document.objects.create(
            company=company,
            name=data["name"],
            created_by=data.get("created_by", ""),
            external_id=data.get("external_id", ""),
            # status/open_id/token: defaults do model
        )

        for s in data.get("signers", []):
            Signer.objects.create(
                document=doc,
                name=s["name"],
                email=s["email"],
                external_id=s.get("external_id", ""),
            )
        return doc
    
    def get_document_with_signers(self, doc_id: int) -> Document:
        doc = Document.objects.select_related("company").prefetch_related("signers").filter(id=doc_id).first()
        if not doc:
            raise NotFoundError("Documento não encontrado.")
        return doc

    def save_document_fields(self, doc: Document, **fields) -> Document:
        for k, v in fields.items():
            setattr(doc, k, v)
        doc.save(update_fields=list(fields.keys()))
        return doc
    
    def update_signer_token_by_email(self, document_id: int, email: str, token: str):
        try:
            signer = Signer.objects.get(document_id=document_id, email__iexact=email)
            signer.token = token
            signer.save()
        except Signer.DoesNotExist:
            print(f"Signer com email {email} não encontrado para o documento {document_id}")
    
    def update_signer_status_token_by_email(self, document_id: int, email: str, status=None, token=None):
        from documents.models import Signer
        s = Signer.objects.filter(
            document_id=document_id,
            email__iexact=email
        ).first()
        if not s:
            return
        fields = []
        if status:
            s.status = status
            fields.append("status")
        if token:
            s.token = token
            fields.append("token")
        if fields:
            s.save(update_fields=fields)


    def upsert_document_content(
        self,
        document_id: int,
        content_type: str,
        *,
        markdown_text: str = "",
        pdf_url: str = "",
    ):
        # pega a instância do Document 
        doc = Document.objects.get(id=document_id)

        # OneToOne: cria ou atualiza o conteúdo
        content, _ = DocumentContent.objects.get_or_create(document=doc)

        content.content_type = content_type
        if content_type == "markdown":
            content.markdown_text = markdown_text or ""
            content.pdf_url = ""
        else:  # "url_pdf"
            content.pdf_url = pdf_url or ""
            content.markdown_text = ""

        content.save(update_fields=["content_type", "markdown_text", "pdf_url"])
        return content
