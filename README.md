# Bikeshare Backend

## Setup
1. Make sure you have Python3 and Pipenv installed
2. Clone this repo
3. In the root of the repo, run `pipenv install`

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
