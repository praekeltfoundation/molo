Writing Test Cases
~~~~~~~~~~~~~~~~~~

Use Molo test mixin `molo.core.tests.base.MoloTestCaseMixin`

The Molo test mixin contains helper methods to generate test content necessary for the main sight.

::

    class MyTest(MoloTestCaseMixin, TestCase):

        def setUp(self):
            self.mk_main()
            main = Main.objects.all().first()
            lang = Languages.for_site(main.get_site()
            self.english = SiteLanguageRelation.objects.create(
                language_setting=lang), locale='en', is_active=True)

            self.user = User.objects.create_user(
                'test', 'test@example.org', 'test')

            self.client = Client()
            ...

        def test_register_auto_login(self):
            # Not logged in, redirects to login page
            login_url = reverse('molo.profiles:edit_my_profile')
            expected_url = '/login/?next=/profiles/edit/myprofile/'

            response = self.client.get(login_url)
            self.assertEqual(response.status_code, 302)
            self.assertEqual(response['Location'], expected_url)


`MoloTestCaseMixin` methods

    * login()

        Creates a superuser and logs in
        username='superuser', email='superuser@email.com', password='pass'

    * mk_root()

        Creates a root page accessible on the application application root url

    * mk_main(title='Main', slug='main'), mk_main2(title='main2', slug='main2', path='4098')

        Create the main page of your molo test site

    * mk_tag(parent, slug=None, \**kwargs), mk_tags(parent, count=2, \**kwargs)

        Attach/add tag to parent page

    * mk_reaction_question(parent, article, \**kwargs)

        Create test reaction question for an article

    * mk_sections(parent, count=2, \**kwargs), mk_section(parent \**kwargs)

        Create test section(s) page content in parent page

    * mk_articles(parent, count=2, \**kwargs), mk_article(parent, \**kwargs)

        Create test article(s) page content in parent page

    * mk_banners(parent, count=2, \**kwargs), mk_banner(parent, \**kwargs)

        Create test banner(s) page content in parent page

    * mk_translation(source, language, translation)
      mk_section_translation(source, language, \**kwargs)
      mk_article_translation(source, language, \**kwargs)
      mk_tag_translation(source, language, \**kwargs)
      mk_reaction_translation(source, language, \**kwargs)

        Create a translated version of the source (Page)
