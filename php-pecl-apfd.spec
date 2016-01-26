# centos/sclo spec file for php-pecl-apfd, from:
#
# remirepo spec file for php-pecl-apfd
# with SCL compatibility, from:
#
# Fedora spec file for php-pecl-apfd
#
# Copyright (c) 2015-2016 Remi Collet
# License: CC-BY-SA
# http://creativecommons.org/licenses/by-sa/4.0/
#
# Please, preserve the changelog entries
#
%if 0%{?scl:1}
%if "%{scl}" == "rh-php56"
%global sub_prefix sclo-php56-
%else
%global sub_prefix sclo-%{scl_prefix}
%endif
%endif

%{?scl:          %scl_package        php-pecl-apfd}
%{!?php_inidir:  %global php_inidir  %{_sysconfdir}/php.d}
%{!?__pecl:      %global __pecl      %{_bindir}/pecl}
%{!?__php:       %global __php       %{_bindir}/php}

%global pecl_name  apfd
%global with_tests 0%{!?_without_tests:1}
%if "%{php_version}" < "5.6"
%global ini_name   %{pecl_name}.ini
%else
%global ini_name   40-%{pecl_name}.ini
%endif
#global prever     RC1

Summary:        Always Populate Form Data
Name:           %{?sub_prefix}php-pecl-%{pecl_name}
Version:        1.0.1
Release:        1%{?dist}
License:        BSD
Group:          Development/Languages
URL:            http://pecl.php.net/package/%{pecl_name}
Source0:        http://pecl.php.net/get/%{pecl_name}-%{version}%{?prever}.tgz

BuildRequires:  %{?scl_prefix}php-devel > 5.3
BuildRequires:  %{?scl_prefix}php-pear

Requires:       %{?scl_prefix}php(zend-abi) = %{php_zend_api}
Requires:       %{?scl_prefix}php(api) = %{php_core_api}

Provides:       %{?scl_prefix}php-%{pecl_name} = %{version}
Provides:       %{?scl_prefix}php-%{pecl_name}%{?_isa} = %{version}
Provides:       %{?scl_prefix}php-pecl(%{pecl_name}) = %{version}
Provides:       %{?scl_prefix}php-pecl(%{pecl_name})%{?_isa} = %{version}
Provides:       %{?scl_prefix}php-pecl-%{pecl_name} = %{version}
Provides:       %{?scl_prefix}php-pecl-%{pecl_name}%{?_isa} = %{version}
# Split off pecl/http
Conflicts:      %{?scl_prefix}php-pecl(http) < 2.4

%if 0%{?fedora} < 20 && 0%{?rhel} < 7
# Filter shared private
%{?filter_provides_in: %filter_provides_in %{_libdir}/.*\.so$}
%{?filter_setup}
%endif


%description
This tiny extension lets PHP's post handler parse `multipart/form-data` and
`application/x-www-form-urlencoded` (or any other customly registered form data
handler, like "json_post") without regard to the request's request method.

This extension does not provide any INI entries, constants, functions or classes.

Package built for PHP %(%{__php} -r 'echo PHP_MAJOR_VERSION.".".PHP_MINOR_VERSION;')%{?scl: as Software Collection (%{scl} by %{?scl_vendor}%{!?scl_vendor:rh})}.


%prep
%setup -q -c
mv %{pecl_name}-%{version}%{?prever} NTS

# Don't install/register tests
sed -e 's/role="test"/role="src"/' -i package.xml

cd NTS
# Sanity check, really often broken
extver=$(sed -n '/#define PHP_APFD_VERSION/{s/.* "//;s/".*$//;p}' php_apfd.h)
if test "x${extver}" != "x%{version}%{?prever}"; then
   : Error: Upstream extension version is ${extver}, expecting %{version}%{?prever}.
   exit 1
fi
cd ..

# Create configuration file
cat << 'EOF' | tee %{ini_name}
; Enable '%{summary}' extension module
extension=%{pecl_name}.so
EOF


%build
cd NTS
%{_bindir}/phpize
%configure \
    --enable-apfd \
    --with-php-config=%{_bindir}/php-config
make %{?_smp_mflags}


%install
make -C NTS install INSTALL_ROOT=%{buildroot}

# install config file
install -D -m 644 %{ini_name} %{buildroot}%{php_inidir}/%{ini_name}

# Install XML package description
install -D -m 644 package.xml %{buildroot}%{pecl_xmldir}/%{name}.xml

# Documentation
for i in $(grep 'role="doc"' package.xml | sed -e 's/^.*name="//;s/".*$//')
do install -Dpm 644 NTS/$i %{buildroot}%{pecl_docdir}/%{pecl_name}/$i
done


# when pear installed alone, after us
%triggerin -- %{?scl_prefix}php-pear
if [ -x %{__pecl} ] ; then
    %{pecl_install} %{pecl_xmldir}/%{name}.xml >/dev/null || :
fi

# posttrans as pear can be installed after us
%posttrans
if [ -x %{__pecl} ] ; then
    %{pecl_install} %{pecl_xmldir}/%{name}.xml >/dev/null || :
fi

%postun
if [ $1 -eq 0 -a -x %{__pecl} ] ; then
    %{pecl_uninstall} %{pecl_name} >/dev/null || :
fi


%check
cd NTS
: Minimal load test for NTS extension
%{__php} --no-php-ini \
    --define extension=%{buildroot}%{php_extdir}/%{pecl_name}.so \
    --modules | grep %{pecl_name}

%if %{with_tests}
: Upstream test suite  for NTS extension
TEST_PHP_EXECUTABLE=%{__php} \
TEST_PHP_ARGS="-n -d extension=$PWD/modules/%{pecl_name}.so" \
NO_INTERACTION=1 \
REPORT_EXIT_STATUS=1 \
%{__php} -n run-tests.php --show-diff
%endif


%files
%doc %{pecl_docdir}/%{pecl_name}
%{pecl_xmldir}/%{name}.xml
%config(noreplace) %{php_inidir}/%{ini_name}
%{php_extdir}/%{pecl_name}.so


%changelog
* Tue Jan 26 2016 Remi Collet <remi@fedoraproject.org> - 1.0.1-1
- cleanup for SCLo build

* Tue Oct 13 2015 Remi Collet <remi@fedoraproject.org> - 1.0.1-5
- rebuild for PHP 7.0.0RC5 new API version

* Fri Sep 18 2015 Remi Collet <remi@fedoraproject.org> - 1.0.1-4
- F23 rebuild with rh_layout

* Wed Jul 22 2015 Remi Collet <remi@fedoraproject.org> - 1.0.1-3
- rebuild against php 7.0.0beta2

* Sun Jun 21 2015 Remi Collet <remi@fedoraproject.org> - 1.0.1-2
- allow build against rh-php56 (as more-php56)
- drop runtime dependency on pear, new scriptlets

* Sat Apr 25 2015 Remi Collet <remi@fedoraproject.org> - 1.0.1-1
- Update to 1.0.1 (stable)

* Wed Mar 18 2015 Remi Collet <remi@fedoraproject.org> - 1.0.0-1
- Update to 1.0.0 (stable)

* Tue Mar 10 2015 Remi Collet <remi@fedoraproject.org> - 1.0.0-0.1.RC1
- Update to 1.0.0RC1

* Sat Feb 14 2015 Remi Collet <remi@fedoraproject.org> - 1.0.0-0
- initial package, for upcoming version 1.0.0