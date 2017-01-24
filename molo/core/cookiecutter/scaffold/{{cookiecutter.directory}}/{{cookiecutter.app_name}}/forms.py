from django import forms


class MediaForm(forms.Form):
    zip_file = forms.FileField(label="Zipped Media File")

    def clean_data_file(self):
        file = self.cleaned_data['data_file']

        if file:
            extension = file.name.split('.')[-1]
            if extension != 'zip':
                raise forms.ValidationError('File Type Is Not .zip')
        return file
    '''

    def process_data(self):
        print("I am processing the form")
        file = self.cleaned_data['data_file'].file

        # delete root media file
        # unzip file in root folder (make sure it's called 'media')
    '''
