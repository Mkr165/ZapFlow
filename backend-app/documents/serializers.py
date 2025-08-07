from rest_framework import serializers
from rest_framework.reverse import reverse
from .models import Company, Document, Signer, DocumentContent
from django.db import transaction
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
        fields = ["id", "name", "email", "external_id","links"]
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
