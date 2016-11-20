"""
Views for importing content from another wagtail instance
"""
from django.views.generic import FormView, View
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import render

from wagtailmodeladmin.views import CreateView, ChooseParentView

from molo.core.content_import.api import forms
from molo.core.content_import.api import importers

from molo.core.models import ArticlePage
from wagtailmodeladmin.options import ModelAdmin as WagtailModelAdmin
from wagtailmodeladmin.helpers import PagePermissionHelper


class ArticleImportView(FormView):
    """
    Test view to see if the importing of a single article can work
    """
    form_class = forms.ArticleImportForm
    success_url = reverse_lazy("molo_api:article-import")
    template_name = "core/api/article_import.html"

    importer = importers.ArticlePageImporter()

    def get_form_kwargs(self):
        # pass valid importer to the form
        kwargs = super(ArticleImportView, self).get_form_kwargs()
        kwargs["importer"] = self.importer
        return kwargs

    def form_valid(self, form):
        self.importer = form.save()
        if self.importer.articles():
            context = self.get_context_data()
            context["form"] = forms.ArticleImportForm(importer=self.importer)
            return self.render_to_response(context=context)
        return super(ArticleImportView, self).form_valid()


class ArticleModelAdmin(WagtailModelAdmin):
    model = ArticlePage


class ArticleChooserView(ChooseParentView):

    def post(self, request):
        import pdb;pdb.set_trace()
        form = self.get_form(request)
        if form.is_valid():
            parent = form.cleaned_data['parent_page']
