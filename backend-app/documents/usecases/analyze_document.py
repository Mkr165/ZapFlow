# documents/usecases/analyze_document.py
from documents.services.pdf_text import pdf_url_to_text
from documents.services.ai import analyze_text
from documents.usecases.errors import ValidationError 

class AnalyzeDocument:
    def __init__(self, repo): self.repo = repo

    def execute(self, doc_id: int, text: str | None = None):
        doc = self.repo.get_document_with_signers(doc_id)
        if not text:
            # tenta usar conteúdo salvo
            content = getattr(doc, "content", None)
            if not content:
                raise ValidationError("Documento sem conteúdo definido.")
            if content.content_type == "markdown":
                text = content.markdown_text or ""
            else: 
                print('verificando pdf url',content.pdf_url)                          # url_pdf
                text = pdf_url_to_text(content.pdf_url)

        if len(text.strip()) < 30:
            raise ValidationError("Texto insuficiente para análise.")

        return analyze_text(text)
