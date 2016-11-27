from molo.core.content_import.api.compat import ImagesAPIEndpoint


class MoloImagesAPIEndpoint(ImagesAPIEndpoint):
    extra_body_fields = ImagesAPIEndpoint.extra_body_fields + [
        "file",
    ]
