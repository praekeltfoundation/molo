cd "${INSTALLDIR}/${NAME}/mobiApp/"
manage="${VENV}/bin/python ${INSTALLDIR}/${NAME}/mobiApp/manage.py"

$manage migrate --settings=mobiApp.settings.production

# process static files
$manage compress --settings=mobiApp.settings.production
$manage collectstatic --noinput --settings=mobiApp.settings.production

# compile i18n strings
$manage compilemessages --settings=mobiApp.settings.production
