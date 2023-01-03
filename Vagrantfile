Vagrant.configure("2") do |config|

  config.vm.box = "ubuntu/focal64"
  config.vm.define :netzob_vagrant
  config.vm.network "private_network", ip: "192.168.56.2"

  config.vm.provider "virtualbox" do |v|
    v.memory = 4096
    v.cpus = 2
  end

  config.vagrant.plugins = ["vagrant-vbguest"]
end
