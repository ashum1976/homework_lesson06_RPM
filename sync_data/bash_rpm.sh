#! /usr/bin/bash

cd /root/
rpmdev-setuptree

rpmdir = /root/rpmbuild

wget https://nginx.org/packages/centos/7/SRPMS/nginx-1.18.0-2.el7.ngx.src.rpm
rpm -i /root/nginx-1.18.0-2.el7.ngx.src.rpm

# Также нужно скачать и разархивировать последний исходники для openssl - он потребуется при сборке:
wget https://www.openssl.org/source/latest.tar.gz && tar -xzf latest.tar.gz

# Заранее поставим все зависимости чтобы в процессе сборки не было ошибок:

yum-builddep ${rpmdir}/SPECS/nginx.spec

# Копируем изменённый spec файл, настроенный для сборки нового пакета:

cp -f  /vagrant/ nginx.spec /root/rpmbuild/SPECS/nginx.spec

# Собираем пакет RPM:

rpmbuild -bb ${rpmdir}/SPECS/nginx.spec 

if  [[ $? == 0 ]]

    then
        yum localinstall ${rpmdir}RPMS/x86_64/*  -y
    else 
        exit 5
fi


mkdir  /usr/share/nginx/html/repo

mv  ${rpmdir}/RPMS/x86_64/* /usr/share/nginx/html/repo/

createrepo /usr/share/nginx/html/repo/

if [[ $? == 0 ]]
    then
        systemctl start nginx
    else 
        exit 5
fi
        
yum-config-manager --add-repo=http://localhost/repo/

testrepo = 'yum repolist enabled | grep localhost_repo  > /dev/null 2>&1'

if [[ $? == 0   ]] 
    then 
        echo "Репозиторий создан "
    else 
        echo  "Косяк с репой"
        exit 5
fi
