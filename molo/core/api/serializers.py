from collections import OrderedDict

from rest_framework import serializers

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
        if page.get_children():
            items = []
            for item in page.get_children():
                items.append(item.id)
            return OrderedDict([
                ("items", items),
            ])


class MoloPageSerializer(PageSerializer):
    children = PageChildrenField(read_only=True)
