manage="${VENV}/bin/python ${INSTALLDIR}/${NAME}/manage.py"

$manage syncdb --noinput --migrate
$manage collectstatic --noinput
