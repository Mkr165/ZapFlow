from .errors import ValidationError

class CreateDocument:
    """
    Regras para criar Documento (de acordo com o diagrama):
    - company (ID), name e pelo menos 1 signer são obrigatórios
    - status/open_id/token NÃO vêm na criação (defaults do model)
    - normaliza e valida signers
    """
    def __init__(self, repo):
        self.repo = repo

    def execute(self, data: dict):
        name = (data.get("name") or "").strip()
        if not name:
            raise ValidationError("Nome do documento é obrigatório.")

        company_id = data.get("company")
        if not company_id:
            raise ValidationError("company (ID) é obrigatório.")

        raw_signers = data.get("signers", [])
        if not isinstance(raw_signers, list) or not raw_signers:
            raise ValidationError("Pelo menos um signatário é obrigatório.")

        # normaliza signers
        signers = []
        seen_emails = set()
        for s in raw_signers:
            n = (s.get("name") or "").strip()
            e = (s.get("email") or "").strip().lower()
            if not n or not e:
                raise ValidationError("Cada signatário precisa de name e email.")
            if e in seen_emails:
                raise ValidationError(f"Email duplicado entre signatários: {e}")
            seen_emails.add(e)
            signers.append({
                "name": n,
                "email": e,
                "external_id": (s.get("external_id") or "").strip(),
            })

        payload = {
            "company": company_id,
            "name": name,
            "created_by": (data.get("created_by") or "").strip(),
            "external_id": (data.get("external_id") or "").strip(),
            "signers": signers,
        }
        return self.repo.create_document_with_signers(payload)
