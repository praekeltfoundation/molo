from os import environ, path, walk
import pkg_resources
import requests
import zipfile
import StringIO

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.urlresolvers import reverse
from django.http import JsonResponse, HttpResponse, Http404
from django.shortcuts import redirect, get_object_or_404, render
from django.utils.translation import (
    LANGUAGE_SESSION_KEY,
    get_language_from_request
)
from django.utils.translation import ugettext as _
from wagtail.wagtailcore.models import Page
from wagtail.wagtailsearch.models import Query

from molo.core.utils import generate_slug, get_locale_code, update_media_file
from molo.core.models import PageTranslation, ArticlePage, Languages
from molo.core.known_plugins import known_plugins
from molo.core.forms import MediaForm
from django.views.generic import ListView


def csrf_failure(request, reason=""):
    freebasics_url = settings.FREE_BASICS_URL_FOR_CSRF_MESSAGE
    return render(request, '403_csrf.html', {'freebasics_url': freebasics_url})


def search(request, results_per_page=10):
    search_query = request.GET.get('q', None)
    page = request.GET.get('p', 1)
    locale = get_locale_code(get_language_from_request(request))

    if search_query:
        main = request.site.root_page

        results = ArticlePage.objects.descendant_of(main).filter(
            languages__language__locale=locale
        ).values_list('pk', flat=True)

        # Elasticsearch backend doesn't support filtering
        # on related fields, at the moment.
        # So we need to filter ArticlePage entries using DB,
        # then, we will be able to search
        results = ArticlePage.objects.filter(pk__in=results)
        results = results.live().search(search_query)

        # At the moment only ES backends have highlight API.
        if hasattr(results, 'highlight'):
            results = results.highlight(
                fields={
                    'title': {},
                    'subtitle': {},
                    'body': {},
                },
                require_field_match=False
            )

        Query.get(search_query).add_hit()
    else:
        results = ArticlePage.objects.none()

    paginator = Paginator(results, results_per_page)
    try:
        search_results = paginator.page(page)
    except PageNotAnInteger:
        search_results = paginator.page(1)
    except EmptyPage:
        search_results = paginator.page(paginator.num_pages)

    return render(request, 'search/search_results.html', {
        'search_query': search_query,
        'search_results': search_results,
        'results': results,
    })


def locale_set(request, locale):
    request.session[LANGUAGE_SESSION_KEY] = locale
    return redirect(request.GET.get('next', '/'))


def health(request):
    app_id = environ.get('MARATHON_APP_ID', None)
    ver = environ.get('MARATHON_APP_VERSION', None)
    return JsonResponse({'id': app_id, 'version': ver})


def add_translation(request, page_id, locale):
    _page = get_object_or_404(Page, id=page_id)
    page = _page.specific
    if not hasattr(page, 'get_translation_for'):
        messages.add_message(
            request, messages.INFO, _('That page is not translatable.'))
        return redirect(reverse('wagtailadmin_home'))

    # redirect to edit page if translation already exists for this locale
    translated_page = page.get_translation_for(
        locale, request.site, is_live=None)
    if translated_page:
        return redirect(
            reverse('wagtailadmin_pages:edit', args=[translated_page.id]))

    # create translation and redirect to edit page
    language = Languages.for_site(request.site).languages.filter(
        locale=locale).first()
    if not language:
        raise Http404
    new_title = str(language) + " translation of %s" % page.title
    new_slug = generate_slug(new_title)
    translation = page.__class__(
        title=new_title, slug=new_slug)
    page.get_parent().add_child(instance=translation)
    translation.save_revision()
    language_relation = translation.languages.first()
    language_relation.language = language
    language_relation.save()
    translation.save_revision()

    # make sure new translation is in draft mode
    translation.unpublish()
    PageTranslation.objects.get_or_create(
        page=page, translated_page=translation)
    return redirect(
        reverse('wagtailadmin_pages:edit', args=[translation.id]))


def import_from_git(request):
    return render(request, 'admin/import_from_git.html')


def versions(request):
    comparison_url = "https://github.com/praekelt/%s/compare/%s...%s"
    plugins_info = []
    for plugin in known_plugins():
        try:
            plugin_version = (
                pkg_resources.get_distribution(plugin[0])).version

            pypi_version = get_pypi_version(plugin[0])

            if plugin[0] == 'molo.core':
                compare_versions_link = comparison_url % (
                    'molo', plugin_version, pypi_version)
            else:
                compare_versions_link = comparison_url % (
                    plugin[0], plugin_version, pypi_version)

            plugins_info.append((plugin[1], pypi_version,
                                 plugin_version, compare_versions_link))
        except:
            pypi_version = get_pypi_version(plugin[0])
            plugins_info.append((plugin[1], pypi_version, "-",
                                 ""))

    return render(request, 'admin/versions.html', {
        'plugins_info': plugins_info,
    })


def get_pypi_version(plugin_name):
    url = "https://pypi.python.org/pypi/%s/json"
    content = requests.get(url % plugin_name).json()
    return content.get('info').get('version')


class TagsListView(ListView):
    template_name = "core/article_tags.html"

    def get_queryset(self, **kwargs):
        tag = self.kwargs["tag_name"]
        main = self.request.site.root_page
        return ArticlePage.objects.descendant_of(main).filter(
            tags__name__in=[tag])


@user_passes_test(lambda u: u.is_superuser)
def upload_file(request):
    '''Upload a Zip File Containing a single file containing media.'''
    if request.method == 'POST':
        form = MediaForm(request.POST, request.FILES)
        if form.is_valid():
            context_dict = {}
            try:
                context_dict['copied_files'] = update_media_file(
                    request.FILES['zip_file'])
            except Exception as e:
                context_dict['error_message'] = e.message
            return render(request,
                          'django_admin/transfer_media_message.html',
                          context_dict)
    else:
        form = MediaForm()
    return render(request, 'django_admin/upload_media.html', {'form': form})


@user_passes_test(lambda u: u.is_superuser)
def download_file(request):
    '''Create and download a zip file containing the media file.'''
    if request.method == "GET":
        if path.exists(settings.MEDIA_ROOT):
            zipfile_name = 'media_%s.zip' % settings.SITE_NAME
            in_memory_file = StringIO.StringIO()

            media_zipfile = zipfile.ZipFile(in_memory_file, 'w',
                                            zipfile.ZIP_DEFLATED)

            directory_name = path.split(settings.MEDIA_ROOT)[-1]
            for root, dirs, files in walk(directory_name):
                for file in files:
                    media_zipfile.write(path.join(root, file))

            media_zipfile.close()

            resp = HttpResponse(in_memory_file.getvalue(),
                                content_type="application/x-zip-compressed")
            resp['Content-Disposition'] = (
                'attachment; filename=%s' % zipfile_name)

            return resp
        else:
            return render(request,
                          'django_admin/transfer_media_message.html',
                          {'error_message':
                           'media file does not exist'})
