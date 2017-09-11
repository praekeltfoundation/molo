from wagtail.wagtailcore.models import Page
from wagtail.wagtailcore.utils import resolve_model_string
from wagtail.api.v2.endpoints import PagesAPIEndpoint
from wagtail.api.v2.serializers import BaseSerializer
from wagtail.api.v2.utils import BadRequestError
from wagtail.wagtailimages.api.v2.endpoints import ImagesAPIEndpoint
from wagtail.wagtailimages.api.v2.endpoints import BaseAPIEndpoint

from molo.core.models import (
    SiteLanguage,
    Languages,
)
from molo.core.api.filters import MainLanguageFilter
from molo.core.api.serializers import (
    MoloPageSerializer,
    MoloImageSerializer,
)


class MoloImagesAPIEndpoint(ImagesAPIEndpoint):
    base_serializer_class = MoloImageSerializer
    body_fields = ImagesAPIEndpoint.body_fields + [
        "filename",
        "file",
        "image_url",
        "image_hash",
    ]


class MoloPagesEndpoint(PagesAPIEndpoint):
    base_serializer_class = MoloPageSerializer

    meta_fields = PagesAPIEndpoint.meta_fields + [
        "children",
        "translations",
        "main_language_children",
    ]

    filter_backends = PagesAPIEndpoint.filter_backends + [
        MainLanguageFilter,
    ]

    known_query_parameters = PagesAPIEndpoint.known_query_parameters.union([
        'is_main_language'
    ])
    extra_api_fields = ['url', 'live']

    def get_queryset(self):
        '''
        This is overwritten in order to not exclude drafts
        and pages submitted for moderation
        '''
        request = self.request

        # Allow pages to be filtered to a specific type
        if 'type' not in request.GET:
            model = Page
        else:
            model_name = request.GET['type']
            try:
                model = resolve_model_string(model_name)
            except LookupError:
                raise BadRequestError("type doesn't exist")
            if not issubclass(model, Page):
                raise BadRequestError("type doesn't exist")

        # This is the overwritten line
        queryset = model.objects.public()  # exclude .live()

        # Filter by site
        queryset = queryset.descendant_of(
            request.site.root_page, inclusive=True)

        return queryset


class LanguagesAPIEndpoint(BaseAPIEndpoint):
    base_serializer_class = BaseSerializer
    filter_backends = []
    extra_api_fields = []
    name = 'languages'
    model = SiteLanguage

    def get_queryset(self):
        '''
        Only serve site-specific languages
        '''
        request = self.request
        return (Languages.for_site(request.site)
                         .languages.filter().order_by('pk'))
