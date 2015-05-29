manage="${VENV}/bin/python ${INSTALLDIR}/${NAME}/manage.py"

$manage syncdb --noinput --no-initial-data --migrate
$manage collectstatic --noinput
