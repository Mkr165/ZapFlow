from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Company, Document, Signer, DocumentStatus
from .serializers import CompanySerializer, DocumentSerializer, SignerSerializer

from documents.usecases.create_document import CreateDocument
from documents.usecases.errors import ValidationError, NotFoundError
from documents.repo.orm import DocumentRepoORM

from rest_framework.decorators import action
from documents.usecases.send_to_zapsign import SendToZapSign
from documents.usecases.get_status import GetZapSignStatus

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
    
    @action(detail=True, methods=["post"])
    def send_to_zapsign(self, request, pk=None):
        pdf_url = request.data.get("pdf_url")
        markdown = request.data.get("markdown_text")
        uc = SendToZapSign(repo=DocumentRepoORM()) 
        try:
            doc = uc.execute(int(pk), pdf_url=pdf_url, markdown_text=markdown)
        except NotFoundError as e:
            return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(self.get_serializer(doc).data, status=status.HTTP_200_OK)

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

class SignerViewSet(viewsets.ModelViewSet):
    queryset = Signer.objects.select_related("document").order_by("-id")
    serializer_class = SignerSerializer
