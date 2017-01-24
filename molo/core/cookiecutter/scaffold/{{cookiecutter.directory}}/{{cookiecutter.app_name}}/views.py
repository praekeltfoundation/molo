import os
import zipfile
import StringIO

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.conf import settings
from django.contrib.auth.decorators import user_passes_test

from testapp.forms import MediaForm
from testapp.utils import replace_media_file


@user_passes_test(lambda u: u.is_superuser)
def upload_file(request):
    '''Upload a Zip File Containing a single file containing media.'''
    if request.method == 'POST':
        form = MediaForm(request.POST, request.FILES)
        if form.is_valid():
            replace_media_file(request.FILES['zip_file'])
            return HttpResponseRedirect('/django-admin/')
    else:
        form = MediaForm()
    return render(request, 'admin/upload_media.html', {'form': form})


@user_passes_test(lambda u: u.is_superuser)
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
