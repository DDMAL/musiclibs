#!/bin/bash

# This script installs all dependencies for the project, suitable for provisioning
# a VM. We recommend running this using Vagrant.

set -e

echo "Updating package lists..."
sudo apt-get -qq update

# Python dependencies
sudo apt-get install -y python3 python3-pip
sudo pip3 install virtualenv

(
    cd /vagrant

    if [ ! -d env ]; then
        echo "Initializing Python virtualenv..."
        virtualenv env
    fi

    source ./env/bin/activate

    pip install -r requirements.txt

    deactivate
)

# RabbitMQ
sudo apt-get install -y rabbitmq-server

# Solr 5 support
sudo apt-get install -y --no-install-recommends openjdk-7-jdk

if [ ! `which solr` ]; then
    (
        echo "Installing Solr 5..."

        mkdir -p ~/solr
        cd ~/solr

        curl -sS -L "http://apache.mirror.iweb.ca/lucene/solr/5.2.1/solr-5.2.1.tgz" -o solr-5.2.1.tgz
        tar xzf solr-5.2.1.tgz

        # FIXME: there should be nicer ways of doing installation
        sudo ln -s "`pwd`/solr-5.2.1/bin/solr" /usr/local/bin/solr

        # Symlink the Misirlou Solr core into the Solr home directory
        mkdir -p ./solr-5.2.1/server/solr
        ln -s /vagrant/solr/misirlou ./solr-5.2.1/server/solr/misirlou
    )
fi

# Node.js support
# Git is required by JSPM to download GitHub dependencies
sudo apt-get install -y npm nodejs-legacy git
sudo npm install --global --quiet npm@~2.12

(
    cd /vagrant/misirlou/frontend
    npm install --no-color --quiet
)