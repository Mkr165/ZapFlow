from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .auth import ApiKeyAuthentication
from .serializers import AutomationCreateSendSerializer
from documents.usecases.create_document import CreateDocument
from documents.usecases.send_to_zapsign import SendToZapSign
from documents.repo.orm import DocumentRepoORM

class AutomationCreateSendView(APIView):
    authentication_classes = [ApiKeyAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        ser = AutomationCreateSendSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        payload = ser.validated_data

        repo = DocumentRepoORM()

        # 1) cria doc (draft)
        doc = CreateDocument(repo).execute({
            "company": request.company.id,
            "name": payload["name"],
            "created_by": payload.get("created_by") or "automation",
            "signers": payload["signers"],
        })

        # 2) define conteúdo
        if payload["content_type"] == "markdown":
            repo.upsert_document_content(doc.id, "markdown", markdown_text=payload["markdown_text"])
        else:
            repo.upsert_document_content(doc.id, "url_pdf", pdf_url=payload["pdf_url"])

        # 3) envia pra ZapSign
        doc = SendToZapSign(repo).execute(doc.id)

        return Response({
            "document_id": doc.id,
            "status": doc.status,
            "open_id": getattr(doc, "open_id", None),
            "token": getattr(doc, "token", None),
        }, status=status.HTTP_201_CREATED)
