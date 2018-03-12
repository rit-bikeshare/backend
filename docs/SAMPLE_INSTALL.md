# Sample Installation guideline

This guides you through the installation of the Bikeshare backend on Ubuntu using the preferred pairing of PostGIS and nginx.

## Prereqs

Before beginning this tutorial, you should have Python3, pipenv, and git installed. Supervisor is recommended to manage your applications. If you want to enable Shibboleth support, you'll need your distribution's shibd (shibboleth) package.

## Set up Postgres + PostGIS

We'll use PostgreSQL + PostGIS for our database server. Like nginx, the Ubuntu PPAs are often woefully out of date, so it's better to install directly from the official repo. Follow the directions [here](https://www.postgresql.org/download/linux/ubuntu/) to add the package source, then run `$ sudo apt install postgres postgis` to install the binaries.

Now we need to create a database for the bikeshare backend and enable PostGIS on it using these commands:

```sh
$ sudo su - postgres
$ createdb  bikeshare-backend
$ createuser bikeshare-backend
$ psql bikeshare-backend
> CREATE EXTENSION postgis;
>\q
$ exit
```

## Set up Bikeshare Backend

The next step is to install the bikeshare project, including dependencies. First, create a user for the backend with `$ adduser --disabled-password bikeshare-backend`. Then, switch to the user, download the source, and install project dependencies (including Django):

```sh
$ sudo su - bikeshare-backend
$ git clone https://github.com/rit-bikeshare/backend.git
$ cd backend
$ pipenv install
$ touch backend_settings.py
```

Take note of the `VirtualEnv` path. You need to edit the activation script (`<venv path>/bin/activate`) to set the setting module. For example, I edited `/home/bikeshare-backend/.local/share/virtualenvs/backend-RpNfDm9u/bin/activate`. At the end, I added the following line:

```sh
export DJANGO_SETTINGS_MODULE=backend_settings
```

Now we need to install some packages specific to our database setup:

```sh
$ pipenv shell
$ pip install psycopg2-binary
$ exit
```

### Configuring Settings

Now we need to configure settings for this app by editing `backend_settings.py`. Refer to Django's setting documentation as well as `app.settings.base` to see all options. Following is a minimal configuration for a production server - you will almost certainly want to use more than this:

```python
from app.settings.prod import *

SECRET_KEY = None # Replace with a secret key

ALLOWED_HOSTS = ['localhost'] # Replace with your host

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'bikeshare-backend',
        'CONN_MAX_AGE': 300
    }
}

STATIC_ROOT = '/home/bikeshare-backend/backend/static/'

USE_SHIB = False
```

Note that secret keys can be generated with a resource such as [this one](https://www.miniwebtool.com/django-secret-key-generator/).

This is an example debug configuration. Do **not** use this in production!

```python
from app.settings.debug import *

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'bikeshare-backend',
        'CONN_MAX_AGE': 300
    }
}

STATIC_ROOT = '/home/bikeshare-backend/backend/static/'

USE_SHIB = False
```

### Initialize the application

Now we're ready to initialize the application. Drop into a virtualenv shell (`$ pipenv shell`) and run the following:

```sh
$ python manage.py migrate
$ python manage.py createsuperuser
$ python manage.py collectstatic
$ exit
```

When creating a superuser, use your user id from Shibboleth as your username (eg, `sgsvcs`).

**WARNING**: Superusers are EXTREMELY powerful and can directly edit the database. System users should never be superusers - instead assign them to an appropriate Django group using the Django administration.

## Set Up uWSGI
uWSGI is what will actually run the bikeshare application. Create a config file `backend_uwsgi.ini` in the backend directory. A sample looks like this:

```ini
# mysite_uwsgi.ini file
[uwsgi]

# Django-related settings
# the base directory (full path)
chdir           = /home/bikeshare-backend/backend
# Django's wsgi file
module          = wsgi
# the virtualenv (full path). REPLACE WITH YOURS
home            = /home/bikeshare-backend/.local/share/virtualenvs/backend-RpNfDm9u

# process-related settings
# master
master          = true
# maximum number of worker processes
processes       = 10
# the socket (use the full path to be safe
socket          = /home/bikeshare-backend/backend/uwsgi.sock
# ... with appropriate permissions - may be needed
chmod-socket    = 666
# clear environment on exit
vacuum          = true
```

Make sure you're running as yourself again (ie, you've exited out of the `bikeshare-backend` user), and install uWSGI with the following: `$ sudo pip3 install uwsgi`

If you'd like to test your configuration, drop back into your `pipenv shell` and run `$ uwsgi --ini backend_uwsgi.ini`

### Configure Supervisor
In order to manage uWSGI it's recommended to use Supervisor. You can put the following in `/etc/supervisor/conf.d/bikeshare-backend.conf`:

```ini
[program:bikeshare-backend]
command=uwsgi --ini /home/bikeshare-backend/backend/backend_uwsgi.ini
environment=DJANGO_SETTINGS_MODULE='backend_settings'
user=bikeshare-backend
autostart=true
autorestart=true
stopsignal=QUIT
```

Reload supervisor's config and then ensure uWSGI is running:

```sh
$ sudo service supervisor reload
$ sudo supervisorctl status bikeshare-backend
```

## Set up Nginx

We're ready to install nginx to use as our webserver. Ubuntu packages nginx in the default PPAs, but uses an older version that doesn't work reliably with Shib.

You can follow the directions [on the nginx wiki](https://www.nginx.com/resources/wiki/start/topics/tutorials/install/) to install it.

Once installed, you need to edit `/etc/nginx/nginx.conf` and make sure that this line is inside the `http` block, otherwise nginx won't find your configuration:

```
    include /etc/nginx/sites-enabled/*;
```

We use a standard nginx config put into `/etc/nginx/sites-available/bikeshare-backend` and symlinked to `/etc/nginx/sites-enabled/bikeshare-backend`:

```nginx
# Configure uWSGI server location
upstream django {
    server unix:///home/bikeshare-backend/backend/uwsgi.sock;
}

server {
    listen 80;
    server_name bikesharedev.rit.edu;

    # Serve static files using nginx
    location /api/static/ {
        alias /home/bikeshare-backend/backend/static;
    }

    # Everything else gets passed through to Django
    location /api/ {
         include uwsgi_params;
         uwsgi_pass django;
    }
}
```

At this point, you should be able to hit your server and see the bikeshare backend live!

## Shibboleth Support
Shibboleth support is great for integration, but requires a lot of extra setup. Fortunately, this is (fairly) well documented.

To get started with Shib/nginx, follow the docs located [here](https://github.com/nginx-shib/nginx-http-shibboleth/blob/master/CONFIG.rst).

When all is said and done, your nginx config should resemble this:

```
upstream django {
    server unix:///home/bikeshare-backend/backend/uwsgi.sock;
}

server {
    listen 80;
    server_name bikesharedev.rit.edu;

    #FastCGI authorizer for Auth Request module
    location = /shibauthorizer {
        internal;
        include fastcgi_params;
        fastcgi_pass unix:/opt/shibboleth/shibauthorizer.sock;
    }

    #FastCGI responder
    location /Shibboleth.sso {
        include fastcgi_params;
        fastcgi_pass unix:/opt/shibboleth/shibresponder.sock;
    }

    #Resources for the Shibboleth error pages. This can be customised.
    location /shibboleth-sp {
        alias /usr/share/shibboleth/;
    }

    location /api/static/ {
        alias /home/bikeshare-backend/backend/static;
    }

    location /api/login/ {
         shib_request /shibauthorizer;

		 include shib_uwsgi_params;
        
         shib_request_set $shib_uid $upstream_http_variable_uid;
         shib_request_set $shib_sn $upstream_http_variable_sn;
         shib_request_set $shib_givenname $upstream_http_variable_givenname;
         shib_request_set $shib_affiliation $upstream_http_variable_affiliation;

         uwsgi_param uid $shib_uid;
         uwsgi_param sn $shib_sn;
         uwsgi_param givenName $shib_givenname;
         uwsgi_param AFFILIATION $shib_affiliation;

         include uwsgi_params;
         uwsgi_pass django;
    }

    location /api/ {
         include uwsgi_params;
         uwsgi_pass django;
    }
}
```

You can obtain the `shib_uwsgi_params` file with this incantation:

```# curl https://raw.githubusercontent.com/nginx-shib/nginx-http-shibboleth/master/includes/shib_fastcgi_params | sed 's/fastcgi_param/uwsgi_param/g' > /etc/nginx/shib_uwsgi_params```