# Misirlou

## Setup
The setup instructions are split into two parts, first setting up the 
django/sorlr/celery backend, and then setting up the frontend.

### Backend

Ensure you have installed [RabbitMQ](https://www.rabbitmq.com/),
[Solr 5](https://lucene.apache.org/solr/),
[Python 3.4+](https://www.python.org/),
[virtualenv](https://virtualenv.readthedocs.org/en/latest/installation.html),
[postgres](http://www.postgresql.org/) and
[redis](http://redis.io/)

In your preferred installation directory, run ``git clone https://github.com/DDMAL/misirlou``.
This creates a 'misirlou' folder. This folder will be referred to as ``$MIS_HOME``.

Set up a virtualenv for the project, and install dependencies.
```bash
cd $MIS_HOME
virtualenv --python=python3 .env
source .env/bin/activate
pip install -r requirements.txt
```

Set up any local settings for your installation. In your new `local_settings.py` file, you can
over-ride any of the projects default settings, including the celery_result_backend, the 
database used, etc... Look in `settings.py` for examples. You should configure a database backend
here, if you'd rather not use SQLite.
```bash
cd $MIS_HOME/misirlou 
mv example-local_settings.py local_settings.py
```

Migrate database.
```bash
#from $MIS_HOME and sourced from your virtualenv.
python manage.py syncdb
```
You need to link the project's solr cores into a `SOLR_HOME` for solr to recognize them.
On my OS, `$SOLR_HOME` is `/opt/solr/server/solr/`. You can also copy the `$MIS_HOME/solr/misirlou`
folder into `$SOLR_HOME` if you don't mind having to potentially recopy it everytime you update.
```bash
# Check that solr is running and note $SOLR_HOME dir.
sudo solr status 

# Link core files into solr_home.
mkdir -p $SOLR_HOME/misirlou/conf $SOLR_HOME/misirlou/data
cp $MIS_HOME/solr/misirlou/core.properties $SOLR_HOME/misirlou
sudo ln -s $MIS_HOME/solr/misirlou/conf/* $SOLR_HOME/misirlou/conf

#Restart solr
sudo solr restart
```

Make sure your redis server is started, as it serves as the result store for 
the celery worker by default.

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

To load development builds of the client-side source, set `DEBUG_CLIENT_SIDE = True`  in your local Django settings and ensure the `NODE_ENV` environment variable is not set to `production`.

To lint the JavaScript files, execute:

```sh
$ npm run lint-js
```

You can build the code once or run a development server which live-reloads client-side assets:

```sh
$ npm run bundle
$ npm run serve-dev
```

The development server runs on port 8001 and proxies the Django server from port 8000. To change the ports, you can set npm configuration values:

```sh
$ npm config set misirlou:dev_server_port 9001
$ npm config set misirlou:dev_server_proxy_port 8008
```
