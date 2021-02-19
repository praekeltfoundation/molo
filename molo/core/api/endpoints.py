from wagtail.core.models import Page
from wagtail.core.utils import resolve_model_string
from wagtail.api.v2.views import PagesAPIViewSet
from wagtail.api.v2.serializers import BaseSerializer
from wagtail.api.v2.utils import BadRequestError
from wagtail.images.api.v2.views import ImagesAPIViewSet
from wagtail.api.v2.views import BaseAPIViewSet

from molo.core.models import (
    SiteLanguage,
    Languages, ArticlePage,
)
from molo.core.api.filters import MainLanguageFilter
from molo.core.api.serializers import (
    MoloPageSerializer,
    MoloImageSerializer,
)


class MoloImagesAPIEndpoint(ImagesAPIViewSet):
    base_serializer_class = MoloImageSerializer
    body_fields = ImagesAPIViewSet.body_fields + [
        "filename",
        "file",
        "image_url",
        "image_hash",
    ]


class MoloPagesEndpoint(PagesAPIViewSet):
    base_serializer_class = MoloPageSerializer

    meta_fields = PagesAPIViewSet.meta_fields + [
        "children",
        "translations",
        "main_language_children",
    ]

    filter_backends = PagesAPIViewSet.filter_backends + [
        MainLanguageFilter,
    ]

    known_query_parameters = PagesAPIViewSet.known_query_parameters.union([
        'is_main_language', 'nav_tags__tag'
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
            self.request._wagtail_site.root_page, inclusive=True)

        # Enable filtering by navigation tags
        if model == ArticlePage and 'nav_tags__tag' in request.GET:
            try:
                queryset = queryset.filter(
                    nav_tags__tag=request.GET['nav_tags__tag'])
            except ValueError as e:
                raise BadRequestError(
                    "field filter error. '%s' is not a valid value "
                    "for nav_tags__tag (%s)" % (
                        request.GET['nav_tags__tag'],
                        str(e)
                    ))

        return queryset


class LanguagesAPIEndpoint(BaseAPIViewSet):
    base_serializer_class = BaseSerializer
    filter_backends = []
    extra_api_fields = []
    name = 'languages'
    model = SiteLanguage

    def get_queryset(self):
        '''
        Only serve site-specific languages
        '''
        site = self.request._wagtail_site
        return (Languages.for_site(site)
                         .languages.filter().order_by('pk'))
