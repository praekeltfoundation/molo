"""
Views for importing content from another wagtail instance
"""
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponseRedirect
from django.views.generic import FormView

from wagtailmodeladmin.options import ModelAdmin as WagtailModelAdmin
from wagtailmodeladmin.views import ChooseParentView

from molo.core.content_import.api import forms, importers
from molo.core.models import ArticlePage


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
    """
    Select the parent page for the ArticlePage objects will be imported
    """

    def get(self, request, *args, **kwargs):
        # The URL being imported from needs to be stored in the session
        # before this view is accessed. Redirect to the MainImportView
        # if it has not been set yet.
        if "url" not in self.request.session:
            return HttpResponseRedirect(reverse("molo_api:main-import"))
        return super(ArticleChooserView, self).get(request, *args, **kwargs)

    def post(self, request):
        # save the ID of the parent page in the session
        form = self.get_form(request)
        if form.is_valid():
            parent = form.cleaned_data["parent_page"]
            self.request.session["parent_page_id"] = parent.pk
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


