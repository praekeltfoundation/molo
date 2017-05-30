import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.rst')) as f:
    readme = f.read()

with open(os.path.join(here, 'requirements-dev.txt')) as f:
    requires_dev = f.readlines()

with open(os.path.join(here, 'VERSION')) as f:
    version = f.read().strip()

install_requires = [
    'Django>=1.9,<1.10',
    'cookiecutter==1.0.0',
    'raven==5.0.0',
    'markdown',
    'django-libsass',
    'dj-database-url',
    'django-cas-ng==3.5.4',
    'django-mptt==0.8.5',
    'requests',
    'elastic-git',
    'unicore.content',
    'wagtail==1.9',
    'babel',
    'wagtailmedia==0.1.3',
    'django-extensions',
    'celery<4.0',
    'redis',
    'six>=1.9',
    'django-google-analytics-app==2.1.4',
    'mote-prk==0.2.1',
    'beautifulsoup4',
    'ujson==1.35',
    'djangorestframework==3.3.2',
    'cached-property',
    'setuptools>=18.5',
    'molo.profiles<6.0.0,>=5.0.0',
    'django-el-pagination==3.1.0',
]

setup(name='molo.core',
      version=version,
      description=('Molo is a set of tools for publishing mobi sites with a '
                   'community focus.'),
      long_description=readme,
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
      tests_require=requires_dev,
      entry_points={
          'console_scripts': ['molo = molo.core.scripts.cli:main'],
      })
