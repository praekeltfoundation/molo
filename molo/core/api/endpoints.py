from wagtail.api.v2.endpoints import PagesAPIEndpoint
from wagtail.wagtailimages.api.v2.endpoints import ImagesAPIEndpoint
from wagtail.wagtailimages.api.v2.endpoints import BaseAPIEndpoint

from molo.core.models import SiteLanguage
from molo.core.api.serializers import (
    MoloPageSerializer,
    SiteLanguageSerializer,
)


class MoloImagesAPIEndpoint(ImagesAPIEndpoint):
    body_fields = ImagesAPIEndpoint.body_fields + [
        "file",
    ]


class MoloPagesEndpoint(PagesAPIEndpoint):
    base_serializer_class = MoloPageSerializer

    meta_fields = PagesAPIEndpoint.meta_fields + [
        "children"
    ]


class LanguagesAPIEndpoint(BaseAPIEndpoint):
    base_serializer_class = SiteLanguageSerializer
    filter_backends = []
    extra_api_fields = []
    name = 'languages'
    model = SiteLanguage
