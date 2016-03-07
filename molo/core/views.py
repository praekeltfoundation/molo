from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils.translation import LANGUAGE_SESSION_KEY
import pkg_resources
import requests


def locale_set(request, locale):
    request.session[LANGUAGE_SESSION_KEY] = locale
    return redirect('/')


def health(request):
    return HttpResponse(status=200)


def versions(request):
    comparison_url = "https://github.com/praekelt/%s/compare/%s...%s"
    packages = [('molo.core', 'Molo'), ('molo.profiles', 'Profiles'),
                ('molo.commenting', 'Commenting'), ('molo.polls', 'Polls'),
                ('molo.yourwords', 'YourWords'), ('molo.servicedirectory',
                'Srvice Directory')]
    packages_info = []
    for package in packages:
        try:
            package_version = (
                pkg_resources.get_distribution(package[0])).version

            pypi_version = get_pypi_version(package[0])

            if package[0] == 'molo.core':
                compare_versions_link = comparison_url % (
                    'molo', package_version, pypi_version)
            else:
                compare_versions_link = comparison_url % (
                    package[0], package_version, pypi_version)

            packages_info.append((package[1], pypi_version,
                                  package_version, compare_versions_link))
        except:
            pypi_version = get_pypi_version(package[0])
            packages_info.append((package[1], pypi_version, "-",
                                 ""))

    return render(request, 'admin/versions.html', {
        'packages_info': packages_info,
    })


def get_pypi_version(package_name):
    url = "https://pypi.python.org/pypi/%s/json"
    content = requests.get(url % package_name).json()
    return content.get('info').get('version')
