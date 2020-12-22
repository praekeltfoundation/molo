from django.test import TestCase, Client
from django.core.cache import cache
from molo.core.models import Main, SiteLanguageRelation, Languages
from molo.core.tests.base import MoloTestCaseMixin
from molo.core.utils import generate_slug

from wagtail.core.models import Site


class TestSites(TestCase, MoloTestCaseMixin):

    def setUp(self):
        cache.clear()
        self.mk_main()
        self.main = Main.objects.all().first()
        self.english = SiteLanguageRelation.objects.create(
            language_setting=Languages.for_site(self.main.get_site()),
            locale='en',
            is_active=True)
        self.yourmind = self.mk_section(
            self.section_index, title='Your mind')

    def test_two_sites_point_to_one_root_page(self):
        # assert that there is only one site rooted at main
        self.assertEqual(self.main.sites_rooted_here.count(), 1)
        client_1 = Client()
        # add a site that points to the same root page
        site_2 = Site.objects.create(
            hostname=generate_slug('site2'), port=80, root_page=self.main)
        # create a link buetween the current langauges and the new site
        Languages.objects.create(
            site_id=site_2.pk)
        SiteLanguageRelation.objects.create(
            language_setting=Languages.for_site(site_2),
            locale='en',
            is_active=True)
        client_2 = Client(HTTP_HOST=site_2.hostname)

        # assert that there are now two sites rooted at main
        self.assertEqual(self.main.sites_rooted_here.count(), 2)

        # assert that the correct hostname is returned for both sites
        response = client_1.get('/sections-main-1/your-mind/')
        self.assertEqual(response.status_code, 200)
        response = client_2.get(
            site_2.root_url + '/sections-main-1/your-mind/')
        self.assertEqual(response.status_code, 200)
