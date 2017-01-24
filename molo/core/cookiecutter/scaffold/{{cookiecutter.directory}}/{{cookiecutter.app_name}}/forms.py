from django import forms


class MediaForm(forms.Form):
    zip_file = forms.FileField(label="Zipped Media File")

    def clean_zip_file(self):
        file = self.cleaned_data['zip_file']

        if file:
            extension = file.name.split('.')[-1]
            if extension != 'zip':
                raise forms.ValidationError('File Type Is Not .zip')
        return file
