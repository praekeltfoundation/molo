from treebeard.mp_tree import get_result_class

from wagtail.core.models import Page


class MoloPage(Page):
    class Meta:
        proxy = True

    def exact_type(self):
        return self.__class__.__name__

    def is_content_page(self, page):
        if self.title.lower() == page.lower():
            return True
        else:
            if hasattr(self.specific, 'translated_pages'):
                for translation in self.specific.translated_pages.all():
                    if translation.title.lower() == page.lower():
                        return True
        return False

    def get_top_level_parent(self, locale=None, depth=3):
        # exclude main has no attribute 'language'
        if depth < 1:
            return

        parentpath = self._get_basepath(self.path, depth)
        self._cached_parent_obj = get_result_class(self.__class__)\
            .objects.get(path=parentpath)

        parent = self._cached_parent_obj.specific \
            if hasattr(self._cached_parent_obj, 'specific')\
            else self._cached_parent_obj.specific

        if parent and hasattr(parent, 'language'):
            if locale and parent.language.locale != locale:
                return parent.translated_pages.filter(
                    language__locale=locale, depth=depth
                ).first().specific
        return parent

    @classmethod
    def can_exist_under(cls, parent):
        if getattr(parent, 'specific_class', None):
            return super().can_exist_under(parent)
        return False
