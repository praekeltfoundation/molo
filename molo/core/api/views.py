from molo.core.models import SiteLanguage
from molo.core.api.serializers import SiteLanguageSerializer
from rest_framework import generics


class SiteLanguagesList(generics.ListAPIView):
    queryset = SiteLanguage.objects.all()
    serializer_class = SiteLanguageSerializer
