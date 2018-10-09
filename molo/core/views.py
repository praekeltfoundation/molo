from os import environ, path, walk
import pkg_resources
import requests
import zipfile

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.urlresolvers import reverse
from django.http import (
    JsonResponse,
    HttpResponse,
    HttpResponseNotAllowed,
    Http404,
)
from django.shortcuts import redirect, get_object_or_404, render
from django.utils.http import is_safe_url
from django.utils.translation import (
    LANGUAGE_SESSION_KEY,
    get_language_from_request
)
from django.utils.translation import ugettext as _
from django.views.generic.edit import FormView
from django.views.generic.base import TemplateView
from io import BytesIO
from wagtail.wagtailcore.models import Page, UserPagePermissionsProxy
from wagtail.wagtailsearch.models import Query
from molo.core.utils import generate_slug, get_locale_code, update_media_file
from molo.core.models import (
    ArticlePage, Languages, SiteSettings, Tag,
    ArticlePageTags, SectionPage, ReactionQuestionChoice,
    ReactionQuestionResponse, ReactionQuestion, TranslatablePageMixin)

from molo.core.templatetags.core_tags import get_pages
from molo.core.known_plugins import known_plugins
from molo.core.forms import MediaForm, ReactionQuestionChoiceForm
from molo.core.tasks import copy_to_all_task
from django.views.generic import ListView

from el_pagination.decorators import page_template


def csrf_failure(request, reason=""):
    freebasics_url = settings.FREE_BASICS_URL_FOR_CSRF_MESSAGE
    return render(request, '403_csrf.html', {'freebasics_url': freebasics_url})


def search(request, results_per_page=10, load_more=False):
    search_query = request.GET.get('q', None)
    page = request.GET.get('p', 1)
    locale = get_locale_code(get_language_from_request(request))

    if search_query:
        main = request.site.root_page

        results = ArticlePage.objects.descendant_of(main).filter(
            language__locale=locale
        ).exact_type(ArticlePage).values_list('pk', flat=True)

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
    if load_more:
        return results
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
    if not issubclass(type(page), TranslatablePageMixin):
        messages.add_message(
            request, messages.INFO, _('That page is not translatable.'))
        return redirect(reverse('wagtailadmin_home'))
    # redirect to edit page if translation already exists for this locale
    translated_page = page.translated_pages.filter(language__locale=locale)
    if translated_page.exists():
        return redirect(
            reverse('wagtailadmin_pages:edit', args=[
                translated_page.first().id]))

    # create translation and redirect to edit page
    language = Languages.for_site(request.site).languages.filter(
        locale=locale).first()
    if not language:
        raise Http404
    new_title = str(language) + " translation of %s" % page.title
    new_slug = generate_slug(new_title)
    translation = page.__class__(
        title=new_title, slug=new_slug, language=language)
    page.get_parent().add_child(instance=translation)
    translation.save_revision()
    # add the translation the new way
    page.specific.translated_pages.add(translation)
    page.save()
    translation.specific.translated_pages.add(page)
    translation.save()
    for translated_page in \
            page.specific.translated_pages.all():
        translations = page.specific.translated_pages.all().\
            exclude(language__pk=translated_page.language.pk)
        for translation in translations:
            translated_page.translated_pages.add(translation)
        translated_page.save()

    # make sure new translation is in draft mode
    translation.unpublish()
    return redirect(
        reverse('wagtailadmin_pages:edit', args=[translation.id]))


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

    return render(request, 'versions.html', {
        'plugins_info': plugins_info,
    })


def get_pypi_version(plugin_name):
    url = "https://pypi.python.org/pypi/%s/json"
    try:
        content = requests.get(url % plugin_name).json()
        return content.get('info').get('version')
    except:
        return 'request failed'


class ReactionQuestionChoiceFeedbackView(TemplateView):
    template_name = 'patterns/basics/articles/reaction_question_feedback.html'

    def get_context_data(self, **kwargs):
        context = super(ReactionQuestionChoiceFeedbackView,
                        self).get_context_data(**kwargs)
        locale = self.request.LANGUAGE_CODE
        choice_slug = self.kwargs.get('choice_slug')
        context['request'] = self.request
        main_lang_choice = ReactionQuestionChoice.objects.descendant_of(
            self.request.site.root_page).filter(
            slug=choice_slug)
        choice = get_pages(context, main_lang_choice, locale)
        if choice:
            choice = choice[0]
        else:
            choice = main_lang_choice
        context.update({'choice': choice})
        article_slug = self.kwargs.get('article_slug')
        article = ArticlePage.objects.descendant_of(
            self.request.site.root_page).filter(slug=article_slug).first()
        context.update({'article': article})
        return context


class ReactionQuestionChoiceView(FormView):
    form_class = ReactionQuestionChoiceForm
    template_name = 'patterns/basics/articles/reaction_question.html'
    success_url = '/'

    def get_success_url(self, *args, **kwargs):
        article_slug = self.kwargs.get('article_slug')
        article = ArticlePage.objects.descendant_of(
            self.request.site.root_page).filter(slug=article_slug).first()
        if not article:
            raise Http404
        choice_id = self.get_context_data()['form'].data.get('choice')
        choice = get_object_or_404(ReactionQuestionChoice, pk=choice_id)
        question_id = self.kwargs.get('question_id')
        return reverse('reaction-feedback', kwargs={
            'question_id': question_id, 'article_slug': article.slug,
            'choice_slug': choice.slug})

    def get_context_data(self, *args, **kwargs):
        context = super(
            ReactionQuestionChoiceView, self).get_context_data(*args, **kwargs)
        question_id = self.kwargs.get('question_id')
        question = get_object_or_404(ReactionQuestion, pk=question_id)
        context.update({'question': question})
        return context

    def form_valid(self, form, *args, **kwargs):
        question_id = self.kwargs.get('question_id')
        question = get_object_or_404(ReactionQuestion, pk=question_id)
        question = question.get_main_language_page().specific
        choice_pk = form.cleaned_data['choice']
        choice = get_object_or_404(ReactionQuestionChoice, pk=choice_pk)
        article_slug = self.kwargs.get('article_slug')
        # get main language article and store the vote there
        article = ArticlePage.objects.descendant_of(
            self.request.site.root_page).filter(slug=article_slug).first()
        if hasattr(article, 'get_main_language_page'):
            article = article.get_main_language_page()
        if not article:
            raise Http404
        if not question.has_user_submitted_reaction_response(
                self.request, question_id, article.pk):
            created = ReactionQuestionResponse.objects.create(
                question=question,
                article=article)
            if created:
                created.choice = choice
                created.save()
                created.set_response_as_submitted_for_session(
                    self.request, article)
            if self.request.user.is_authenticated():
                created.user = self.request.user
                created.save()

        else:
            messages.error(
                self.request,
                "You have already given feedback on this article.")
        return super(ReactionQuestionChoiceView, self).form_valid(
            form, *args, **kwargs)


class TagsListView(ListView):
    template_name = "core/article_tags.html"

    def get_queryset(self, *args, **kwargs):
        site_settings = SiteSettings.for_site(self.request.site)
        main = self.request.site.root_page
        tag = self.kwargs["tag_name"]
        if site_settings.enable_tag_navigation:
            count = self.request.GET.get("count")
            context = {'request': self.request}
            locale = self.request.LANGUAGE_CODE

            tag = Tag.objects.filter(slug=tag).descendant_of(main)
            if tag.exists():
                tag = tag.first()
                articles = []
                for article_tag in ArticlePageTags.objects.filter(
                        tag=tag.get_main_language_page()).all():
                    articles.append(article_tag.page.pk)
                articles = ArticlePage.objects.filter(
                    pk__in=articles).descendant_of(main).order_by(
                        '-first_published_at')
                return get_pages(context, articles[:count], locale)
            raise Http404
        return ArticlePage.objects.descendant_of(main).filter(
            tags__name__in=[tag]).order_by(
                '-first_published_at')

    def get_context_data(self, *args, **kwargs):
        context = super(TagsListView, self).get_context_data(*args, **kwargs)
        tag = self.kwargs['tag_name']
        context.update({'tag': Tag.objects.filter(
            slug=tag).descendant_of(self.request.site.root_page).first()})
        return context


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
            in_memory_file = BytesIO()

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

        else:
            resp = render(request,
                          'django_admin/transfer_media_message.html',
                          {'error_message':
                           'media file does not exist'})
    else:
        resp = HttpResponseNotAllowed(permitted_methods=['GET'])

    return resp


@page_template(
    'patterns/basics/article-teasers/latest-promoted_variations/'
    'latest-articles_for-paging.html')
def home_index(
        request,
        extra_context=None,
        template=(
            'patterns/components/article-teasers/latest-promoted_variations/'
            'article_for_paging.html')):
    locale_code = request.GET.get('locale')
    return render(request, template, {'locale_code': locale_code})


@page_template(
    'patterns/basics/sections/sectionpage-article-list-'
    'standard_for-paging.html')
def section_index(
        request,
        extra_context=None,
        template=(
            'patterns/basics/sections/sectionpage-article-list-'
            'standard_for-paging.html')):
    section = SectionPage.objects.get(pk=request.GET.get('section'))
    locale_code = request.GET.get('locale')
    return render(
        request, template, {'section': section, 'locale_code': locale_code})


@page_template('core/article_tags_for_paging.html')
def tag_index(request, extra_context=None,
              template=('core/article_tags_for_paging.html')):
    tag_name = request.GET.get("tag_name")
    if not tag_name:
        raise Http404

    main = request.site.root_page
    tag = Tag.objects.filter(slug=tag_name).descendant_of(main)

    if tag.exists():
        tag = tag.first()
        context = {'request': request}
        locale = request.LANGUAGE_CODE
        articles = []
        for article_tag in ArticlePageTags.objects.filter(
                tag=tag.get_main_language_page()).all():
            articles.append(article_tag.page.pk)
        articles = ArticlePage.objects.filter(
            pk__in=articles).descendant_of(main).order_by(
                'latest_revision_created_at')
        # count = articles.count() if articles.count() < count else count
        # context = self.get_context_data(
        #     object_list=get_pages(context, articles[:count], locale))
        object_list = get_pages(context, articles, locale)
        locale_code = request.GET.get('locale')
        return render(request, template, {
            'object_list': object_list, 'tag': tag,
            'locale_code': locale_code})
    raise Http404


@page_template('search/search_results_for_paging.html')
def search_index(
        request,
        extra_context=None,
        template=('search/search_results_for_paging.html')):
    search_query = request.GET.get('q')
    results = search(request, load_more=True)
    locale_code = request.GET.get('locale')
    return render(
        request, template, {
            'search_query': search_query, 'results': results,
            'locale_code': locale_code})


@page_template(
    'patterns/basics/article-teasers/latest-promoted_variations/late'
    'st-articles_for-feature.html')
def home_more(
        request, template='core/main-feature-more.html', extra_context=None):
    locale_code = request.GET.get('locale')
    return render(request, template, {'locale_code': locale_code})


def get_valid_next_url_from_request(request):
    next_url = request.POST.get('next') or request.GET.get('next')
    if not next_url or not is_safe_url(url=next_url, host=request.get_host()):
        return ''
    return next_url


def copy_to_all_confirm(request, page_id):
    page = get_object_or_404(Page, id=page_id).specific
    next_url = get_valid_next_url_from_request(request)
    if request.method == 'POST':
        if next_url:
            return redirect(next_url)
        return redirect('wagtailadmin_explore', page.get_parent().id)

    return render(request, 'wagtailadmin/pages/confirm_copy_to_all.html', {
        'page': page,
        'next': next_url,
        'not_live_descendant_count': page.get_descendants().not_live().count()
    })


def copy_to_all(request, page_id):
    page = get_object_or_404(Page, id=page_id).specific
    copy_to_all_task.delay(page.pk, request.user.pk, request.site.pk)
    next_url = get_valid_next_url_from_request(request)
    if next_url:
        return redirect(next_url)
    return redirect('wagtailadmin_explore', page.get_parent().id)


def publish(request, page_id):
    page = get_object_or_404(Page, id=page_id).specific

    user_perms = UserPagePermissionsProxy(request.user)
    if not user_perms.for_page(page).can_publish():
        raise PermissionDenied

    next_url = get_valid_next_url_from_request(request)

    if request.method == 'POST':
        include_descendants = request.POST.get("include_descendants", False)

        page.save_revision().publish()

        if include_descendants:
            not_live_descendant_pages = (
                page.get_descendants().not_live().specific())
            for not_live_descendant_page in not_live_descendant_pages:
                if user_perms.for_page(not_live_descendant_page).can_publish():
                    not_live_descendant_page.save_revision().publish()

        if next_url:
            return redirect(next_url)
        return redirect('wagtailadmin_explore', page.get_parent().id)

    return render(request, 'wagtailadmin/pages/confirm_publish.html', {
        'page': page,
        'next': next_url,
        'not_live_descendant_count': page.get_descendants().not_live().count()
    })
