from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from .forms import MediaForm

from django.conf import settings
import shutil
import os
import zipfile
import StringIO


def handle_uploaded_file(file):
    '''Replace the Current Media Folder.'''
    media_parent_directory = os.path.dirname(settings.MEDIA_ROOT)
    zip_file_reference = os.path.join(media_parent_directory, 'new_media.zip')

    if os.path.isdir(settings.MEDIA_ROOT):
        shutil.rmtree(settings.MEDIA_ROOT)

    with open(zip_file_reference, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)

    with zipfile.ZipFile(zip_file_reference, 'r') as z:
        z.extractall(media_parent_directory)

    os.remove(zip_file_reference)


def upload_file(request):
    '''Upload a Zip File Containing a single file containing media.'''
    if request.method == 'POST':
        print("Confirmed: post")
        form = MediaForm(request.POST, request.FILES)
        print("Confirmed: form object created")
        if form.is_valid():
            print("form is valid")
            handle_uploaded_file(request.FILES['zip_file'])
            return HttpResponseRedirect('/django-admin/')
    else:
        form = MediaForm()
    return render(request, 'admin/upload_media.html', {'form': form})


def download_file(request):
    '''Create and download a zip file containing the media file.'''
    if request.method == "GET":
        zipfile_name = 'media_%s.zip' % settings.SITE_NAME
        in_memory_file = StringIO.StringIO()

        media_zipfile = zipfile.ZipFile(in_memory_file, 'w',
                                        zipfile.ZIP_DEFLATED)

        directory_name = os.path.split(settings.MEDIA_ROOT)[-1]
        for root, dirs, files in os.walk(directory_name):
            for file in files:
                media_zipfile.write(os.path.join(root, file))

        media_zipfile.close()

        resp = HttpResponse(in_memory_file.getvalue(),
                            content_type="application/x-zip-compressed")
        resp['Content-Disposition'] = 'attachment; filename=%s' % zipfile_name

        return resp
