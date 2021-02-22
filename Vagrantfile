Vagrant.configure("2") do |config|
  config.vm.box = "ashum1976/centos7_kernel_5.10"
                config.vm.synced_folder ".", "/vagrant", disabled: true
                config.vm.synced_folder "./sync_data", "/vagrant"
                config.vm.provision "shell", inline: <<-SHELL
                        mkdir -p ~root/.ssh
                        cp ~vagrant/.ssh/auth* ~root/.ssh
                        yum install -y redhat-lsb-core rpmdevtools rpm-build createrepo yum-utils wget

                SHELL
		
end
