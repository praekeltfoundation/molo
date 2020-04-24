from bs4 import BeautifulSoup
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from markdown import markdown

from wagtail.core import blocks
from wagtailmedia.blocks import AbstractMediaChooserBlock
from wagtail.images.blocks import ImageChooserBlock


class MarkDownBlock(blocks.TextBlock):
    """ MarkDown Block """

    class Meta:
        icon = 'code'

    def render_basic(self, value, context=None):
        md = markdown(
            value,
            extensions=[
                'markdown.extensions.fenced_code',
                'codehilite',
            ],
        )
        return mark_safe(md)

    def clean(self, value):
        value = super().clean(value)

        # Return an error message if there is html in the value
        has_html = bool(BeautifulSoup(value, "html.parser").find())
        if has_html:
            raise ValidationError(
                    _('Please use MarkDown for formatting text instead of '
                      'HTML.')
                )

        return value


class MultimediaBlock(AbstractMediaChooserBlock):
    class Meta:
        icon = 'media'

    def render_basic(self, value, context=None):
        if not value:
            return ''

        if value.type == 'video':
            player_code = '''<div><video width="320" height="240" controls>
<source src="{0}" type="video/mp4">Click here to download
<a href="{0}">{1}</a></video></div>'''

        else:
            player_code = '''<div><audio controls><source src="{0}"
type="audio/mpeg">Click here to download
<a href="{0}">{1}</a></audio></div>'''

        md = markdown(
            player_code.format(value.file.url, value.title),
            extensions=[
                'markdown.extensions.fenced_code',
                'codehilite',
            ],
        )

        return mark_safe(md)


class SocialMediaLinkBlock(blocks.StructBlock):
    title = blocks.CharBlock(required=True)
    link = blocks.CharBlock(required=True)
    image = ImageChooserBlock()
