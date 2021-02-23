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

%changelog
* Thu Oct 29 2020 Andrei Belov <defan@nginx.com> - 1.18.0-2%{?dist}.ngx
- 1.18.0-2 (improved module dependency tracking)

* Tue Apr 21 2020 Konstantin Pavlov <thresh@nginx.com> - 1.18.0-1%{?dist}.ngx
- 1.18.0

* Tue Aug 13 2019 Andrei Belov <defan@nginx.com> - 1.16.1-1%{?dist}.ngx
- 1.16.1

* Tue Apr 23 2019 Konstantin Pavlov <thresh@nginx.com> - 1.16.0-1%{?dist}.ngx
- 1.16.0

* Tue Dec  4 2018 Konstantin Pavlov <thresh@nginx.com> - 1.14.2-1%{?dist}.ngx
- 1.14.2

* Tue Nov  6 2018 Konstantin Pavlov <thresh@nginx.com> - 1.14.1-2%{?dist}.ngx
- 1.14.1
- Fixes CVE-2018-16843
- Fixes CVE-2018-16844
- Fixes CVE-2018-16845

* Tue Apr 17 2018 Konstantin Pavlov <thresh@nginx.com> - 1.14.0-1%{?dist}.ngx
- 1.14.0

* Tue Jul 11 2017 Konstantin Pavlov <thresh@nginx.com> - 1.12.1-1%{?dist}.ngx
- 1.12.1
- Fixes CVE-2017-7529

* Wed Apr 12 2017 Konstantin Pavlov <thresh@nginx.com> - 1.12.0-1%{?dist}.ngx
- 1.12.0

* Tue Jan 31 2017 Konstantin Pavlov <thresh@nginx.com> - 1.10.3-1%{?dist}.ngx
- 1.10.3
- Extended hardening build flags.
- Added check-reload target to init script / systemd service.

* Tue Oct 18 2016 Konstantin Pavlov <thresh@nginx.com> - 1.10.2-1%{?dist}.ngx
- 1.10.2

* Tue May 31 2016 Konstantin Pavlov <thresh@nginx.com> - 1.10.1-1%{?dist}.ngx
- 1.10.1

* Tue Apr 26 2016 Konstantin Pavlov <thresh@nginx.com> - 1.10.0-1%{?dist}.ngx
- 1.10.0

* Tue Jan 26 2016 Konstantin Pavlov <thresh@nginx.com> - 1.8.1-1%{?dist}.ngx
- 1.8.1

* Tue Apr 21 2015 Sergey Budnevitch <sb@nginx.com> - 1.8.0-1%{?dist}.ngx
- 1.8.0

* Tue Apr  7 2015 Sergey Budnevitch <sb@nginx.com> - 1.6.3-1%{?dist}.ngx
- 1.6.3

* Tue Sep 16 2014 Sergey Budnevitch <sb@nginx.com> - 1.6.2-1%{?dist}.ngx
- 1.6.2

* Tue Aug  5 2014 Sergey Budnevitch <sb@nginx.com> - 1.6.1-1%{?dist}.ngx
- 1.6.1
- init-script now returns 0 on stop command if nginx is not running

* Thu Apr 24 2014 Konstantin Pavlov <thresh@nginx.com> - 1.6.0-1%{?dist}.ngx
- 1.6.0
- http-auth-request module added

* Tue Mar 18 2014 Sergey Budnevitch <sb@nginx.com> - 1.4.7-1%{?dist}.ngx
- 1.4.7
- warning added when binary upgrade returns non-zero exit code

* Tue Mar  4 2014 Sergey Budnevitch <sb@nginx.com> - 1.4.6-1%{?dist}.ngx
- 1.4.6

* Tue Feb 11 2014 Konstantin Pavlov <thresh@nginx.com> - 1.4.5-1%{?dist}.ngx
- 1.4.5

* Tue Nov 19 2013 Sergey Budnevitch <sb@nginx.com> - 1.4.4-1%{?dist}.ngx
- 1.4.4

* Tue Oct  8 2013 Sergey Budnevitch <sb@nginx.com> - 1.4.3-1%{?dist}.ngx
- 1.4.3
- init script now honours additional options sourced from /etc/default/nginx

* Wed Jul 17 2013 Sergey Budnevitch <sb@nginx.com> - 1.4.2-1%{?dist}.ngx
- 1.4.2
- dpkg-buildflags options now passed by --with-{cc,ld}-opt

* Mon May  6 2013 Sergey Budnevitch <sb@nginx.com> - 1.4.1-1%{?dist}.ngx
- 1.4.1
- fixed openssl version detection with dash as /bin/sh

* Wed Apr 24 2013 Sergey Budnevitch <sb@nginx.com> - 1.4.0-1%{?dist}.ngx
- 1.4.0
- gunzip module added
- spdy module added if openssl version >= 1.0.1

* Tue Apr  2 2013 Sergey Budnevitch <sb@nginx.com> - 1.2.8-1%{?dist}.ngx
- 1.2.8
- set permissions on default log files at installation

* Tue Feb 12 2013 Sergey Budnevitch <sb@nginx.com> - 1.2.7-1%{?dist}.ngx
- 1.2.7
- excess slash removed from --prefix

* Tue Dec 11 2012 Sergey Budnevitch <sb@nginx.com> - 1.2.6-1%{?dist}.ngx
- 1.2.6

* Tue Nov 13 2012 Sergey Budnevitch <sb@nginx.com> - 1.2.5-1%{?dist}.ngx
- 1.2.5

* Tue Sep 25 2012 Sergey Budnevitch <sb@nginx.com> - 1.2.4-1%{?dist}.ngx
- 1.2.4

* Tue Aug  7 2012 Sergey Budnevitch <sb@nginx.com> - 1.2.3-1%{?dist}.ngx
- 1.2.3

* Tue Jul  3 2012 Sergey Budnevitch <sb@nginx.com> - 1.2.2-1%{?dist}.ngx
- 1.2.2

* Tue Jun  5 2012 Sergey Budnevitch <sb@nginx.com> - 1.2.1-1%{?dist}.ngx
- 1.2.1
- package provides 'httpd' (ticket #158)
- upgrade action added to postinst script
- minor fix in prerm

* Mon Apr 23 2012 Sergey Budnevitch <sb@nginx.com> - 1.2.0-1%{?dist}.ngx
- 1.2.0

* Thu Apr 12 2012 Sergey Budnevitch <sb@nginx.com> - 1.0.15-1%{?dist}.ngx
- 1.0.15

* Thu Mar 22 2012 Sergey Budnevitch <sb@nginx.com> - 1.0.14-2%{?dist}.ngx
- postinst script added to fix error on installation when another

* Thu Mar 15 2012 Sergey Budnevitch <sb@nginx.com> - 1.0.14-1%{?dist}.ngx
- 1.0.14

* Mon Mar  5 2012 Sergey Budnevitch <sb@nginx.com> - 1.0.13-1%{?dist}.ngx
- 1.0.13

* Mon Feb  6 2012 Sergey Budnevitch <sb@nginx.com> - 1.0.12-1%{?dist}.ngx
- 1.0.12
- banner added to install script

* Thu Dec 15 2011 Sergey Budnevitch <sb@nginx.com> - 1.0.11-1%{?dist}.ngx
- 1.0.11
- init script enhancements (thanks to Gena Makhomed)

* Tue Nov 15 2011 Sergey Budnevitch <sb@nginx.com> - 1.0.10-1%{?dist}.ngx
- 1.0.10

* Tue Nov  1 2011 Sergey Budnevitch <sb@nginx.com> - 1.0.9-1%{?dist}.ngx
- 1.0.9
- nginx-debug package added

* Tue Oct 11 2011 Sergey Budnevitch <sb@nginx.com> - 1.0.8-2%{?dist}.ngx
- typo in configure fixed
- upgrade and configtest arguments to init-script added (based on fedora
  one)
- logrotate creates new logfiles with nginx owner

* Sat Oct  1 2011 Sergey Budnevitch <sb@nginx.com> - 1.0.8-1%{?dist}.ngx
- 1.0.8
- built with mp4 module

* Fri Sep 30 2011 Sergey Budnevitch <sb@nginx.com> - 1.0.7-1%{?dist}.ngx
- 1.0.7

* Tue Aug 30 2011 Sergey Budnevitch <sb@nginx.com> - 1.0.6-1%{?dist}.ngx
- 1.0.6
- replace "conf.d/*" config include with "conf.d/*.conf" in default
  nginx.conf

* Thu Aug 11 2011 Sergey Budnevitch <sb@nginx.com> - 1.0.5-1%{?dist}.ngx
- Initial release

