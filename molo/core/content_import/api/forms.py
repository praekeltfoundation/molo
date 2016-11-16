from django import forms


# TODO: make the form return the valid JSON response
class MainImportForm(forms.Form):
    url = forms.CharField(
        max_length=100,
    )

    def __init__(self, **kwargs):
        self.importer = kwargs.pop("importer")
        super(MainImportForm, self).__init__(**kwargs)

    def save(self):
        # return valid API response
        return self.importer.get_content_from_url("http://localhost:8000/api/v1/pages/")

