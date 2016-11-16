"""
Views for importing content from another wagtail instance
"""
from django.views.generic import FormView
from django.core.urlresolvers import reverse_lazy

from wagtailmodeladmin.views import CreateView

from molo.core.content_import.api import forms
from molo.core.content_import.api import importers

from molo.core.models import ArticlePage
from wagtailmodeladmin.options import ModelAdmin as WagtailModelAdmin


class ImportView(FormView):
    """
    Test view to see if the importing of a single article can work
    """
    form_class = forms.MainImportForm
    success_url = reverse_lazy("molo_api:test-api-import-view")
    template_name = "core/api/import.html"

    # def get_context_data(self, **kwargs):
    #     pass

    def get_form_kwargs(self):
        # pass valid importer to the form
        kwargs = super(ImportView, self).get_form_kwargs()
        kwargs["importer"] = importers.ArticlePageImporter()
        return kwargs

    def form_valid(self, form):
        data = form.save()
        if data:
            context = self.get_context_data()
            context["data"] = data
            return self.render_to_response(context=context)
        return super(ImportView, self).form_valid()
