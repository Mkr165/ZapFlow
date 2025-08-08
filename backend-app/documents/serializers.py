from rest_framework import serializers
from rest_framework.reverse import reverse
from .models import Company, Document, Signer, DocumentContent
from django.db import transaction
from django.db.models import Count
class CompanySerializer(serializers.ModelSerializer):
    links = serializers.SerializerMethodField()

    class Meta:
        model = Company
        fields = ["id", "name", "api_token", "created_at", "last_updated_at", "links"]

    def get_links(self, obj):
        req = self.context.get("request")
        return {
            "self":      reverse("company-detail", args=[obj.pk], request=req), 
            "documents": reverse("document-list", request=req) + f"?company={obj.pk}",
        }


class SignerSerializer(serializers.ModelSerializer):
    links = serializers.SerializerMethodField()

    class Meta: 
        model = Signer 
        fields = ["id", "name", "email", "external_id","status","links"]
        extra_kwargs = {
            "id": {"read_only": True},
        }

    def get_links(self, obj):
        req = self.context.get("request") 
        return {
            "self":     reverse("signer-detail", args=[obj.pk], request=req),
            "document": reverse("document-detail", args=[obj.document_id], request=req),
        }


class DocumentSerializer(serializers.ModelSerializer):
    signers = SignerSerializer(many=True, required=False)
    links = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = [
            "id", "company", "name", "created_by", "external_id",
            "status", "open_id", "token", "created_at", "last_updated_at",
            "signers", "links",
        ]
        read_only_fields = ["status", "open_id", "token", "created_at", "last_updated_at"]

    @transaction.atomic
    def update(self, instance, validated_data):
        # pega e remove os signers do payload
        signers_data = validated_data.pop("signers", None)

        # atualiza campos simples do documento
        for attr, val in validated_data.items():
            setattr(instance, attr, val)
        instance.save()

        # se veio "signers", aplica política de "replace-all"
        if signers_data is not None:
            if len(signers_data) == 0:
                raise serializers.ValidationError({"signers": "Informe pelo menos 1 signatário."})

            # remove os atuais e recria (simples e atômico)
            instance.signers.all().delete()
            Signer.objects.bulk_create([
                Signer(
                    document=instance,
                    name=s["name"],
                    email=s["email"],
                    external_id=s.get("external_id", "") or ""
                )
                for s in signers_data
            ])

        return instance

    def get_links(self, obj):
        req = self.context.get("request")
        return {
            "self":     reverse("document-detail", args=[obj.pk], request=req),
            "send":     reverse("document-send-to-zapsign", args=[obj.pk], request=req),
            "status":   reverse("document-status", args=[obj.pk], request=req),
            "content":  reverse("document-content", args=[obj.pk], request=req),
            "analysis": reverse("document-analysis", args=[obj.pk], request=req),
        }


class DocumentContentSerializer(serializers.ModelSerializer):
    links = serializers.SerializerMethodField()

    class Meta:
        model = DocumentContent
        fields = ["content_type", "markdown_text", "pdf_url", "links"]

    def get_links(self, obj):
        req = self.context.get("request")
        return {
            "document": reverse("document-detail", args=[obj.document_id], request=req),
        }

class AutomationCreateSendSerializer(serializers.Serializer):
    name = serializers.CharField()
    created_by = serializers.CharField(required=False, allow_blank=True)
    signers = serializers.ListSerializer(child=serializers.DictField(), allow_empty=False)
    content_type = serializers.ChoiceField(choices=["markdown", "url_pdf"])
    markdown_text = serializers.CharField(required=False, allow_blank=True)
    pdf_url = serializers.URLField(required=False, allow_blank=True)

    def validate(self, data):
        ct = data["content_type"]
        if ct == "markdown" and not data.get("markdown_text"):
            raise serializers.ValidationError("markdown_text é obrigatório quando content_type=markdown.")
        if ct == "url_pdf" and not data.get("pdf_url"):
            raise serializers.ValidationError("pdf_url é obrigatório quando content_type=url_pdf.")
        return data
    
 
class ReportDocumentSerializer(serializers.ModelSerializer):
    signer_count = serializers.IntegerField(read_only=True)
    signers = SignerSerializer(many=True, required=False)
    class Meta:
        model = Document
        fields = ("id", "name", "status", "created_at", "last_updated_at", "signer_count","signers")


# análise via automação
class AutomationAnalysisInputSerializer(serializers.Serializer):
    # Se enviar "text", analisamos esse texto; se não enviar, usamos o conteúdo salvo (markdown/url_pdf)
    text = serializers.CharField(required=False, allow_blank=True)

class AutomationReportFilterSerializer(serializers.Serializer):
    status = serializers.ChoiceField(
        choices=["draft","sent","signed","canceled", "pending"], required=False
    )
    date_from = serializers.DateField(required=False)
    date_to = serializers.DateField(required=False)

    def validate(self, data):
        df, dt = data.get("date_from"), data.get("date_to")
        if df and dt and df > dt:
            raise serializers.ValidationError("date_from não pode ser maior que date_to.")
        return data