from django.apps import AppConfig
from django.db.utils import OperationalError, ProgrammingError
from django.conf import settings
from django.utils.timezone import activate

import logging


class MoloAppConfig(AppConfig):
    name = 'molo.core'

    def ready(self):
        from molo.core.models import Site, CmsSettings

        logging.basicConfig()
        logger = logging.getLogger(__name__)

        try:
            site = Site.objects.first()
            timezone = CmsSettings.for_site(site).timezone

            if timezone is None:
                timezone_name = settings.TIME_ZONE
                logger.warning(
                    'Timezone unset, defaulting to {0}'.format(timezone_name))
            else:
                timezone_name = timezone.title

        except (OperationalError, ProgrammingError) as e:
            timezone_name = settings.TIME_ZONE
            logger.warning('Database error: {0}'.format(e))
            logger.warning('Defaulting to timezone: {0}'.format(timezone_name))

        activate(timezone_name)
