import json
import requests

from django.shortcuts import get_object_or_404

from elasticgit.workspace import RemoteWorkspace

from molo.core.models import Main
from molo.core.models import (
    SiteLanguage, SectionPage, ArticlePage, FooterPage)

from rest_framework.decorators import (
    api_view, authentication_classes, permission_classes)
from rest_framework.response import Response
from rest_framework.authentication import (
    SessionAuthentication, BasicAuthentication)
from rest_framework.permissions import IsAuthenticated

from unicore.content.models import Localisation, Category, Page


@api_view(['GET'])
def get_repos(request):
    response = requests.get('http://localhost:6543/repos.json').json()
    return Response({
        'repos': [repo.get('name') for repo in response]})


@api_view(['GET'])
def get_repo_languages(request, name):
    ws = RemoteWorkspace('http://localhost:6543/repos/%s.json' % name)
    ws.sync(Localisation)

    return Response({
        'locales': [l.locale for l in ws.S(Localisation).all()],
    })


@api_view(['GET'])
def get_available_languages(request):
    return Response({
        'locales': [{
            'locale': l.locale,
            'name': l.get_locale_display(),
            'is_main_language': l.is_main_language}
            for l in SiteLanguage.objects.all()],
    })


@api_view(['POST'])
@authentication_classes((SessionAuthentication, BasicAuthentication))
@permission_classes((IsAuthenticated,))
def import_content(request, name):

    def get_or_create(cls, obj, parent):
        if cls.objects.filter(uuid=obj.uuid).exists():
            instance = cls.objects.get(uuid=obj.uuid)
            instance.title = obj.title
            print 'updated', obj.title
            return instance

        instance = cls(uuid=obj.uuid, title=obj.title)
        parent.add_child(instance=instance)
        print 'created', obj.title
        return instance

    ws = RemoteWorkspace('http://localhost:6543/repos/%s.json' % name)
    ws.sync(Localisation)
    ws.sync(Category)
    ws.sync(Page)

    # create wagtail content

    locales = request.data.get('locales')
    for selected_locale in locales:
        site_language = get_object_or_404(
            SiteLanguage, locale=selected_locale.get('site_language'))

        if site_language.is_main_language:
            main = Main.objects.all().first()
            for c in ws.S(Category).filter(
                    language=selected_locale.get('locale')
            ).order_by('position')[:10000]:  # S() only returns 10 results if you don't ask for more
                section = get_or_create(SectionPage, c, main)
                section.description = c.subtitle
                # TODO: image
                section.save_revision().publish()

            for p in ws.S(Page).filter(
                language=selected_locale.get('locale')
            ).order_by('position')[:10000]:  # S() only returns 10 results if you don't ask for more
                if p.primary_category:
                    try:
                        section = SectionPage.objects.get(
                            uuid=p.primary_category)
                        page = get_or_create(ArticlePage, p, section)
                    except SectionPage.DoesNotExist:
                        print "couldn't find", p.primary_category, SectionPage.objects.all().values('uuid')
                else:
                    # special case for articles with no primary category
                    # this assumption is probably wrong..but we have no where
                    # else to put them
                    page = get_or_create(FooterPage, p, main)

                page.subtitle = p.subtitle
                page.body = json.dumps([
                    {'type': 'paragraph', 'value': p.description},
                    {'type': 'paragraph', 'value': p.content}
                ])
                page.featured_in_latest = p.featured
                page.featured_in_homepage = p.featured_in_category
                # TODO: tags (see mk_tags)
                # TODO: related pages
                # TODO: image
                # TODO
                page.save_revision().publish()
        else:
            # TODO: import translations
            pass
    return Response()
