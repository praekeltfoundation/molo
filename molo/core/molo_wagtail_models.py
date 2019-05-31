from treebeard.mp_tree import get_result_class

from wagtail.core.models import Page


class MoloPage(Page):
    class Meta:
        proxy = True

    def get_top_level_parent(self, locale=None, depth=3):
        # exclude main has no attribute 'language'
        if depth < 1:
            return

        parentpath = self._get_basepath(self.path, depth)
        self._cached_parent_obj = get_result_class(self.__class__)\
            .objects.get(path=parentpath)

        parent = self._cached_parent_obj.specific \
            if hasattr(self._cached_parent_obj, 'specific')\
            else self._cached_parent_obj

        if parent and hasattr(parent, 'language'):
            if locale and parent.language.locale != locale:
                return parent.translated_pages.filter(
                    language__locale=locale, depth=depth
                ).first().specific
        return parent
