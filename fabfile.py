from fabric.api import *
from fabric.contrib.files import exists
from fabric.contrib.project import rsync_project
from StringIO import StringIO

# fabric settings
env.user = 'eli'
env.hosts = ['dev.elifiner.com']
env.use_ssh_config = True

# application settings
config = type(env)()
config.app_user = env.user
config.app_name = 'testapp'
config.app_script = 'app.py'
config.app_wsgi_object = 'app:app'
config.remote_app_dir = '/home/%(app_user)s/%(app_name)s' % config

# supervisor configuration
supervisor_config = '''\
[program:%(app_name)s]
command = /home/%(app_user)s/%(app_name)s/venv/bin/gunicorn %(app_wsgi_object)s -b localhost:8000
directory = %(remote_app_dir)s
user = %(app_user)s
''' % config

# nginx configuration
nginx_config = '''\
server {
    location / {
        proxy_pass http://127.0.0.1:8000;
    }
    location /static {
        alias  /home/%(app_user)s/%(app_name)s/static/;
    }
}
''' % config

def setup_server():
    install_requirements()
    install_app()
    configure_supervisor()
    configure_nginx()

def install_requirements():
    with hide('stdout'):
        sudo('apt-get update')
        sudo('apt-get install -y python')
        sudo('apt-get install -y python-pip')
        sudo('apt-get install -y python-virtualenv')
        sudo('apt-get install -y nginx')
        sudo('apt-get install -y supervisor')
        sudo('apt-get install -y git')

def install_app():
    if not exists(config.remote_app_dir):
        run('mkdir -p %s' % config.remote_app_dir)
    update()
    with cd(config.remote_app_dir):
        run('virtualenv venv --prompt="(%s)"' % config.app_name)
        with prefix('source venv/bin/activate'):
            run('pip install -r requirements.txt')

def configure_supervisor():
    conf_path = '/etc/supervisor/conf.d/%s.conf' % config.app_name
    put(StringIO(supervisor_config), conf_path, use_sudo=True)
    sudo('supervisorctl reread')
    sudo('supervisorctl update')

def configure_nginx():
    conf_path = '/etc/nginx/sites-available/%s' % config.app_name
    enabled_path = '/etc/nginx/sites-enabled/%s' % config.app_name
    put(StringIO(nginx_config), conf_path, use_sudo=True)
    if not exists(enabled_path):
        sudo('ln -s %s %s' % (conf_path, enabled_path))
    sudo('/etc/init.d/nginx restart')

def uninstall_app():
    if exists(config.remote_app_dir):
        run('rm -rf %s' % config.remote_app_dir)

def update():
    rsync_project(local_dir='./', remote_dir=config.remote_app_dir, exclude=['venv'])

def start():
    sudo('supervisorctl start %s' % config.app_name)

def stop():
    sudo('supervisorctl stop %s' % config.app_name)

def restart():
    sudo('supervisorctl restart %s' % config.app_name)
