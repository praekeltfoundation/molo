"""
Views for importing content from another wagtail instance
"""
from django.http import HttpResponseRedirect, QueryDict
from django.views.generic import FormView, View
from django.core.urlresolvers import reverse, reverse_lazy
from django.shortcuts import render

from wagtailmodeladmin.views import CreateView, ChooseParentView

from molo.core.content_import.api import forms
from molo.core.content_import.api import importers

from molo.core.models import ArticlePage
from wagtailmodeladmin.options import ModelAdmin as WagtailModelAdmin
from wagtailmodeladmin.helpers import PagePermissionHelper


class MainImportView(FormView):
    form_class = forms.MainImportForm
    template_name = "core/api/main_import_page.html"
    success_url = reverse_lazy("molo_api:article-parent-chooser")

    def form_valid(self, form):
        content_type = form.cleaned_data["content_type"]

        # set the needed variables to the session for later retrieval
        self.request.session["url"] = form.cleaned_data["url"]
        self.request.session["content_type"] = content_type
        return super(MainImportView, self).form_valid(form)


class ArticleModelAdmin(WagtailModelAdmin):
    """ This is needed to instantiate the ArticleChooserView. """
    model = ArticlePage


class ArticleChooserView(ChooseParentView):

    def post(self, request):
        form = self.get_form(request)
        if form.is_valid():
            parent = form.cleaned_data["parent_page"]
            self.request.session["parent_page_id"] = parent.pk

            if "url" not in self.request.session:
                return HttpResponseRedirect(reverse("molo_api:main-import"))
            return HttpResponseRedirect(reverse("molo_api:article-import"))


class ArticleImportView(FormView):
    """
    View that will actually take care of article imports
    """
    form_class = forms.ArticleImportForm
    success_url = reverse_lazy("molo_api:article-import")
    template_name = "core/api/article_import.html"

    importer = importers.ArticlePageImporter()

    def get_form_kwargs(self):
        # pass valid importer to the form
        kwargs = super(ArticleImportView, self).get_form_kwargs()
        print "========= parent page ============="
        print self.request.session["parent_page_id"]

        if "url" in self.request.session:
            url = self.request.session["url"]
            self.importer.get_content_from_url(url + "/api/v1/pages/")
            kwargs["importer"] = self.importer

        if "parent_page_id" in self.request.session:
            kwargs["parent"] = self.request.session["parent_page_id"]
            print "========== kwargs in view ==============="
            print kwargs
        return kwargs

    def form_valid(self, form):
        self.importer = form.save()
        return super(ArticleImportView, self).form_valid(form)


