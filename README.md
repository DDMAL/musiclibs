# Misirlou

## Setup

### Backend

*Installation instructions to come.*

Misirlou requires Python, virtualenv, RabbitMQ, Celery, and Solr 5.

### Frontend

The only required global dependencies for Misirlou's client-side are [Node.js](https://nodejs.org/) (tested
with version 0.12) and npm. Once those are installed, follow these steps from the project root directory to build
the source files:

```sh
$ cd misirlou/frontend
$ npm install
```

If you're developing the front-end, you may also want to install the [JSPM](https://github.com/jspm/jspm-cli)
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
