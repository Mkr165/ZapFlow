# documents/usecases/analyze_document.py
from .errors import NotFoundError
from documents.services.ai import analyze_text

class AnalyzeDocument:
    def __init__(self, repo):
        self.repo = repo

    def execute(self, document_id: int, text: str | None = None) -> dict:
        doc = self.repo.get_document_with_signers(document_id)
        if not doc:
            raise NotFoundError("Documento não encontrado.")
        base_text = (text or doc.name or "").strip()
        return analyze_text(base_text)
