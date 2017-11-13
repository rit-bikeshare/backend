# Bikeshare Backend

## Setup
1. Make sure you have Python3 and Pipenv installed, as well as a GIS-enabled database.
2. Clone this repo
3. In the root of the repo, run `pipenv install`
4. Create a Django setting file somewhere. `/etc/` is a good place for it. You can inherit from one of the predefined configurations - see the `my_settings` file for an example.
5. Set the env variable `DJANGO_SETTINGS_MODULE` to the name of the file, minus the .py extension. This can be done with eg a procfile. You may also need to configure PYTHONPATH if it does not contain the directory where your settings file is.
6. Optionally define `DATABASE_URL` and install the `dj-database-url` package.

## Launching a dev server
1. In the root of the repo, run `pipenv shell`
2. Prep database with `python3 manage.py makemigrations; python3 manage.py migrate`
3. Run dev server with `python3 manage.py runserver`

## Creating a SuperUser
This is needed to access the admin site.

1. In the root of the repo, run `pipenv shell`
2. Run `python3 manage.py createsuperuser`
3. Enter your RIT ID for the username (eg `sgsvcs`)
4. Password isn't used, so feel free to fake it!
