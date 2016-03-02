from django.conf.urls import url
from django.core import urlresolvers
from django.utils.translation import ugettext_lazy as _

from wagtail.wagtailcore import hooks
from wagtail.wagtailadmin.menu import MenuItem

from . import views


@hooks.register('register_admin_urls')
def register_admin_urls():
    return [
        url(r'^import-ucd/$',
            views.import_from_ucd,
            name='import-from-ucd'),
    ]


@hooks.register('register_admin_menu_item')
def register_import_menu_item():
    return MenuItem(
        _('Import content'),
        urlresolvers.reverse('import-from-ucd'),
        classnames='icon icon-download',
    )
