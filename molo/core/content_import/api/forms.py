from django import forms


# TODO: make the form return the valid JSON response
class MainImportForm(forms.Form):
    url = forms.CharField(
        max_length=100,
    )

    def __init__(self, **kwargs):
        self.importer = kwargs.pop("importer")
        super(MainImportForm, self).__init__(**kwargs)


class ArticleImportForm(forms.Form):
    url = forms.CharField(
        max_length=100,
        required=False
    )

    def __init__(self, *args, **kwargs):
        # generate fields dynamically for each article found in the response
        self.importer = kwargs.pop("importer")
        super(ArticleImportForm, self).__init__(*args, **kwargs)
        if self.importer and self.importer.articles():
            for i, article in enumerate(self.importer.articles()):
                self.fields["%s" %i] = forms.BooleanField(
                    label=article["title"]
                )
                self.fields["%s" % i].required = False

    def save(self):
        if not self.importer.articles():
            self.importer.get_content_from_url("http://localhost:8000/api/v1/pages/")
        else:
            # there is content, and some fields could have been selected,
            # get the IDs of the articles so they can be saved
            selected_choices = [int(k) for k,v in self.cleaned_data.items() if v]

            # save articles
            # for id in selected_choices:
            #     article = self.importer.save_articles(selected_choices)
        return self.importer
