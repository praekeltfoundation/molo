from wagtail.core.models import Page
from wagtail.core.utils import WAGTAIL_APPEND_SLASH
from django.urls import reverse


class MoloPage(Page):
    class Meta:
        proxy = True

