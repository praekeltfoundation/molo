cd "${INSTALLDIR}/${NAME}/mobi-application/"
manage="${VENV}/bin/python ${INSTALLDIR}/${NAME}/mobi-application/manage.py"

$manage migrate --settings=mobi-application.settings.production

# process static files
$manage compress --settings=mobi-application.settings.production
$manage collectstatic --noinput --settings=mobi-application.settings.production

# compile i18n strings
$manage compilemessages --settings=mobi-application.settings.production
