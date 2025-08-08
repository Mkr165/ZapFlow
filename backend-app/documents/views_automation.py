# documents/views_automation.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.db.models import Count

from .auth import ApiKeyAuthentication
from .serializers import (
    AutomationCreateSendSerializer,
    AutomationAnalysisInputSerializer,
    AutomationReportFilterSerializer,
    ReportDocumentSerializer,
)
from documents.repo.orm import DocumentRepoORM
from documents.models import Document
from documents.usecases.analyze_document import AnalyzeDocument
 
class AutomationCreateSendView(APIView):
    authentication_classes = [ApiKeyAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        ser = AutomationCreateSendSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        payload = ser.validated_data

        from documents.usecases.create_document import CreateDocument
        from documents.usecases.send_to_zapsign import SendToZapSign

        repo = DocumentRepoORM()
        doc = CreateDocument(repo).execute({
            "company": request.company.id,
            "name": payload["name"],
            "created_by": payload.get("created_by") or "automation",
            "signers": payload["signers"],
        })
        if payload["content_type"] == "markdown":
            repo.upsert_document_content(doc.id, "markdown", markdown_text=payload["markdown_text"])
        else:
            repo.upsert_document_content(doc.id, "url_pdf", pdf_url=payload["pdf_url"])

        doc = SendToZapSign(repo).execute(doc.id)

        return Response({
            "document_id": doc.id,
            "status": doc.status,
            "open_id": getattr(doc, "open_id", None),
            "token": getattr(doc, "token", None),
        }, status=status.HTTP_201_CREATED)

class AutomationAnalysisView(APIView):
    authentication_classes = [ApiKeyAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk: int):
        ser = AutomationAnalysisInputSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        text_override = ser.validated_data.get("text") 
        uc = AnalyzeDocument(repo=DocumentRepoORM())
        result = uc.execute(int(pk), text=text_override)
        return Response(result, status=status.HTTP_200_OK)

class AutomationReportView(APIView):
    authentication_classes = [ApiKeyAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        s = AutomationReportFilterSerializer(data=request.query_params)
        s.is_valid(raise_exception=True)
        q = s.validated_data

        qs = (
            Document.objects.filter(company=request.company)
            .annotate(signer_count=Count("signers"))
            .order_by("-created_at")
        )
        if q.get("status"):
            qs = qs.filter(status=q["status"])
        if q.get("date_from"):
            qs = qs.filter(created_at__date__gte=q["date_from"])
        if q.get("date_to"):
            qs = qs.filter(created_at__date__lte=q["date_to"])

        summary = dict(
            qs.values_list("status").annotate(total=Count("id"))
        )
        data = ReportDocumentSerializer(qs, many=True).data
        return Response({"summary": summary, "items": data}, status=200)