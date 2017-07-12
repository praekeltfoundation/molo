from wagtail.api.v2.endpoints import PagesAPIEndpoint
from wagtail.wagtailimages.api.v2.endpoints import ImagesAPIEndpoint
from molo.core.api.serializers import MoloPageSerializer


class MoloImagesAPIEndpoint(ImagesAPIEndpoint):
    body_fields = ImagesAPIEndpoint.body_fields + [
        "file",
    ]


class MoloPagesEndpoint(PagesAPIEndpoint):
    base_serializer_class = MoloPageSerializer

    meta_fields = PagesAPIEndpoint.meta_fields + [
        "children"
    ]
