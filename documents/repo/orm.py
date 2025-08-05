from documents.models import Company, Document, Signer
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
