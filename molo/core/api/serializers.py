from collections import OrderedDict

from rest_framework import serializers
from wagtail.wagtailcore.models import Page

from molo.core.api.compat import PageSerializer


class PageChildrenField(serializers.Field):
    """
    Serializes the "children" field.

    Example:
    "children": {
        "count": 1,
        "listing_url": "/api/v1/pages/?child_of=2"
    }
    """
    def get_attribute(self, instance):
        return instance

    def to_representation(self, page):
        tree = Page.dump_bulk(page)
        if "children" in tree[0]:
            children = tree[0]["children"]
            return OrderedDict([
                ('count', page.numchild),
                ("items", children),
            ])


class MoloPageSerializer(PageSerializer):
    children = PageChildrenField(read_only=True)
