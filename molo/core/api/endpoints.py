from wagtail.core.models import Page
from wagtail.core.utils import resolve_model_string
from wagtail.api.v2.endpoints import PagesAPIEndpoint
from wagtail.api.v2.serializers import BaseSerializer
from wagtail.api.v2.utils import BadRequestError
from wagtail.images.api.v2.endpoints import ImagesAPIEndpoint
from wagtail.images.api.v2.endpoints import BaseAPIEndpoint

from molo.core.decorators import prometheus_query_count, request_time

from molo.core.models import (
    SiteLanguage,
    Languages, ArticlePage,
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
        'is_main_language', 'nav_tags__tag'
    ])
    extra_api_fields = ['url', 'live']

    @request_time.time()
    @prometheus_query_count
    def get_queryset(self):
        """"
        This is overwritten in order to not exclude drafts
        and pages submitted for moderation
        """
        request = self.request

        # Allow pages to be filtered to a specific type

        model = request.GET.get('type', Page)

        if model is not Page:
            model_name = request.GET['type']
            try:
                model = resolve_model_string(model_name)
            except LookupError:
                raise BadRequestError("type doesn't exist")

            if not issubclass(model, Page):
                raise BadRequestError("type doesn't exist")

        # Enable filtering by navigation tags
        tag = request.GET.get('nav_tags__tag')
        if model == ArticlePage and tag:
            try:
                # use view_restrictions__restriction_type=None
                # instead of .public()
                queryset = model.objects \
                    .filter(nav_tags__tag=tag, view_restrictions__restriction_type=None)\
                    .descendant_of(request.site.root_page, inclusive=True,)

            except ValueError as e:
                raise BadRequestError(
                    "field filter error. '%s' is not a valid value "
                    "for nav_tags__tag (%s)" % (tag, str(e)))
            return queryset

        return model.objects.filter(view_restrictions__restriction_type=None)\
            .descendant_of(request.site.root_page, inclusive=True)


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
