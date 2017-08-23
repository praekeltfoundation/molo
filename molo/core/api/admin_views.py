"""
Views for importing content from another wagtail instance
"""
from django.conf import settings
from django.shortcuts import render
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponseRedirect
from django.views.generic import View, FormView

from wagtail.contrib.modeladmin.options import ModelAdmin as WagtailModelAdmin
from wagtail.contrib.modeladmin.views import ChooseParentView

from molo.core.api import forms, importers
from molo.core.api.constants import ARTICLE_SESSION_VARS, SECTION_SESSION_VARS
from molo.core.models import ArticlePage, SectionPage
from molo.core.tasks import import_site


class SiteImportView(FormView):
    '''
    The first import view that takes a URL, begins a
    celery tak to import the site if the site is responsive
    and redirects user to a message that the site content
    is being fetched
    '''
    form_class = forms.SiteImportForm
    template_name = "core/api/site_import_page.html"
    success_url = reverse_lazy("molo_api:begun-import")

    def form_valid(self, form):
        url = form.cleaned_data["url"]
        site_pk = self.request.site.root_page.get_site().pk
        user_pk = self.request.user.pk

        # call the function synchronously if locally hosted
        if settings.DEBUG:
            import_site(url, site_pk, user_pk)
        else:
            import_site.delay(url, site_pk, user_pk)

        return super(SiteImportView, self).form_valid(form)


class MainImportView(FormView):
    form_class = forms.MainImportForm
    template_name = "core/api/main_import_page.html"
    success_url = reverse_lazy("molo_api:article-parent-chooser")

    def form_valid(self, form):
        content_type = form.cleaned_data["content_type"]

        # set the needed variables to the session for later retrieval
        self.request.session["url"] = form.cleaned_data["url"]
        if content_type == "core.ArticlePage":
            self.request.session["article_content_type"] = content_type
            return HttpResponseRedirect(
                reverse("molo_api:article-parent-chooser")
            )
        elif content_type == "core.SectionPage":
            self.request.session["section_content_type"] = content_type
            return HttpResponseRedirect(
                reverse("molo_api:section-parent-chooser")
            )


class ArticleModelAdmin(WagtailModelAdmin):
    """ This is needed to instantiate the ArticleChooserView. """
    model = ArticlePage


class ArticleChooserView(ChooseParentView):
    """
    Select the parent page for the ArticlePage objects will be imported
    """

    def get(self, request, *args, **kwargs):
        # The URL being imported from needs to be stored in the session
        # before this view is accessed. Redirect to the MainImportView
        # if it has not been set yet.
        if not all(
            key in self.request.session for key in ARTICLE_SESSION_VARS.first
        ):
            return HttpResponseRedirect(reverse("molo_api:main-import"))
        return super(ArticleChooserView, self).get(request, *args, **kwargs)

    def post(self, request):
        # save the ID of the parent page in the session
        form = self.get_form(request)
        if form.is_valid():
            parent = form.cleaned_data["parent_page"]
            self.request.session["article_parent_page_id"] = parent.pk
        return HttpResponseRedirect(reverse("molo_api:article-import"))


class ArticleImportView(FormView):
    """
    Fetches available articles and renders them in a list.
    The user can then select which articles to save
    """
    form_class = forms.ArticleImportForm
    success_url = reverse_lazy("molo_api:article-import")
    template_name = "core/api/article_import.html"

    importer = importers.ArticlePageImporter()

    def get(self, *args, **kwargs):
        if not all(
            key in self.request.session for key in ARTICLE_SESSION_VARS.first
        ):
            return HttpResponseRedirect(reverse("molo_api:main-import"))

        if ARTICLE_SESSION_VARS.second not in self.request.session:
            return HttpResponseRedirect(
                reverse("molo_api:article-parent-chooser")
            )

        return super(ArticleImportView, self).get(*args, **kwargs)

    def get_form_kwargs(self):
        # pass valid importer to the form
        kwargs = super(ArticleImportView, self).get_form_kwargs()
        url = self.request.session["url"]
        self.importer.get_content_from_url(url)
        kwargs["importer"] = self.importer
        kwargs["parent"] = self.request.session["article_parent_page_id"]
        return kwargs

    def form_valid(self, form):
        self.importer = form.save()
        return super(ArticleImportView, self).form_valid(form)


class SectionModelAdmin(WagtailModelAdmin):
    """ This is needed to instantiate the ArticleChooserView. """
    model = SectionPage


class SectionParentChooserView(ChooseParentView):
    """
    Select the parent page for the section
    """
    def get(self, request, *args, **kwargs):
        # The URL being imported from needs to be stored in the session
        # before this view is accessed. Redirect to the MainImportView
        # if it has not been set yet.
        if not all(
            key in self.request.session for key in SECTION_SESSION_VARS.first
        ):
            return HttpResponseRedirect(reverse("molo_api:main-import"))
        return super(SectionParentChooserView, self).get(
            request, *args, **kwargs)

    def post(self, request, *args):
        # save the ID of the parent page in the session
        form = self.get_form(request)
        if form.is_valid():
            parent = form.cleaned_data["parent_page"]
            self.request.session["section_parent_page_id"] = parent.pk
        return HttpResponseRedirect(reverse("molo_api:section-import"))


class SectionImportView(FormView):
    """
    Fetches available section and renders them in a list.
    The user can then select which section to save
    """
    form_class = forms.SectionImportForm
    success_url = reverse_lazy("molo_api:section-import")
    template_name = "core/api/section_import.html"

    importer = importers.SectionPageImporter()

    def get(self, *args, **kwargs):
        if not all(
            key in self.request.session for key in SECTION_SESSION_VARS.first
        ):
            return HttpResponseRedirect(reverse("molo_api:main-import"))

        if SECTION_SESSION_VARS.second not in self.request.session:
            return HttpResponseRedirect(
                reverse("molo_api:section-parent-chooser")
            )

        return super(SectionImportView, self).get(*args, **kwargs)

    def get_form_kwargs(self):
        # pass valid importer to the form
        kwargs = super(SectionImportView, self).get_form_kwargs()
        url = self.request.session["url"]
        self.importer.get_content_from_url(url)
        kwargs["importer"] = self.importer
        kwargs["parent"] = self.request.session["section_parent_page_id"]
        return kwargs

    def form_valid(self, form):
        self.importer = form.save()
        return super(SectionImportView, self).form_valid(form)


class ImportBegun(View):
    template_name = 'core/api/import_begun.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)
