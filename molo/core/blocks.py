from django.utils.safestring import mark_safe
from markdown import markdown

from wagtail.wagtailcore import blocks
from wagtailmedia.blocks import AbstractMediaChooserBlock


class MarkDownBlock(blocks.TextBlock):
    """ MarkDown Block """

    class Meta:
        icon = 'code'

    def render_basic(self, value):
        md = markdown(
            value,
            [
                'markdown.extensions.fenced_code',
                'codehilite',
            ],
        )
        return mark_safe(md)


class MultimediaBlock(AbstractMediaChooserBlock):
    class Meta:
        icon = 'media'

    def render_basic(self, value):
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
            [
                'markdown.extensions.fenced_code',
                'codehilite',
            ],
        )

        return mark_safe(md)
