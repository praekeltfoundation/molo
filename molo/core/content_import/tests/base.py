import json
import responses

from django.conf import settings

from wagtail.wagtailcore.utils import cautious_slugify
from unicore.content.models import Page, Category, Localisation


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
