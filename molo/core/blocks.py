import html2markdown
import re
from bs4 import BeautifulSoup
from django.utils.safestring import mark_safe
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

    def get_api_representation(self, value, context=None):
        """
        This identifies any content that contains html and converts it into
        the quivalent markdown for sending via the API
        """
        # Remove an invalid html tag that is often present in the content
        value = value.replace("</br>", "\n")

        has_html = bool(BeautifulSoup(value, "html.parser").find())
        if not has_html:
            return self.get_prep_value(value)

        # Some content has markdown and html. We convert it to html first
        # to remove duplicate formatting and then to markdown
        html_value = markdown(
            value,
            extensions=[
                'markdown.extensions.fenced_code',
                'codehilite',
            ],
        )
        # This replaces newlines inside paragraphs with a space
        html_value = re.sub(r'\n(?!<p>)', ' ', html_value)

        markdown_value = html2markdown.convert(html_value)

        # Remove any duplicated markdown
        markdown_value = markdown_value.replace("____", "__")
        markdown_value = markdown_value.replace("****", "**")
        # Remove underlines since there isn't a markdown equivalent
        markdown_value = markdown_value.replace("<u>", "")
        markdown_value = markdown_value.replace("</u>", "")
        # Remove any escape characters placed in front of markdown
        markdown_value = markdown_value.replace("\\", "")
        return markdown_value


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
