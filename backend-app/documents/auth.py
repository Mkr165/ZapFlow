# documents/auth.py
from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions
from documents.models import Company

APIKEY_HEADER = "HTTP_X_API_KEY"

class ApiKeyUser:
    def __init__(self, company):
        self.company = company
    @property
    def is_authenticated(self):
        return True

class ApiKeyAuthentication(BaseAuthentication):
    def authenticate(self, request):
        api_key = request.META.get(APIKEY_HEADER)
        if not api_key:
            return None
        company = Company.objects.filter(api_token=api_key).first()
        if not company:
            raise exceptions.AuthenticationFailed("API key inválida.")
        request.company = company
        return (ApiKeyUser(company), None)  
