# BioCloud

The ultimate Django server to run NGS analysis pipeline.


## Getting Started

### Requirements

- Git
- Python 3.5+

### Set up a Python Virtual Environment

#### Built-in `venv`

Create the virtual environment at `<repo>/venv`:

    python3 -m venv venv

To activate it:

    . venv/bin/activate

Or on Windows, use

    . venv\Scripts\activate.bat

### Install Dependencies

Use pip:

    pip install -r requirements.txt


### Set up Local Environment Variables and Database

Settings are stored in environment variables via [django-environ]. The
quickiest way to start is to copy `local.sample.env` into `local.env`:

    cp src/biocloud/settings/local.sample.env src/biocloud/settings/local.env

Then edit the `SECRET_KEY` line in `local.env`, replacing `{{ secret_key }}` into any [Django Secret Key] value. An example:

    SECRET_KEY=-@5#xz3#f)4waw+p=l^c$1!6ei8&c5u_=^%*sdu(6vy@m$*-v&

After that, just run the migration.


### Go Develop

Change to the `src` directory:

    cd src

The website uses [PostgreSQL] database, make sure it has been running. On OSX, PostgreSQL may not run in the background, which can be started manually by

    fab start_db

Then run the database migration.

    python manage.py migrate

Run the development server

    python manage.py runserver

the Django-Q job cluster for executing pipeline jobs

    python manage.py qcluster

and a local SMTP server so all email sending will be captured

    fab start_smtp


[PostgreSQL]: https://www.postgresql.org/


## License

Release under MIT License. A great portion of code is adapted from [PyCon Taiwan 2016 website]'s source code under license MIT.


[Anaconda]: https://www.continuum.io/downloads
[conda]: http://conda.pydata.org/docs/intro.html
[django-environ]: http://django-environ.readthedocs.org/en/latest/
[Django Secret Key]: http://www.miniwebtool.com/django-secret-key-generator/
[PyCon Taiwan 2016 website]: https://github.com/pycontw/pycontw2016
