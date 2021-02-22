

#                                                               Домашнее задание



##                                          Сборка RPM


Для сборки RPM нужны пакеты:

            rpmdevtools
            rpm-build
            
        
Команда rpmdev-setuptree создаёт в домашней папке пользователя, кто её запустил, каталог  rpmbuild с подкаталагами всей структуры для сборки пакетов.

            rpmdev-setuptree
            
Для выполнения задачи, загрузим  SRPM пакет NGINX для дальнейшей работы над ним, соберем его с поддержкой openssl:

            [root@gpt-lvm SOURCES]# wget https://nginx.org/packages/centos/7/SRPMS/nginx-1.18.0-2.el7.ngx.src.rpm
            
            --2021-02-22 10:41:58--  https://nginx.org/packages/centos/7/SRPMS/nginx-1.18.0-2.el7.ngx.src.rpm
            Resolving nginx.org (nginx.org)... 52.58.199.22, 3.125.197.172, 2a05:d014:edb:5704::6, ...
            Connecting to nginx.org (nginx.org)|52.58.199.22|:443... connected.
            HTTP request sent, awaiting response... 200 OK
            Length: 1055846 (1.0M) [application/x-redhat-package-manager]
            Saving to: ‘nginx-1.18.0-2.el7.ngx.src.rpm’

            100%[====================================================================================================================================================================================================>] 1,055,846   6.17MB/s   in 0.2s

            2021-02-22 10:41:58 (6.17 MB/s) - ‘nginx-1.18.0-2.el7.ngx.src.rpm’ saved [1055846/1055846

Также нужно скачать и разархивировать последний исходники для openssl - он потребуется при сборке:

             [root@gpt-lvm ~]#  wget https://www.openssl.org/source/latest.tar.gz
             
             [root@gpt-lvm ~]# tar -xzf latest.tar.gz

Заранее поставим все зависимости чтобы в процессе сборки не было ошибок:
             
             [root@gpt-lvm openssl-1.1.1j]# yum-builddep ~/rpmbuild/SPECS/nginx.spec

             etting requirements for /root/rpmbuild/SPECS/nginx.spec
                --> Already installed : systemd-219-78.el7_9.3.x86_64
                --> Already installed : 1:openssl-devel-1.0.2k-21.el7_9.x86_64
                --> Already installed : zlib-devel-1.2.7-19.el7_9.x86_64
                --> Already installed : pcre-devel-8.32-17.el7.x86_64
                

            
            
            
Если установить  src.rpm пакет, в домашней директории создается древо каталогов для сборки, как и при запуске программы rpmdev-setuptree, только папок может быть меньше:
          
            [root@gpt-lvm SOURCES]# tree ~/rpmbuild/
            
            /root/rpmbuild/
            ├── BUILD
            ├── RPMS
            ├── SOURCES
            │   ├── logrotate
            │   ├── nginx-1.18.0.tar.gz
            │   ├── nginx.check-reload.sh
            │   ├── nginx.conf
            │   ├── nginx.copyright
            │   ├── nginx-debug.service
            │   ├── nginx-debug.sysconf
            │   ├── nginx.init.in
            │   ├── nginx.service
            │   ├── nginx.suse.logrotate
            │   ├── nginx.sysconf
            │   ├── nginx.upgrade.sh
            │   └── nginx.vh.default.conf
            ├── SPECS
            │   └── nginx.spec
            └── SRPMS
            
 
 
 Для запуска сборки пакета нужно поправить spec файл, лежащий в одноимённой директории:
 
 
            /root/rpmbuild/SPECS/nginx.spec

поскольку сборка производится на кастомном образе centos7, с ядром 5.10.17, которое можно было собрать компилятором gcc версии 7 и выше, а в репозиториях такой версии не было. GCC было установлено с использованием make, make install в папку /usr/local/bin/. И в nginx.spec файле это нужно отразить:


            %build
            ./configure %{BASE_CONFIGURE_ARGS} \
                
                --with-cc=/usr/local/bin/gcc \        <----- путь к gcc, не смотря на то что в переменной $PATH прописан, при сборке пакета не находится, указываем прямо где лежит.
                
                --with-cc-opt="%{WITH_CC_OPT}" \
                --with-ld-opt="%{WITH_LD_OPT}" \
                --with-openssl=/root/openssl-1.1.1j   <----- путь к скачанным исходникам openssl 


            
 при появлении ошибки  связанной с получением информации о debug: 
            
            *** ERROR: No build ID note found in /root/rpmbuild/BUILDROOT/nginx-1.18.0-2.el7.ngx.x86_64/usr/sbin/nginx
            
в начале файла  nginx.spec, поместить

*           %define debug_package %{nil}

полный вид nginx.spec:

<details>
           
#    <summary> Переделанный spec файл </summary>
           
           #
            %define nginx_home %{_localstatedir}/cache/nginx
            %define nginx_user nginx
            %define nginx_group nginx
            %define nginx_loggroup adm
            %define debug_package %{nil}

            # distribution specific definitions
            %define use_systemd (0%{?rhel} >= 7 || 0%{?fedora} >= 19 || 0%{?suse_version} >= 1315 || 0%{?amzn} >= 2)

            %if %{use_systemd}
            BuildRequires: systemd
            Requires(post): systemd
            Requires(preun): systemd
            Requires(postun): systemd
            %endif

            %if 0%{?rhel}
            %define _group System Environment/Daemons
            %endif

            %if 0%{?rhel} == 6
            Requires(pre): shadow-utils
            Requires: initscripts >= 8.36
            Requires(post): chkconfig
            Requires: openssl >= 1.0.1
            BuildRequires: openssl-devel >= 1.0.1
            %endif

            %if 0%{?rhel} == 7
            %define epoch 1
            Epoch: %{epoch}
            Requires(pre): shadow-utils
            Requires: openssl >= 1.0.2
            BuildRequires: openssl-devel >= 1.0.2
            %define dist .el7
            %endif

            %if 0%{?rhel} == 8
            %define epoch 1
            Epoch: %{epoch}
            Requires(pre): shadow-utils
            BuildRequires: openssl-devel >= 1.1.1
            %define _debugsource_template %{nil}
            %endif

            %if 0%{?suse_version} >= 1315
            %define _group Productivity/Networking/Web/Servers
            %define nginx_loggroup trusted
            Requires(pre): shadow
            BuildRequires: libopenssl-devel
            %define _debugsource_template %{nil}
            %endif

            %if 0%{?fedora}
            %define _debugsource_template %{nil}
            %global _hardened_build 1
            %define _group System Environment/Daemons
            BuildRequires: openssl-devel
            Requires(pre): shadow-utils
            %endif

            # end of distribution specific definitions

            %define base_version 1.18.0
            %define base_release 2%{?dist}.ngx

            %define bdir %{_builddir}/%{name}-%{base_version}

            %define WITH_CC_OPT $(echo %{optflags} $(pcre-config --cflags)) -fPIC
            %define WITH_LD_OPT -Wl,-z,relro -Wl,-z,now -pie

            %define BASE_CONFIGURE_ARGS $(echo "--prefix=%{_sysconfdir}/nginx --sbin-path=%{_sbindir}/nginx --modules-path=%{_libdir}/nginx/modules --conf-path=%{_sysconfdir}/nginx/nginx.conf --error-log-path=%{_localstatedir}/log/nginx/error.log --http-log-path=%{_localstatedir}/log/nginx/access.log --pid-path=%{_localstatedir}/run/nginx.pid --lock-path=%{_localstatedir}/run/nginx.lock --http-client-body-temp-path=%{_localstatedir}/cache/nginx/client_temp --http-proxy-temp-path=%{_localstatedir}/cache/nginx/proxy_temp --http-fastcgi-temp-path=%{_localstatedir}/cache/nginx/fastcgi_temp --http-uwsgi-temp-path=%{_localstatedir}/cache/nginx/uwsgi_temp --http-scgi-temp-path=%{_localstatedir}/cache/nginx/scgi_temp --user=%{nginx_user} --group=%{nginx_group} --with-compat --with-file-aio --with-threads --with-http_addition_module --with-http_auth_request_module --with-http_dav_module --with-http_flv_module --with-http_gunzip_module --with-http_gzip_static_module --with-http_mp4_module --with-http_random_index_module --with-http_realip_module --with-http_secure_link_module --with-http_slice_module --with-http_ssl_module --with-http_stub_status_module --with-http_sub_module --with-http_v2_module --with-mail --with-mail_ssl_module --with-stream --with-stream_realip_module --with-stream_ssl_module --with-stream_ssl_preread_module")

            Summary: High performance web server
            Name: nginx
            Version: %{base_version}
            Release: %{base_release}
            Vendor: Nginx, Inc.
            URL: http://nginx.org/
            Group: %{_group}

            Source0: http://nginx.org/download/%{name}-%{version}.tar.gz
            Source1: logrotate
            Source2: nginx.init.in
            Source3: nginx.sysconf
            Source4: nginx.conf
            Source5: nginx.vh.default.conf
            Source7: nginx-debug.sysconf
            Source8: nginx.service
            Source9: nginx.upgrade.sh
            Source10: nginx.suse.logrotate
            Source11: nginx-debug.service
            Source12: nginx.copyright
            Source13: nginx.check-reload.sh

            License: 2-clause BSD-like license

            BuildRoot: %{_tmppath}/%{name}-%{base_version}-%{base_release}-root
            BuildRequires: zlib-devel
            BuildRequires: pcre-devel

            Provides: webserver
            Provides: nginx-r%{base_version}

            %description
            nginx [engine x] is an HTTP and reverse proxy server, as well as
            a mail proxy server.

            %if 0%{?suse_version} >= 1315
            %debug_package
            %endif

            %prep
            %setup -q
            cp %{SOURCE2} .
            sed -e 's|%%DEFAULTSTART%%|2 3 4 5|g' -e 's|%%DEFAULTSTOP%%|0 1 6|g' \
                -e 's|%%PROVIDES%%|nginx|g' < %{SOURCE2} > nginx.init
            sed -e 's|%%DEFAULTSTART%%||g' -e 's|%%DEFAULTSTOP%%|0 1 2 3 4 5 6|g' \
                -e 's|%%PROVIDES%%|nginx-debug|g' < %{SOURCE2} > nginx-debug.init

            %build
            ./configure %{BASE_CONFIGURE_ARGS} \
                --with-cc=/usr/local/bin/gcc \
                --with-cc-opt="%{WITH_CC_OPT}" \
                --with-ld-opt="%{WITH_LD_OPT}" \
                --with-openssl=/root/openssl-1.1.1j
                
            make %{?_smp_mflags}
            %{__mv} %{bdir}/objs/nginx \
                %{bdir}/objs/nginx-debug
            ./configure %{BASE_CONFIGURE_ARGS} \
                --with-cc=/usr/local/bin/gcc \
                --with-cc-opt="%{WITH_CC_OPT}" \
                --with-ld-opt="%{WITH_LD_OPT}"
            make %{?_smp_mflags}

            %install
            %{__rm} -rf $RPM_BUILD_ROOT
            %{__make} DESTDIR=$RPM_BUILD_ROOT INSTALLDIRS=vendor install

            %{__mkdir} -p $RPM_BUILD_ROOT%{_datadir}/nginx
            %{__mv} $RPM_BUILD_ROOT%{_sysconfdir}/nginx/html $RPM_BUILD_ROOT%{_datadir}/nginx/

            %{__rm} -f $RPM_BUILD_ROOT%{_sysconfdir}/nginx/*.default
            %{__rm} -f $RPM_BUILD_ROOT%{_sysconfdir}/nginx/fastcgi.conf

            %{__mkdir} -p $RPM_BUILD_ROOT%{_localstatedir}/log/nginx
            %{__mkdir} -p $RPM_BUILD_ROOT%{_localstatedir}/run/nginx
            %{__mkdir} -p $RPM_BUILD_ROOT%{_localstatedir}/cache/nginx

            %{__mkdir} -p $RPM_BUILD_ROOT%{_libdir}/nginx/modules
            cd $RPM_BUILD_ROOT%{_sysconfdir}/nginx && \
                %{__ln_s} ../..%{_libdir}/nginx/modules modules && cd -

            %{__mkdir} -p $RPM_BUILD_ROOT%{_datadir}/doc/%{name}-%{base_version}
            %{__install} -m 644 -p %{SOURCE12} \
                $RPM_BUILD_ROOT%{_datadir}/doc/%{name}-%{base_version}/COPYRIGHT

            %{__mkdir} -p $RPM_BUILD_ROOT%{_sysconfdir}/nginx/conf.d
            %{__rm} $RPM_BUILD_ROOT%{_sysconfdir}/nginx/nginx.conf
            %{__install} -m 644 -p %{SOURCE4} \
                $RPM_BUILD_ROOT%{_sysconfdir}/nginx/nginx.conf
            %{__install} -m 644 -p %{SOURCE5} \
                $RPM_BUILD_ROOT%{_sysconfdir}/nginx/conf.d/default.conf

            %{__mkdir} -p $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig
            %{__install} -m 644 -p %{SOURCE3} \
                $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/nginx
            %{__install} -m 644 -p %{SOURCE7} \
                $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/nginx-debug

            %{__install} -p -D -m 0644 %{bdir}/objs/nginx.8 \
                $RPM_BUILD_ROOT%{_mandir}/man8/nginx.8

            %if %{use_systemd}
            # install systemd-specific files
            %{__mkdir} -p $RPM_BUILD_ROOT%{_unitdir}
            %{__install} -m644 %SOURCE8 \
                $RPM_BUILD_ROOT%{_unitdir}/nginx.service
            %{__install} -m644 %SOURCE11 \
                $RPM_BUILD_ROOT%{_unitdir}/nginx-debug.service
            %{__mkdir} -p $RPM_BUILD_ROOT%{_libexecdir}/initscripts/legacy-actions/nginx
            %{__install} -m755 %SOURCE9 \
                $RPM_BUILD_ROOT%{_libexecdir}/initscripts/legacy-actions/nginx/upgrade
            %{__install} -m755 %SOURCE13 \
                $RPM_BUILD_ROOT%{_libexecdir}/initscripts/legacy-actions/nginx/check-reload
            %else
            # install SYSV init stuff
            %{__mkdir} -p $RPM_BUILD_ROOT%{_initrddir}
            %{__install} -m755 nginx.init $RPM_BUILD_ROOT%{_initrddir}/nginx
            %{__install} -m755 nginx-debug.init $RPM_BUILD_ROOT%{_initrddir}/nginx-debug
            %endif

            # install log rotation stuff
            %{__mkdir} -p $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d
            %if 0%{?suse_version}
            %{__install} -m 644 -p %{SOURCE10} \
                $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d/nginx
            %else
            %{__install} -m 644 -p %{SOURCE1} \
                $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d/nginx
            %endif

            %{__install} -m755 %{bdir}/objs/nginx-debug \
                $RPM_BUILD_ROOT%{_sbindir}/nginx-debug

            %check
            %{__rm} -rf $RPM_BUILD_ROOT/usr/src
            cd %{bdir}
            grep -v 'usr/src' debugfiles.list > debugfiles.list.new && mv debugfiles.list.new debugfiles.list
            cat /dev/null > debugsources.list
            %if 0%{?suse_version} >= 1500
            cat /dev/null > debugsourcefiles.list
            %endif

            %clean
            %{__rm} -rf $RPM_BUILD_ROOT

            %files
            %defattr(-,root,root)

            %{_sbindir}/nginx
            %{_sbindir}/nginx-debug

            %dir %{_sysconfdir}/nginx
            %dir %{_sysconfdir}/nginx/conf.d
            %{_sysconfdir}/nginx/modules

            %config(noreplace) %{_sysconfdir}/nginx/nginx.conf
            %config(noreplace) %{_sysconfdir}/nginx/conf.d/default.conf
            %config(noreplace) %{_sysconfdir}/nginx/mime.types
            %config(noreplace) %{_sysconfdir}/nginx/fastcgi_params
            %config(noreplace) %{_sysconfdir}/nginx/scgi_params
            %config(noreplace) %{_sysconfdir}/nginx/uwsgi_params
            %config(noreplace) %{_sysconfdir}/nginx/koi-utf
            %config(noreplace) %{_sysconfdir}/nginx/koi-win
            %config(noreplace) %{_sysconfdir}/nginx/win-utf

            %config(noreplace) %{_sysconfdir}/logrotate.d/nginx
            %config(noreplace) %{_sysconfdir}/sysconfig/nginx
            %config(noreplace) %{_sysconfdir}/sysconfig/nginx-debug
            %if %{use_systemd}
            %{_unitdir}/nginx.service
            %{_unitdir}/nginx-debug.service
            %dir %{_libexecdir}/initscripts/legacy-actions/nginx
            %{_libexecdir}/initscripts/legacy-actions/nginx/*
            %else
            %{_initrddir}/nginx
            %{_initrddir}/nginx-debug
            %endif

            %attr(0755,root,root) %dir %{_libdir}/nginx
            %attr(0755,root,root) %dir %{_libdir}/nginx/modules
            %dir %{_datadir}/nginx
            %dir %{_datadir}/nginx/html
            %{_datadir}/nginx/html/*

            %attr(0755,root,root) %dir %{_localstatedir}/cache/nginx
            %attr(0755,root,root) %dir %{_localstatedir}/log/nginx

            %dir %{_datadir}/doc/%{name}-%{base_version}
            %doc %{_datadir}/doc/%{name}-%{base_version}/COPYRIGHT
            %{_mandir}/man8/nginx.8*

            %pre
            # Add the "nginx" user
            getent group %{nginx_group} >/dev/null || groupadd -r %{nginx_group}
            getent passwd %{nginx_user} >/dev/null || \
                useradd -r -g %{nginx_group} -s /sbin/nologin \
                -d %{nginx_home} -c "nginx user"  %{nginx_user}
            exit 0

            %post
            # Register the nginx service
            if [ $1 -eq 1 ]; then
            %if %{use_systemd}
                /usr/bin/systemctl preset nginx.service >/dev/null 2>&1 ||:
                /usr/bin/systemctl preset nginx-debug.service >/dev/null 2>&1 ||:
            %else
                /sbin/chkconfig --add nginx
                /sbin/chkconfig --add nginx-debug
            %endif
                # print site info
                cat <<BANNER
            ----------------------------------------------------------------------

            Thanks for using nginx!

            Please find the official documentation for nginx here:
            * http://nginx.org/en/docs/

            Please subscribe to nginx-announce mailing list to get
            the most important news about nginx:
            * http://nginx.org/en/support.html

            Commercial subscriptions for nginx are available on:
            * http://nginx.com/products/

            ----------------------------------------------------------------------
            BANNER

                # Touch and set permisions on default log files on installation

                if [ -d %{_localstatedir}/log/nginx ]; then
                    if [ ! -e %{_localstatedir}/log/nginx/access.log ]; then
                        touch %{_localstatedir}/log/nginx/access.log
                        %{__chmod} 640 %{_localstatedir}/log/nginx/access.log
                        %{__chown} nginx:%{nginx_loggroup} %{_localstatedir}/log/nginx/access.log
                    fi

                    if [ ! -e %{_localstatedir}/log/nginx/error.log ]; then
                        touch %{_localstatedir}/log/nginx/error.log
                        %{__chmod} 640 %{_localstatedir}/log/nginx/error.log
                        %{__chown} nginx:%{nginx_loggroup} %{_localstatedir}/log/nginx/error.log
                    fi
                fi
            fi

            %preun
            if [ $1 -eq 0 ]; then
            %if %use_systemd
                /usr/bin/systemctl --no-reload disable nginx.service >/dev/null 2>&1 ||:
                /usr/bin/systemctl stop nginx.service >/dev/null 2>&1 ||:
            %else
                /sbin/service nginx stop > /dev/null 2>&1
                /sbin/chkconfig --del nginx
                /sbin/chkconfig --del nginx-debug
            %endif
            fi

            %postun
            %if %use_systemd
            /usr/bin/systemctl daemon-reload >/dev/null 2>&1 ||:
            %endif
            if [ $1 -ge 1 ]; then
                /sbin/service nginx status  >/dev/null 2>&1 || exit 0
                /sbin/service nginx upgrade >/dev/null 2>&1 || echo \
                    "Binary upgrade failed, please check nginx's error.log"
            fi

</details>

После успешной сборки получаем готовы файл для установки в систему:


            [root@gpt-lvm ~]# ll rpmbuild/RPMS/x86_64/
            total 5472
            -rw-r--r--. 1 root root 5599588 Feb 22 19:58 nginx-1.18.0-2.el7.ngx.x86_64.rpm
            
            
Устанавливаем nginx в систему:


            [root@gpt-lvm ~]# yum localinstall rpmbuild/RPMS/x86_64/nginx-1.18.0-2.el7.ngx.x86_64.rpm  -y
            
            Loaded plugins: fastestmirror
            Examining rpmbuild/RPMS/x86_64/nginx-1.18.0-2.el7.ngx.x86_64.rpm: 1:nginx-1.18.0-2.el7.ngx.x86_64
            Marking rpmbuild/RPMS/x86_64/nginx-1.18.0-2.el7.ngx.x86_64.rpm to be installed
            Resolving Dependencies                                                                                                                                                                              
            --> Running transaction check
            ---> Package nginx.x86_64 1:1.18.0-2.el7.ngx will be installed
            Running transaction
            ......................
            Installing : 1:nginx-1.18.0-2.el7.ngx.x86_64                                                                                                                                                   1/1
            ----------------------------------------------------------------------

            Thanks for using nginx!

            Please find the official documentation for nginx here:
            * http://nginx.org/en/docs/

            Please subscribe to nginx-announce mailing list to get
            the most important news about nginx:
            * http://nginx.org/en/support.html

            Commercial subscriptions for nginx are available on:
            * http://nginx.com/products/

            ----------------------------------------------------------------------
            Verifying  : 1:nginx-1.18.0-2.el7.ngx.x86_64                                                                                                                                                   1/1

            Installed:
            nginx.x86_64 1:1.18.0-2.el7.ngx

            Complete!

            
Проверка старта сервиса с помощью systemd:

            [root@gpt-lvm ~]# systemctl start nginx
            
            
            root@gpt-lvm ~]# systemctl status nginx   <----- проверяем статус сервиса nginx
            
            
            ● nginx.service - nginx - high performance web server
            Loaded: loaded (/usr/lib/systemd/system/nginx.service; disabled; vendor preset: disabled)
            Active: active (running) since Mon 2021-02-22 20:19:17 UTC; 4min 14s ago
                Docs: http://nginx.org/en/docs/
            Process: 19356 ExecStart=/usr/sbin/nginx -c /etc/nginx/nginx.conf (code=exited, status=0/SUCCESS)
            Main PID: 19357 (nginx)
            CGroup: /system.slice/nginx.service
                    ├─19357 nginx: master process /usr/sbin/nginx -c /etc/nginx/nginx.conf
                    └─19358 nginx: worker process
            
            [root@gpt-lvm ~]# lsof -n | grep nginx | grep LISTEN     <---- или так посмотерть запущен сервис или нет
            
            nginx     19357         root    6u     IPv4              49047       0t0        TCP *:http (LISTEN)
            nginx     19358        nginx    6u     IPv4              49047       0t0        TCP *:http (LISTEN)
            
            
            
            
