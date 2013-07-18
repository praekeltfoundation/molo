from fabric.api import cd, sudo, env
import os

expected_vars = [
    'PROJECT',
]

for var in expected_vars:
    if var not in os.environ:
        raise Exception('Please specify %s environment variable' % (
            var,))

PROJECT = os.environ['PROJECT']
USER = os.environ.get('USER', 'jmbo')

env.path = os.path.join('var', 'praekelt', PROJECT)


def restart():
    sudo('/etc/init.d/nginx restart')
    sudo('supervisorctl reload')


def deploy():
    with cd(env.path):
        sudo('git pull', user=USER)
        sudo('ve/bin/python manage.py syncdb --migrate --noinput',
             user=USER)
        sudo('ve/bin/python manage.py collectstatic --noinput',
             user=USER)


def install_packages(force=False):
    with cd(env.path):
        sudo('ve/bin/pip install %s -r requirements.pip' % (
             '--upgrade' if force else '',), user=USER)
