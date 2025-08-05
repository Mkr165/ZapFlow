from django.db import models

class Company(models.Model):
    name = models.CharField(max_length=120)
    api_token = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class DocumentStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    SENT = "sent", "Sent"
    SIGNED = "signed", "Signed"
    CANCELED = "canceled", "Canceled"


class Document(models.Model):
    # Campo Python = company; coluna no DB = company_id (igual ao diagrama)
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="documents",
        db_column="company_id",      # <- garante o nome da coluna do diagrama
    )
    open_id = models.BigIntegerField(
        null=True, blank=True, db_index=True, db_column="openId"   # <- coluna camelCase
    )
    token = models.CharField(max_length=200, blank=True, default="")
    name = models.CharField(max_length=200)
    status = models.CharField(
        max_length=20,
        choices=DocumentStatus.choices,
        default=DocumentStatus.DRAFT,
        db_index=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated_at = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=120, blank=True, default="")
    external_id = models.CharField(
        max_length=120, blank=True, default="", db_index=True, db_column="externalId"  # <- coluna camelCase
    )

    def __str__(self):
        return f"{self.name} ({self.status})"


class SignerStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    SIGNED = "signed", "Signed"
    REJECTED = "rejected", "Rejected"


class Signer(models.Model):
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name="signers"
    )
    token = models.CharField(max_length=200, blank=True, default="")
    status = models.CharField(
        max_length=20,
        choices=SignerStatus.choices,
        default=SignerStatus.PENDING,
        db_index=True,
    )
    name = models.CharField(max_length=120)
    email = models.EmailField(db_index=True)
    external_id = models.CharField(
        max_length=120, blank=True, default="", db_index=True, db_column="externalId"  # <- alinhei ao diagrama
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["document", "email"], name="uniq_signer_per_document")
        ]

    def __str__(self):
        return f"{self.name} <{self.email}>"
