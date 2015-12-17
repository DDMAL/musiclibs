# Misirlou

## Setup
The setup instructions are split into two parts, first setting up the 
django/sorlr/celery backend, and then setting up the frontend.

### Backend

Ensure you have installed [RabbitMQ](https://www.rabbitmq.com/),
[Solr 5](https://lucene.apache.org/solr/),
[Python 3.4+](https://www.python.org/) and
[virtualenv](https://virtualenv.readthedocs.org/en/latest/installation.html).

In your preferred installation directory, run ``git clone https://github.com/DDMAL/misirlou``.
This creates a 'misirlou' folder. This folder will be referred to as ``$MIS_HOME``.

Navigate to ``$MIS_HOME`` and execute ``virtualenv --python=python3 env``. It is not
strictly necessary to name the virtual environment "env",
but its easy to type and these instructions will assume you have.

Execute ``source env/bin/activate; pip install -r requirements.txt`` in order
to install the required python libraries to your virtual environment.

Navigate to ``$MIS_HOME/misirlou`` and either copy or rename ``example-local_settings.py``
to ``local_settings.py``.

Back in ``$MIS_HOME``, execute ``python manage.py syncdb`` to prep the sqlite database.

Ensure solr is running by executing ``solr status``. If it is not,
run ``sudo solr start``. Once it has started, execute ``solr status`` once
more and take note of the ``sole_home`` value. On my machine this is 
``/opt/solr/server/solr/`` but it will vary depending on OS. This path
will be referred to as ``$SOLR_HOME``.

Execute ``sudo ln -s $MIS_HOME/solr/misirlou $SOLR_HOME``. This will create
a link to the core configuration files that come with misirlou in your solr home.
Execute ``sudo solr restart`` to restart solr and load this newly linked core.

To start misirlou locally, execute the ``start.sh`` script in ``$MIS_HOME``. This
will start a celery worker and local server and redirect their combined output
to the terminal. Killing this script with CTRL+C will kill both child processes.

If you'd prefer to have more discrete control over the server and celery process,
you may execute ``source env/bin/activate; python manage.py runserver_plus`` in
``$MIS_HOME`` to start the server, then execute 
``source env/bin/activate; celery -A misirlou  worker -l info`` in a separate 
terminal to start Celery.

### Frontend

The only required global dependencies for Misirlou's client-side are [Node.js](https://nodejs.org/) (tested
with version 0.12) and npm. Once those are installed, follow these steps from the project root directory to build
the source files:

```sh
$ cd misirlou/frontend
$ npm run build
```

## Development workflow

### Frontend

If you're developing the front-end, you may want to install the [JSPM](https://github.com/jspm/jspm-cli)
command-line tool by running `npm install -g jspm`.

To lint the JavaScript files, execute:

```sh
$ npm run lint-js
```

Finally, to run a development server which live-reloads client-side assets, execute:

```sh
$ npm run install-dev-server
$ npm run serve-dev
```

(Currently, the development server is installed unconventionally using a script because many users will not need
it and npm does not support optional devDependencies.)
