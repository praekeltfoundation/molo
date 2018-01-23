from wagtail.wagtailcore.models import Page
from wagtail.wagtailcore.utils import WAGTAIL_APPEND_SLASH
from django.urls import reverse


class MoloPage(Page):
    class Meta:
        proxy = True

    def get_url_parts(self, request=None):
        for (site_id, root_path, root_url) in self._get_site_root_paths(
                request):
            if hasattr(request, 'site') and site_id != request.site.pk:
                continue
            if self.url_path.startswith(root_path):
                page_path = reverse('wagtail_serve', args=(
                    self.url_path[len(root_path):],))

                # Remove the trailing slash from the URL reverse generates if
                # WAGTAIL_APPEND_SLASH is False and we're not trying to serve
                # the root path
                if not WAGTAIL_APPEND_SLASH and page_path != '/':
                    page_path = page_path.rstrip('/')
                return (site_id, root_url, page_path)
