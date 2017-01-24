import os
import shutil
import zipfile

from django.conf import settings


def replace_media_file(file):
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
