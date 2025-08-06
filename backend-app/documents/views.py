from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Company, Document, Signer, DocumentStatus, DocumentContent
from .serializers import CompanySerializer, DocumentContentSerializer, DocumentSerializer, SignerSerializer

from documents.usecases.create_document import CreateDocument
from documents.usecases.errors import ValidationError, NotFoundError
from documents.repo.orm import DocumentRepoORM

from rest_framework.decorators import action
from documents.usecases.send_to_zapsign import SendToZapSign
from documents.usecases.get_status import GetZapSignStatus
from documents.usecases.analyze_document import AnalyzeDocument

from django.shortcuts import get_object_or_404
 
class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all().order_by("-id")
    serializer_class = CompanySerializer

class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.select_related("company").prefetch_related("signers").order_by("-created_at")
    serializer_class = DocumentSerializer

    def create(self, request, *args, **kwargs):
        uc = CreateDocument(repo=DocumentRepoORM())
        try:
            doc = uc.execute(request.data.copy())
        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except NotFoundError as e:
            return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)
        return Response(self.get_serializer(doc).data, status=status.HTTP_201_CREATED)
    
    def perform_destroy(self, instance):
        # guard-rail de negócio (rápido): não permitir excluir assinado
        if instance.status == DocumentStatus.SIGNED:
            raise ValidationError("Documento assinado não pode ser excluído.")
        instance.delete()
    
    @action(detail=True, methods=["get"])
    def status(self, request, pk=None):
        uc = GetZapSignStatus(repo=DocumentRepoORM())
        try:
            out = uc.execute(int(pk))
        except NotFoundError as e:
            return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(out, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"])
    def status(self, request, pk=None):
        uc = GetZapSignStatus(repo=DocumentRepoORM())
        try:
            out = uc.execute(int(pk))
        except NotFoundError as e:
            return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(out, status=status.HTTP_200_OK) 
  
    
    @action(detail=True, methods=["post"])
    def analysis(self, request, pk=None):
        txt = request.data.get("text")
        uc = AnalyzeDocument(repo=DocumentRepoORM())
        try:
            out = uc.execute(int(pk), text=txt)
        except NotFoundError as e:
            return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)
        return Response(out, status=status.HTTP_200_OK)  

    @action(detail=True, methods=["get", "put", "patch"])
    def content(self, request, pk=None):
        doc = self.get_object()

        # GET → retorna conteúdo atual
        if request.method == "GET":
            body = getattr(doc, "content", None)
            if not body:
                return Response({"detail": "Sem conteúdo definido."}, status=status.HTTP_404_NOT_FOUND)
            return Response(DocumentContentSerializer(body).data, status=status.HTTP_200_OK)

        # PUT/PATCH → salva conteúdo
        ctype = request.data.get("content_type", "markdown")
        md = request.data.get("markdown_text", "")
        url = request.data.get("pdf_url", "")

        if ctype not in ("markdown", "url_pdf"):
            return Response({"detail": "content_type inválido."}, status=status.HTTP_400_BAD_REQUEST)
        if ctype == "markdown" and not md:
            return Response({"detail": "Informe markdown_text."}, status=status.HTTP_400_BAD_REQUEST)
        if ctype == "url_pdf" and not url:
            return Response({"detail": "Informe pdf_url."}, status=status.HTTP_400_BAD_REQUEST)

        body, created = DocumentContent.objects.get_or_create(document=doc)
        if ctype == "markdown":
            body.content_type, body.markdown_text, body.pdf_url = "markdown", md, ""
        else:
            body.content_type, body.markdown_text, body.pdf_url = "url_pdf", "", url

        body.save(update_fields=["content_type", "markdown_text", "pdf_url"])
        return Response(
            DocumentContentSerializer(body).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )


class SignerViewSet(viewsets.ModelViewSet):
    queryset = Signer.objects.select_related("document").order_by("-id")
    serializer_class = SignerSerializer
