from wagtail.core.models import Page


class MoloPage(Page):
    class Meta:
        proxy = True
