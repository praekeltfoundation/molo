import json
import responses

from django.conf import settings

from wagtail.wagtailcore.utils import cautious_slugify
from unicore.content.models import Page, Category, Localisation

from unicore.content import models as eg_models


class ElasticGitTestMixin(object):
    def create_category_data_iter(self, count=2, locale='eng_UK', **kwargs):
        for i in range(count):
            data = {}
            data.update({
                'title': u'Test Category %s' % (i,),
                'language': locale
            })
            data.update(kwargs)
            data.update({
                'slug': cautious_slugify(data['title'])
            })
            yield data, i

    def create_categories(
            self, workspace, count=2, locale='eng_UK', **kwargs):
        categories = []
        for data, i in self.create_category_data_iter(
                count=count, locale=locale, **kwargs):
            category = Category(data)
            workspace.save(
                category, u'Added category %s.' % (i,))
            categories.append(category)

        workspace.refresh_index()
        return categories

    def create_page_data_iter(self, count=2, locale='eng_UK', **kwargs):
        for i in range(count):
            data = {}
            data.update({
                'title': u'Test Page %s' % (i,),
                'content': u'this is sample content for pg %s' % (i,),
                'language': locale
            })
            data.update(kwargs)
            data.update({
                'slug': cautious_slugify(data['title'])
            })
            yield data, i

    def create_pages(
            self, workspace, count=2, locale='eng_UK', **kwargs):
        pages = []
        for data, i in self.create_page_data_iter(
                count=count, locale=locale, **kwargs):
            page = Page(data)
            workspace.save(page, message=u'Added page %s.' % (i,))
            pages.append(page)

        workspace.refresh_index()
        return pages

    def create_localisation(self, workspace, locale='eng_UK', **kwargs):
        data = {'locale': locale}
        data.update(kwargs)
        loc = Localisation(data)
        workspace.save(loc, u'Added localisation %s.' % (locale,))
        workspace.refresh_index()
        return loc

    def mock_get_repos_from_ucd(self, data=[], status=200):
        responses.add(
            responses.GET, '%s/repos.json' % settings.UNICORE_DISTRIBUTE_API,
            body=json.dumps(data),
            content_type="application/json",
            status=status)

    def create_workspace(self, prefix=None, **kw):
        if prefix is None:
            index_prefix = self.mk_index_prefix()
        else:
            index_prefix = '%s-%s' % (self.mk_index_prefix(), prefix)

        ws = self.mk_workspace(index_prefix=index_prefix, **kw)

        ws.setup_custom_mapping(eg_models.Localisation, {
            'properties': {
                'locale': {
                    'type': 'string',
                    'index': 'not_analyzed',
                }
            }
        })

        ws.setup_custom_mapping(eg_models.Category, {
            'properties': {
                'language': {'type': 'string', 'index': 'not_analyzed'},
                'position': {'type': 'integer', 'index': 'not_analyzed'},
            }
        })

        ws.setup_custom_mapping(eg_models.Page, {
            'properties': {
                'language': {'type': 'string', 'index': 'not_analyzed'},
                'position': {'type': 'integer', 'index': 'not_analyzed'},
            }
        })

        return ws

    def create_category(self, *args, **kw):
        [cat] = self.create_categories(*args, count=1, **kw)
        return cat

    def create_page(self, *args, **kw):
        [page] = self.create_pages(*args, count=1, **kw)
        return page

    def add_languages(self, ws, *locales):
        for locale in locales:
            lang = eg_models.Localisation({'locale': locale})
            ws.save(lang, 'Added %s' % locale)

    def catch(self, error_cls, fn):
        error = None

        try:
            fn()
        except error_cls as e:
            error = e

        self.assertTrue(
            error is not None,
            "Expected an error to be raised")

        return error
