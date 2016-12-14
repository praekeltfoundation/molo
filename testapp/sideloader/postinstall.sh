cd "${INSTALLDIR}/${NAME}/testapp/"
manage="${VENV}/bin/python ${INSTALLDIR}/${NAME}/testapp/manage.py"

$manage migrate --settings=testapp.settings.production

# process static files
$manage compress --settings=testapp.settings.production
$manage collectstatic --noinput --settings=testapp.settings.production

# compile i18n strings
$manage compilemessages --settings=testapp.settings.production
