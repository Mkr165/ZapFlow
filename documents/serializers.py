from rest_framework import serializers
from .models import Company, Document, Signer

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ["id", "name", "api_token", "created_at", "last_updated_at"]

class SignerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Signer
        fields = ["id", "token", "status", "name", "email", "external_id"]

class DocumentSerializer(serializers.ModelSerializer):
    signers = SignerSerializer(many=True, required=False)

    class Meta:
        model = Document
        fields = ["id","company","name","created_by","external_id",
                  "status","open_id","token","created_at","last_updated_at","signers"]
        read_only_fields = ["status","open_id","token","created_at","last_updated_at"]
