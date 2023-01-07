Vagrant.configure("2") do |config|

  config.vm.provider "virtualbox" do |v|
    v.memory = 3072
    v.cpus = 2
  end

  config.vm.define "netzob-20-04" do |netzob2004|
    netzob2004.vm.box = "ubuntu/focal64"
    netzob2004.vm.provider "virtualbox" do |v_provider|
      v_provider.name = "netzob_20.04"
    end
    netzob2004.vm.network "private_network", ip: "192.168.56.20"
    netzob2004.vm.hostname = "netzob-20-04"
  end

  config.vm.define "netzob-22-04" do |netzob2204|
    netzob2204.vm.box = "ubuntu/jammy64"
    netzob2204.vm.provider "virtualbox" do |v_provider|
      v_provider.name = "netzob_22.04"
    end
    netzob2204.vm.network "private_network", ip: "192.168.56.21"
    netzob2204.vm.hostname = "netzob-22-04"
  end

  config.vagrant.plugins = ["vagrant-vbguest"]
end
