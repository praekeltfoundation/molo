from molo.core.content_import.api.compat import ImagesAPIEndpoint
from molo.core.content_import.api.serializers import MoloImageSerializer


class MoloImagesAPIEndpoint(ImagesAPIEndpoint):
    base_serializer_class = MoloImageSerializer

    extra_body_fields = ImagesAPIEndpoint.extra_body_fields + [
        'file',
        'original',
    ]
