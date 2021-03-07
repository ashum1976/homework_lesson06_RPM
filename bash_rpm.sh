#! /usr/bin/bash

export PATH=$PATH:/usr/local/bin
cd /root/

# Создаём структуру папок, для сборки rpm пакета

rpmdev-setuptree

rpmdir="/root/rpmbuild"

if [[ ! -e nginx-1.18.0-2.el7.ngx.src.rpm ]]
    then

        wget https://nginx.org/packages/centos/7/SRPMS/nginx-1.18.0-2.el7.ngx.src.rpm
        rpm -i /root/nginx-1.18.0-2.el7.ngx.src.rpm
fi

# Также нужно скачать и разархивировать последний исходники для openssl - он потребуется при сборке:

if [[ ! -e latest.tar.gz ]]
    then
        wget https://www.openssl.org/source/latest.tar.gz && tar -xzf latest.tar.gz
fi


# Заранее поставим все зависимости чтобы в процессе сборки не было ошибок:

yum-builddep $rpmdir/SPECS/nginx.spec > /dev/null 2>&1

# Копируем изменённый spec файл, настроенный для сборки нового пакета:

cp -f  /vagrant/nginx.spec $rpmdir/SPECS/nginx.spec

# Собираем пакет RPM:

rpmbuild -bb $rpmdir/SPECS/nginx.spec > /dev/null 2>&1

if  [[ $? == 0 ]]

    then
        yum localinstall $rpmdir/RPMS/x86_64/*  -y
    else 
        exit 5
fi


if [[ ! -d /usr/share/nginx/html/repo ]]
    then
        mkdir  /usr/share/nginx/html/repo
fi

mv  ${rpmdir}/RPMS/x86_64/* /usr/share/nginx/html/repo/

createrepo /usr/share/nginx/html/repo/

if [[ $? == 0 ]]
    then
        systemctl start nginx
    else 
        exit 5
fi
        
yum-config-manager --add-repo=http://localhost/repo/ 2>/dev/null

testrepo=$(yum repolist enabled | grep localhost_repo  > /dev/null 2>&1)
if [[ $? == 0   ]] 
    then 
        echo -e "\e[34mРепозиторий создан\e[0m"
    else 
        echo -e "\e[31mКосяк с репой\e[0m" 
        exit 5
fi

