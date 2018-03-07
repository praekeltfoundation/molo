import codecs
import os
import sys
from setuptools import setup, find_packages

HERE = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    with codecs.open(os.path.join(HERE, *parts), 'rb', 'utf-8') as f:
        return f.read()


install_requires = [
    'babel',
    'beautifulsoup4',
    'cached-property',
    'celery<4.0',
    'cookiecutter==1.0.0',
    'dj-database-url',
    'Django>=1.11,<2.0',
    'django-cas-ng==3.5.8',
    'django-el-pagination==3.1.0',
    'django-extensions',
    'django-google-analytics-app==4.2.0',
    'django-libsass',
    'django-mptt==0.8.6',
    'djangorestframework==3.4.0',
    'django-phonenumber-field==1.3.0',
    'django-import-export',
    'django-daterange-filter',
    'elastic-git',
    'markdown',
    'mote-prk==0.2.1',
    'raven==5.0.0',
    'redis',
    'requests',
    'setuptools>=18.5',
    'six>=1.9',
    'ujson==1.35',
    'unicodecsv==0.14.1',
    'unicore.content',
    'wagtail>=1.13,<1.14',
    'wagtailmedia==0.1.3',
    'ImageHash==3.4',
    'boto==2.48.0',
    'django-storages==1.6.3',
    'Unidecode==0.04.16',
    'django-treebeard==4.2.0',
]

# we need to only install typing for python2
if sys.version_info < (3, 5):
    install_requires.append('typing')

setup(name='molo.core',
      version=read('VERSION'),
      description=('Molo is a set of tools for publishing mobi sites with a '
                   'community focus.'),
      long_description=read('README.rst'),
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Environment :: Web Environment',
          'Framework :: Django',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: BSD License',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.7',
          'Topic :: Internet :: WWW/HTTP',
          'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
      ],
      author='Praekelt.org',
      author_email='dev@praekelt.org',
      url='http://github.com/praekelt/molo',
      license='BSD',
      keywords='praekelt, mobi, web, django',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      namespace_packages=['molo'],
      install_requires=install_requires,
      entry_points={
          'console_scripts': ['molo = molo.core.scripts.cli:main'],
      })
