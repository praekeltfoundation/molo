import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.rst')) as f:
    readme = f.read()

with open(os.path.join(here, 'requirements.txt')) as f:
    requires = filter(None, f.readlines())

with open(os.path.join(here, 'requirements-dev.txt')) as f:
    requires_dev = filter(None, f.readlines())

with open(os.path.join(here, 'VERSION')) as f:
    version = f.read().strip()

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
      install_requires=requires,
      tests_require=requires_dev,
      entry_points={
          'console_scripts': ['molo = molo.core.scripts.cli:main'],
      })
