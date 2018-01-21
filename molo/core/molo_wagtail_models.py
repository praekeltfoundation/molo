from wagtail.wagtailcore.models import Page


class MoloPage(Page):
    def get_url_parts(self, request=None):
        for (site_id, root_path, root_url) in \
                self._get_site_root_paths(request):
            if hasattr(request, 'site') and site_id != request.site.pk:
                super(MoloPage, self).get_url_parts(request)
