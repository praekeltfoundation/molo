class PageEffectiveImageMixin(object):
    def get_effective_image(self):
        if self.image:
            return self.image
        page = self.get_main_language_page()
        if page.specific.image:
            return page.specific.get_effective_image()
        return ''
