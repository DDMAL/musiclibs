# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure(2) do |config|
  config.vm.box = "ubuntu/trusty32"

  config.vm.network "forwarded_port", guest: 8000, host: 8008

  config.vm.provision "shell", privileged: false, path: "etc/provision.sh"

  config.vm.provider "virtualbox" do |v|
    v.memory = 1024
  end
end
