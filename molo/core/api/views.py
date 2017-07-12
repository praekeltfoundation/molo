from rest_framework.views import APIView
from rest_framework.response import Response

from molo.core.models import SiteLanguage
from molo.core.api.serializers import SiteLanguageSerializer
from rest_framework import generics

# does it work with multi-site ?
class SiteLanguagesList(generics.ListAPIView):
    queryset = SiteLanguage.objects.all()
    serializer_class = SiteLanguageSerializer
