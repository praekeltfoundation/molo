from molo.core.api.compat import ImagesAPIEndpoint, PagesAPIEndpoint
from molo.core.api.serializers import MoloPageSerializer

class MoloImagesAPIEndpoint(ImagesAPIEndpoint):
    extra_body_fields = ImagesAPIEndpoint.extra_body_fields + [
        "file",
    ]


class MoloPagesEndpoint(PagesAPIEndpoint):
    base_serializer_class = MoloPageSerializer

    extra_meta_fields = PagesAPIEndpoint.extra_meta_fields + [
        "children"
    ]
