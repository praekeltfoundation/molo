cd "${INSTALLDIR}/${NAME}/{{cookiecutter.app_name}}/"
manage="${VENV}/bin/python ${INSTALLDIR}/${NAME}/{{cookiecutter.app_name}}/manage.py"

$manage migrate
$manage collectstatic --noinput
