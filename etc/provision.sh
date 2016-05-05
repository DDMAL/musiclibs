#!/bin/bash

# This script installs all dependencies for the project, suitable for provisioning
# a VM. We recommend running this using Vagrant.

set -e

sudo add-apt-repository -y ppa:chris-lea/redis-server

echo "Updating package lists..."
sudo apt-get -qq update

sudo apt-get install -y python3 python3-pip rabbitmq-server redis-server libpq-dev
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

# Solr support
java_version=$(java -version 2>&1 | awk -F '"' '/version/ {print $2}')

if [[ "$java_version" != "1.8"* ]]; then
    echo "Adding Java 8 PPA and updating package lists..."
    sudo add-apt-repository -y ppa:openjdk-r/ppa
    sudo apt-get -qq update

    sudo apt-get install -y --no-install-recommends openjdk-8-jdk

    # FIXME: I don't really know if this is the right thing to do
    sudo update-alternatives --install /usr/bin/java  java  /usr/lib/jvm/java-8-openjdk-i386/jre/bin/java 2000
    sudo update-alternatives --install /usr/bin/javac javac /usr/lib/jvm/java-8-openjdk-i386/bin/javac    2000
fi

solr_version=6.0.0

# FIXME: Get a better way of checking the current Solr version
if [ ! `which solr` ] || [[  `readlink -f $( which solr )` != *"solr-$solr_version"* ]]; then
    (
        echo "Installing Solr $solr_version..."

        mkdir -p ~/solr
        cd ~/solr

        curl -sS -L "https://www.apache.org/dist/lucene/solr/6.0.0/solr-6.0.0.tgz" -o "solr-$solr_version.tgz"
        tar xzf "solr-$solr_version.tgz"

        # FIXME: there should really be a nicer way of doing installation
        sudo ln -fs "`pwd`/solr-$solr_version/bin/solr" /usr/local/bin/solr

        # Symlink the Misirlou Solr core into the Solr home directory
        mkdir -p "./solr-$solr_version/server/solr"
        ln -s /vagrant/solr/misirlou      "./solr-$solr_version/server/solr/misirlou"
        ln -s /vagrant/solr/misirlou_test "./solr-$solr_version/server/solr/misirlou_test"

        echo "Solr installed!"
    )
fi

# Frontend build support

# Add a PPA to get Node v. 0.12
if ! grep -q nodesource /etc/apt/sources.list /etc/apt/sources.list.d/*; then
    curl -sL https://deb.nodesource.com/setup_0.12 | sudo bash -
fi

# Git is required by JSPM to download GitHub dependencies
sudo apt-get install -y nodejs git
sudo npm install --no-color --global --quiet npm@~2.12

(
    cd /vagrant/misirlou/frontend
    npm run build --no-color --quiet
)
