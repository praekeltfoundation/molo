cd "${INSTALLDIR}/${NAME}/{{cookiecutter.app_name}}/"
manage="${VENV}/bin/python ${INSTALLDIR}/${NAME}/{{cookiecutter.app_name}}/manage.py"

$manage migrate --settings={{cookiecutter.app_name}}.settings.production

# process static files
$manage compress --settings={{cookiecutter.app_name}}.settings.production
$manage collectstatic --noinput --settings={{cookiecutter.app_name}}.settings.production

# compile i18n strings
$manage compilemessages --settings={{cookiecutter.app_name}}.settings.production
