import requests
from rest_framework.decorators import (
    api_view, authentication_classes, permission_classes)
from rest_framework.response import Response
from unicore.content.models import Localisation, Category, Page
from molo.core.models import SiteLanguage, SectionPage, ArticlePage
from elasticgit.workspace import RemoteWorkspace
from rest_framework.authentication import (
    SessionAuthentication, BasicAuthentication)
from rest_framework.permissions import IsAuthenticated
from molo.core.models import Main


@api_view(['GET'])
def get_repos(request):
    response = requests.get('http://localhost:6543/repos.json').json()
    return Response({
        'repos': [repo.get('name') for repo in response]})


@api_view(['GET'])
def get_content_for_repo(request, name):
    ws = RemoteWorkspace('http://localhost:6543/repos/%s.json' % name)
    ws.sync(Localisation)
    ws.sync(Category)
    ws.sync(Page)

    return Response({
        'locales': [{l.locale for l in ws.S(Localisation).all()}],
        'categories': [c.title for c in ws.S(Category).all()],
        'pages': [p.title for p in ws.S(Page).all()],
    })


@api_view(['POST'])
@authentication_classes((SessionAuthentication, BasicAuthentication))
@permission_classes((IsAuthenticated,))
def import_content(request, name):
    ws = RemoteWorkspace('http://localhost:6543/repos/%s.json' % name)
    ws.sync(Localisation)
    ws.sync(Category)
    ws.sync(Page)

    # create wagtail content

    locales = request.data.get('locales')
    for selected_locale in locales:
        for l in ws.S(Localisation).filter(
                locale=selected_locale.get('locale')):
            print l
        print SiteLanguage.objects.get(
            locale=selected_locale.get('site_language'))
        site_language = SiteLanguage.objects.get(
            locale=selected_locale.get('site_language'))
        if site_language.is_main_language:
            main = Main.objects.all().first()
            for c in ws.S(Category).filter(
                    locale=selected_locale.get('locale')):
                if SectionPage.objects.filter(uuid=c.uuid).exists():
                    section = SectionPage.objects.get(uuid=c.uuid)
                    section.title = c.title
                    section.save_revision().publish()
                else:
                    section = SectionPage(uuid=c.uuid, title=c.title)
                    main.add_child(instance=section)
                    section.save_revision().publish()

            for p in ws.S(Page).filter(locale=selected_locale.get('locale')):
                section = SectionPage.objects.get(uuid=p.uuid)
                page = ArticlePage(
                    uuid=p.uuid, title=p.title, subtitle=p.description
                )
                section.add_child(instane=page)
                page.save_revision().publish()
    return Response()
