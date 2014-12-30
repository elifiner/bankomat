from fabric.api import *
from fabric.contrib.files import exists
from fabric.contrib.project import rsync_project

env.hosts = ['dev.elifiner.com']

# application settings
app_user = 'eli'
app_name = 'bankomat'
app_dir = '/home/%s/%s' % (app_user, app_name)

local_supervisor_conf = './etc/supervisor.conf'
system_supervisor_conf = '/etc/supervisor/conf.d/%s.conf' % app_name
local_nginx_conf = './etc/nginx.conf'
system_nginx_conf = '/etc/nginx/sites-enabled/%s' % app_name

# fabric settings
env.use_ssh_config = True

def _install_requirements():
    with hide('stdout'):
        sudo('apt-get install -y python')
        sudo('apt-get install -y python-pip')
        sudo('apt-get install -y python-virtualenv')
        sudo('apt-get install -y nginx')
        sudo('apt-get install -y supervisor')
        sudo('apt-get install -y git')

def _configure_supervisor():
    if not exists(system_supervisor_conf):
        sudo('ln -s %s/%s %s' % (app_dir, local_supervisor_conf, system_supervisor_conf))

def _configure_nginx():
    if not exists(system_nginx_conf):
        sudo('ln -s %s/%s %s' % (app_dir, local_nginx_conf, system_nginx_conf))

def _sync_code():
    if not exists(app_dir):
        run('mkdir -p %s' % app_dir)
    rsync_project(local_dir='./', remote_dir=app_dir, exclude=['venv'], extra_opts='--delete')

def _update_venv():
    with cd(app_dir):
        if not exists('venv'):
            run('virtualenv venv --prompt="(%s)"' % app_name)
        with prefix('source venv/bin/activate'):
            run('pip install -r requirements.txt')

def install():
    _install_requirements()
    _sync_code()
    _update_venv()
    _configure_nginx()
    _configure_supervisor()

def uninstall():
    if exists(app_dir):
        run('rm -rf %s' % app_dir)
    if exists(system_nginx_conf):
        sudo('rm %s' % system_nginx_conf)
    if exists(system_supervisor_conf):
        sudo('rm %s' % system_supervisor_conf)

def update():
    _sync_code()
    _update_venv()
    sudo('supervisorctl reread')
    sudo('supervisorctl restart')
    sudo('service nginx restart')
