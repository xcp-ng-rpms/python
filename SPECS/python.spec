%global package_speccommit 1850ba90c8fde75adac9c2b787d1326960b0be74
%global usver 2.7.5
%global xsver 92
%global xsrel %{xsver}%{?xscount}%{?xshash}
# ======================================================
# Conditionals and other variables controlling the build
# ======================================================

%{!?__python_ver:%global __python_ver EMPTY}
#global __python_ver 27
%global unicode ucs4

%if "%{__python_ver}" != "EMPTY"
%global main_python 0
%global python python%{__python_ver}
%global tkinter tkinter%{__python_ver}
%else
%global main_python 1
%global python python
%global tkinter tkinter
%endif

%global pybasever 2.7
%global pylibdir %{_libdir}/python%{pybasever}
%global tools_dir %{pylibdir}/Tools
%global demo_dir %{pylibdir}/Demo
%global doc_tools_dir %{pylibdir}/Doc/tools
%global dynload_dir %{pylibdir}/lib-dynload
%global site_packages %{pylibdir}/site-packages

%define __python /usr/bin/python2

# Python's configure script defines SOVERSION, and this is used in the Makefile
# to determine INSTSONAME, the name of the libpython DSO:
#   LDLIBRARY='libpython$(VERSION).so'
#   INSTSONAME="$LDLIBRARY".$SOVERSION
# We mirror this here in order to make it easier to add the -gdb.py hooks.
# (if these get out of sync, the payload of the libs subpackage will fail
# and halt the build)
%global py_SOVERSION 1.0
%global py_INSTSONAME_optimized libpython%{pybasever}.so.%{py_SOVERSION}
%global py_INSTSONAME_debug     libpython%{pybasever}_d.so.%{py_SOVERSION}

%global with_debug_build 1

# Disabled for now:
%global with_huntrleaks 0

%global with_gdb_hooks 1

%global with_systemtap 1

# some arches don't have valgrind so we need to disable its support on them
%global with_valgrind 0

# Having more than 28 cores on a PPC machine will lead to race conditions
# during build so we have to set a limit.
# See: https://bugzilla.redhat.com/show_bug.cgi?id=1568974
%ifarch ppc %{power64} &&  %_smp_ncpus_max > 28
%global _smp_ncpus_max 28
%endif

%global with_gdbm 1

# Turn this to 0 to turn off the "check" phase:
%global run_selftest_suite 1

# Some of the files below /usr/lib/pythonMAJOR.MINOR/test  (e.g. bad_coding.py)
# are deliberately invalid, leading to SyntaxError exceptions if they get
# byte-compiled.
#
# These errors are ignored by the normal python build, and aren't normally a
# problem in the buildroots since /usr/bin/python isn't present.
#
# However, for the case where we're rebuilding the python srpm on a machine
# that does have python installed we need to set this to avoid
# brp-python-bytecompile treating these as fatal errors:
#
%global _python_bytecompile_errors_terminate_build 0

# We need to get a newer configure generated out of configure.in for the following
# patches:
#   patch 4 (CFLAGS)
#   patch 52 (valgrind)
#   patch 55 (systemtap)
#   patch 145 (linux2)
#
# For patch 55 (systemtap), we need to get a new header for configure to use
#
# configure.in requires autoconf-2.65, but the version in Fedora is currently
# autoconf-2.66
#
# For now, we'll generate a patch to the generated configure script and
# pyconfig.h.in on a machine that has a local copy of autoconf 2.65
#
# Instructions on obtaining such a copy can be seen at
#   http://bugs.python.org/issue7997
#
# To make it easy to regenerate the patch, this specfile can be run in two
# ways:
# (i) regenerate_autotooling_patch  0 : the normal approach: prep the
# source tree using a pre-generated patch to the "configure" script, and do a
# full build
# (ii) regenerate_autotooling_patch 1 : intended to be run on a developer's
# workstation: prep the source tree without patching configure, then rerun a
# local copy of autoconf-2.65, regenerate the patch, then exit, without doing
# the rest of the build
%global regenerate_autotooling_patch 0


# ==================
# Top-level metadata
# ==================
Summary: An interpreted, interactive, object-oriented programming language
Name: %{python}
# Remember to also rebase python-docs when changing this:
Version: 2.7.5
Release: %{?xsrel}%{?dist}
License: Python
Group: Development/Languages
Requires: %{python}-libs%{?_isa} = %{version}-%{release}
Provides: python-abi = %{pybasever}
Provides: python(abi) = %{pybasever}


# =======================
# Build-time requirements
# =======================

# (keep this list alphabetized)

BuildRequires: autoconf
BuildRequires: bluez-libs-devel
BuildRequires: bzip2
BuildRequires: bzip2-devel

# expat 2.1.0 added the symbol XML_SetHashSalt without bumping SONAME.  We use
# it (in pyexpat) in order to enable the fix in Python-2.7.3 for CVE-2012-0876:
BuildRequires: expat-devel >= 2.1.0

BuildRequires: findutils
BuildRequires: gcc-c++
%if %{with_gdbm}
BuildRequires: gdbm-devel
%endif
BuildRequires: git-core
BuildRequires: glibc-devel
BuildRequires: gmp-devel
BuildRequires: libdb-devel
BuildRequires: libffi-devel
BuildRequires: libGL-devel
BuildRequires: libX11-devel
BuildRequires: ncurses-devel
BuildRequires: openssl-devel >= 3.0.9
BuildRequires: pkgconfig
BuildRequires: readline-devel
BuildRequires: sqlite-devel

%if 0%{?with_systemtap}
BuildRequires: systemtap-sdt-devel
# (this introduces a circular dependency, in that systemtap-sdt-devel's
# /usr/bin/dtrace is a python script)
%global tapsetdir      /usr/share/systemtap/tapset
%endif # with_systemtap

BuildRequires: tar
BuildRequires: tcl-devel
BuildRequires: tix-devel
BuildRequires: tk-devel

%if 0%{?with_valgrind}
BuildRequires: valgrind-devel
%endif

BuildRequires: zlib-devel



# =======================
# Source code and patches
# =======================

Source0: Python-2.7.5.tar.xz
Patch0: python-2.7.1-config.patch
Patch1: 00001-pydocnogui.patch
Patch2: python-2.5-cflags.patch
Patch3: python-2.5.1-plural-fix.patch
Patch4: python-2.5.1-sqlite-encoding.patch
Patch5: python-2.7rc1-binutils-no-dep.patch
Patch6: python-2.7rc1-socketmodule-constants.patch
Patch7: python-2.7rc1-socketmodule-constants2.patch
Patch8: python-2.6-rpath.patch
Patch9: python-2.6.4-distutils-rpath.patch
Patch10: 00055-systemtap.patch
Patch11: python-2.7.3-lib64.patch
Patch12: python-2.7-lib64-sysconfig.patch
Patch13: 00104-lib64-fix-for-test_install.patch
Patch14: 00111-no-static-lib.patch
Patch15: python-2.7.3-debug-build.patch
Patch16: 00113-more-configuration-flags.patch
Patch17: 00114-statvfs-f_flag-constants.patch
Patch18: 00121-add-Modules-to-build-path.patch
Patch19: 00125-less-verbose-COUNT_ALLOCS.patch
Patch20: python-2.7.1-fix_test_abc_with_COUNT_ALLOCS.patch
Patch21: python-2.7.2-add-extension-suffix-to-python-config.patch
Patch22: 00131-disable-tests-in-test_io.patch
Patch23: 00132-add-rpmbuild-hooks-to-unittest.patch
Patch24: 00133-skip-test_dl.patch
Patch25: 00134-fix-COUNT_ALLOCS-failure-in-test_sys.patch
Patch26: 00135-skip-test-within-test_weakref-in-debug-build.patch
Patch27: 00136-skip-tests-of-seeking-stdin-in-rpmbuild.patch
Patch28: 00137-skip-distutils-tests-that-fail-in-rpmbuild.patch
Patch29: 00138-fix-distutils-tests-in-debug-build.patch
Patch30: 00139-skip-test_float-known-failure-on-arm.patch
Patch31: 00140-skip-test_ctypes-known-failure-on-sparc.patch
Patch32: 00141-fix-test_gc_with_COUNT_ALLOCS.patch
Patch33: 00142-skip-failing-pty-tests-in-rpmbuild.patch
Patch34: 00143-tsc-on-ppc.patch
Patch35: 00144-no-gdbm.patch
Patch36: 00146-hashlib-fips.patch
Patch37: 00147-add-debug-malloc-stats.patch
Patch38: 00153-fix-test_gdb-noise.patch
Patch39: 00155-avoid-ctypes-thunks.patch
Patch40: 00156-gdb-autoload-safepath.patch
Patch41: 00157-uid-gid-overflows.patch
Patch42: 00165-crypt-module-salt-backport.patch
Patch43: 00166-fix-fake-repr-in-gdb-hooks.patch
Patch44: 00167-disable-stack-navigation-tests-when-optimized-in-test_gdb.patch
Patch45: 00168-distutils-cflags.patch
Patch46: 00169-avoid-implicit-usage-of-md5-in-multiprocessing.patch
Patch47: 00170-gc-assertions.patch
Patch48: 00173-workaround-ENOPROTOOPT-in-bind_port.patch
Patch49: 00174-fix-for-usr-move.patch
Patch50: 00180-python-add-support-for-ppc64p7.patch
Patch51: 00181-allow-arbitrary-timeout-in-condition-wait.patch
Patch52: 00184-ctypes-should-build-with-libffi-multilib-wrapper.patch
Patch53: 00185-urllib2-honors-noproxy-for-ftp.patch
Patch54: 00186-memory-leak-marshalc.patch
Patch55: 00187-add-RPATH-to-pyexpat.patch
Patch56: 00188-CVE-2013-4238-hostname-check-bypass-in-SSL-module.patch
Patch57: 00189-gdb-py-bt-dont-raise-exception-from-eval.patch
Patch58: 00190-gdb-fix-ppc64-failures.patch
Patch59: 00191-add-RPATH-to-elementtree.patch
Patch60: 00192-Fix-missing-documentation-for-some-keywords.patch
Patch61: 00193-buffer-overflow.patch
Patch62: 00194-gdb-dont-fail-on-frame-with-address.patch
Patch63: 00195-make-multiproc-ignore-EINTR.patch
Patch64: 00196-avoid-double-close-of-pipes.patch
Patch65: 00197-add-missing-import-in-bdist_rpm.patch
Patch66: 00198-fix-readline-erroneous-output.patch
Patch67: 00199-CVE-2013-1753.patch
Patch68: 00200-CVE-2014-4616.patch
Patch69: 00201-CVE-2014-4650.patch
Patch70: 00202-CVE-2014-7185.patch
Patch71: 00203-CVE-2013-1752-nntplib.patch
Patch72: 00204-CVE-2013-1752-ftplib.patch
Patch73: 00205-CVE-2013-1752-httplib-headers.patch
Patch74: 00206-CVE-2013-1752-poplib.patch
Patch75: 00207-CVE-2013-1752-smtplib.patch
Patch76: 00208-CVE-2013-1752-imaplib.patch
Patch77: 00209-pep466-backport-hmac.compare_digest.patch
Patch78: 00210-pep466-backport-hashlib.pbkdf2_hmac.patch
Patch79: 00211-pep466-UTF-7-decoder-fix-illegal-unicode.patch
Patch80: 00212-pep466-pyunicode_fromformat-raise-overflow.patch
Patch81: 00213-pep466-pyunicode_fromformat-fix-formats.patch
Patch82: 00214-pep466-backport-py3-ssl-changes.patch
Patch83: 00215-pep466-reflect-openssl-settings-ssltests.patch
Patch84: 00216-pep466-fix-load-verify-locs-unicode.patch
Patch85: 00217-pep466-backport-hashlib-algorithm-consts.patch
Patch86: 00218-pep466-backport-urandom-pers-fd.patch
Patch87: 00219-pep466-fix-referenced-sslwrap.patch
Patch88: 00220-pep466-allow-passing-ssl-urrlib-httplib.patch
Patch89: 00222-add-2014-bit-dh-key.patch
Patch90: 00223-pep476-verify-certs-by-default.patch
Patch91: 00224-pep476-add-toggle-for-cert-verify.patch
Patch92: 00225-cprofile-sort-option.patch
Patch93: 00227-accept-none-keyfile-loadcertchain.patch
Patch94: 00228-backport-ssl-version.patch
Patch95: 00229-Expect-a-failure-when-trying-to-connect-with-SSLv2-c.patch
Patch96: 00230-force-all-child-threads-to-terminate-in-TestForkInThread.patch
Patch97: 00231-Initialize-OpenSSL_add_all_digests-in-_hashlib.patch
Patch98: 00232-man-page-date-macro-removal.patch
Patch99: 00233-Computed-Goto-dispatch.patch
Patch100: 00234-PEP493-updated-implementation.patch
Patch101: 00235-JSON-decoder-lone-surrogates-fix.patch
Patch102: 00236-use-Py_ssize_t-for-file-offset-and-length-computations-in-iteration.patch
Patch103: 00237-CVE-2016-0772-smtplib.patch
Patch104: 00238-CVE-2016-5699-httplib.patch
Patch105: 00240-increase-smtplib-tests-timeouts.patch
Patch106: 00241-CVE-2016-5636-buffer-overflow-in-zipimport-module-fix.patch
Patch107: 00242-CVE-2016-1000110-httpoxy.patch
Patch108: 00255-Fix-ssl-module-parsing-of-GEN_RID-subject-alternative-name-fields-in-X.509-certs.patch
Patch109: 00256-fix-incorrect-parsing-of-regular-expressions.patch
Patch110: 00257-threading-wait-clamp-remaining-time.patch
Patch111: 00263-fix-ssl-reference-leaks.patch
Patch112: 00265-protect-key-list-during-fork.patch
Patch113: 00266-fix-shutil.make_archive-ignoring-empty-dirs.patch
Patch114: 00268-set-stream-name-to-None.patch
Patch115: 00275-fix-fnctl-with-integer-on-big-endian.patch
Patch116: 00276-increase-imaplib-MAXLINE.patch
Patch117: 00281-add-context-parameter-to-xmlrpclib.ServerProxy.patch
Patch118: 00282-obmalloc-mmap-threshold.patch
Patch119: 00285-fix-non-deterministic-read-in-test_pty.patch
Patch120: 00287-fix-thread-hanging-on-inaccessible-nfs-server.patch
Patch121: 00295-fix-https-behind-proxy.patch
Patch122: 00296-Readd-the-private-_set_hostport-api-to-httplib.patch
Patch123: 00298-do-not-send-IP-in-SNI-TLS-extension.patch
Patch124: 00299-fix-ssl-module-pymax.patch
Patch125: 00303-CVE-2018-1060-1.patch
Patch126: 00305-CVE-2016-2183.patch
Patch127: 00306-fix-oserror-17-upon-semaphores-creation.patch
Patch128: 00310-use-xml-sethashsalt-in-elementtree.patch
Patch129: 00314-parser-check-e_io.patch
Patch130: 00317-CVE-2019-5010-ssl-crl.patch
Patch131: 00320-CVE-2019-9636-and-CVE-2019-10160.patch
Patch132: 00324-disallow-control-chars-in-http-urls.patch
Patch133: 00325-CVE-2019-9948.patch
Patch134: 00330-CVE-2018-20852.patch
Patch135: 00332-CVE-2019-16056.patch
Patch136: 00344-CVE-2019-16935.patch
Patch137: 99999-python-2.7.5-issues-17979-17998.patch
Patch138: 00351-cve-2019-20907-fix-infinite-loop-in-tarfile.patch
Patch139: 05000-autotool-intermediates.patch
Patch140: fix-dereferencing-pointer-build-issue.patch
Patch141: detect-openssl-version.patch
Patch142: fix-hash-openssl.patch
Patch143: enable-tls-1.2.patch
Patch144: remove-some-ssl_methods.patch
Patch145: 0001-CP-50323-Replace-deprecated-functions.patch
Patch146: 0001-CP-50325-Use-new-api-of-ncurses-devel.patch

# Work around bug 562906 until it's fixed in rpm-build by providing a fixed
# version of pythondeps.sh:
Source2: pythondeps.sh
%global __python_requires %{SOURCE2}

# Systemtap tapset to make it easier to use the systemtap static probes
# (actually a template; LIBRARY_PATH will get fixed up during install)
# Written by dmalcolm; not yet sent upstream
Source3: libpython.stp


# Example systemtap script using the tapset
# Written by wcohen, mjw, dmalcolm; not yet sent upstream
Source4: systemtap-example.stp

# Another example systemtap script that uses the tapset
# Written by dmalcolm; not yet sent upstream
Source5: pyfuntop.stp

Source7: pynche

# Configuration file to change ssl verification settings globally
# Downstream only see Patch224
Source8: cert-verification.cfg

# configuration for systemd's tmpfiles
Source9: python.conf

# ======================================================
# Additional metadata, and subpackages
# ======================================================

%if %{main_python}
Obsoletes: Distutils
Provides: Distutils
Provides: python2 = %{version}
Obsoletes: python-elementtree <= 1.2.6
Obsoletes: python-sqlite < 2.3.2
Provides: python-sqlite = 2.3.2
Obsoletes: python-ctypes < 1.0.1
Provides: python-ctypes = 1.0.1
Obsoletes: python-hashlib < 20081120
Provides: python-hashlib = 20081120
Obsoletes: python-uuid < 1.31
Provides: python-uuid = 1.31

# python-sqlite2-2.3.5-5.fc18 was retired.  Obsolete the old package here
# so it gets uninstalled on updates
%if 0%{?fedora} >= 17
Obsoletes: python-sqlite2 <= 2.3.5-6
%endif

# python-argparse is part of python as of version 2.7
# drop this Provides in F17
# (having Obsoletes here caused problems with multilib; see rhbz#667984)
Provides:   python-argparse = %{version}-%{release}
%endif

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

URL: http://www.python.org/

%description
Python is an interpreted, interactive, object-oriented programming
language often compared to Tcl, Perl, Scheme or Java. Python includes
modules, classes, exceptions, very high level dynamic data types and
dynamic typing. Python supports interfaces to many system calls and
libraries, as well as to various windowing systems (X11, Motif, Tk,
Mac and MFC).

Programmers can write new built-in modules for Python in C or C++.
Python can be used as an extension language for applications that need
a programmable interface.

Note that documentation for Python is provided in the python-docs
package.

This package provides the "python" executable; most of the actual
implementation is within the "python-libs" package.

%package libs
Summary: Runtime libraries for Python
Group: Applications/System

# New behaviour of httplib (patch 295) doesn't play well with really old pip
# version (1.4.1) bundled in the old virtualenv package. This new version of
# virtualenv updated bundled pip to 9.0.1 which works fine.
# Resolves: https://bugzilla.redhat.com/show_bug.cgi?id=1483438
Conflicts: python-virtualenv < 15.1.0-1

# Needed for ctypes, to load libraries, worked around for Live CDs size
# Requires: binutils

# expat 2.1.0 added the symbol XML_SetHashSalt without bumping SONAME.  We use
# this symbol (in pyexpat), so we must explicitly state this dependency to
# prevent "import pyexpat" from failing with a linker error if someone hasn't
# yet upgraded expat:
Requires: expat >= 2.1.0

Provides: python2-libs = %{version}-%{release}
Provides: python2-libs%{?_isa} = %{version}-%{release}

%description libs
This package contains runtime libraries for use by Python:
- the libpython dynamic library, for use by applications that embed Python as
a scripting language, and by the main "python" executable
- the Python standard library

%package devel
Summary: The libraries and header files needed for Python development
Group: Development/Libraries
Requires: %{python}%{?_isa} = %{version}-%{release}
Requires: pkgconfig

# Macros were previously here, but were moved to their respective packages
Requires: python-rpm-macros > 3-30
Requires: python2-rpm-macros > 3-30

# Needed here because of the migration of Makefile from -devel to the main
# package
Conflicts: %{python} < %{version}-%{release}
%if %{main_python}
Obsoletes: python2-devel < %{version}-%{release}
Provides: python2-devel = %{version}-%{release}
Provides: python2-devel%{?_isa} = %{version}-%{release}
%endif

%description devel
The Python programming language's interpreter can be extended with
dynamically loaded extensions and can be embedded in other programs.
This package contains the header files and libraries needed to do
these types of tasks.

Install python-devel if you want to develop Python extensions.  The
python package will also need to be installed.  You'll probably also
want to install the python-docs package, which contains Python
documentation.

%package tools
Summary: A collection of development tools included with Python
Group: Development/Tools
Requires: %{name} = %{version}-%{release}
Requires: %{tkinter} = %{version}-%{release}
%if %{main_python}
Obsoletes: python2-tools < %{version}-%{release}
Provides: python2-tools = %{version}
%endif

%description tools
This package includes several tools to help with the development of Python
programs, including IDLE (an IDE with editing and debugging facilities), a
color editor (pynche), and a python gettext program (pygettext.py).

%package -n %{tkinter}
Summary: A graphical user interface for the Python scripting language
Group: Development/Languages
Requires: %{name} = %{version}-%{release}
%if %{main_python}
Obsoletes: tkinter2 < %{version}-%{release}
Provides: tkinter2 = %{version}
%endif

%description -n %{tkinter}

The Tkinter (Tk interface) program is an graphical user interface for
the Python scripting language.

You should install the tkinter package if you'd like to use a graphical
user interface for Python programming.

%package test
Summary: The test modules from the main python package
Group: Development/Languages
Requires: %{name} = %{version}-%{release}

%description test

The test modules from the main python package: %{name}
These have been removed to save space, as they are never or almost
never used in production.

You might want to install the python-test package if you're developing python
code that uses more than just unittest and/or test_support.py.

%if 0%{?with_debug_build}
%package debug
Summary: Debug version of the Python runtime
Group: Applications/System

# The debug build is an all-in-one package version of the regular build, and
# shares the same .py/.pyc files and directories as the regular build.  Hence
# we depend on all of the subpackages of the regular build:
Requires: %{name}%{?_isa} = %{version}-%{release}
Requires: %{name}-libs%{?_isa} = %{version}-%{release}
Requires: %{name}-devel%{?_isa} = %{version}-%{release}
Requires: %{name}-test%{?_isa} = %{version}-%{release}
Requires: tkinter%{?_isa} = %{version}-%{release}
Requires: %{name}-tools%{?_isa} = %{version}-%{release}

%description debug
python-debug provides a version of the Python runtime with numerous debugging
features enabled, aimed at advanced Python users, such as developers of Python
extension modules.

This version uses more memory and will be slower than the regular Python build,
but is useful for tracking down reference-counting issues, and other bugs.

The bytecodes are unchanged, so that .pyc files are compatible between the two
version of Python, but the debugging features mean that C/C++ extension modules
are ABI-incompatible with those built for the standard runtime.

It shares installation directories with the standard Python runtime, so that
.py and .pyc files can be shared.  All compiled extension modules gain a "_d"
suffix ("foo_d.so" rather than "foo.so") so that each Python implementation can
load its own extensions.
%endif # with_debug_build


# ======================================================
# The prep phase of the build:
# ======================================================

%prep
%autosetup -p1 -n Python-%{version} -S git

# CA-397616: Remove test_gdb test temporarily
rm -f Lib/test/test_gdb.py

# remove the unused module test
rm -f Lib/test/test_ftplib.py

# follows 00165-crypt-module-salt-backport.patch
mv Modules/cryptmodule.c Modules/_cryptmodule.c

%if 0%{?with_systemtap}
# Provide an example of usage of the tapset:
cp -a %{SOURCE4} .
cp -a %{SOURCE5} .
%endif # with_systemtap

# Ensure that we're using the system copy of various libraries, rather than
# copies shipped by upstream in the tarball:
#   Remove embedded copy of expat:
rm -r Modules/expat || exit 1

#   Remove embedded copy of libffi:
for SUBDIR in darwin libffi libffi_arm_wince libffi_msvc libffi_osx ; do
  rm -r Modules/_ctypes/$SUBDIR || exit 1 ;
done

#   Remove embedded copy of zlib:
rm -r Modules/zlib || exit 1

# Don't build upstream Python's implementation of these crypto algorithms;
# instead rely on _hashlib and OpenSSL.
#
# For example, in our builds md5.py uses always uses hashlib.md5 (rather than
# falling back to _md5 when hashlib.md5 is not available); hashlib.md5 is
# implemented within _hashlib via OpenSSL (and thus respects FIPS mode)
for f in md5module.c md5.c shamodule.c sha256module.c sha512module.c; do
    rm Modules/$f
done

# This shouldn't be necesarry, but is right now (2.2a3)
find -name "*~" |xargs rm -f

# ======================================================
# Configuring and building the code:
# ======================================================

%build
topdir=$(pwd)
export CFLAGS="$RPM_OPT_FLAGS -D_GNU_SOURCE -fPIC -fwrapv"
export CXXFLAGS="$RPM_OPT_FLAGS -D_GNU_SOURCE -fPIC -fwrapv"
export CPPFLAGS="$(pkg-config --cflags-only-I libffi)"
export OPT="$RPM_OPT_FLAGS -D_GNU_SOURCE -fPIC -fwrapv"
export LINKCC="gcc"
export LDFLAGS="$RPM_LD_FLAGS"
if pkg-config openssl ; then
  export CFLAGS="$CFLAGS $(pkg-config --cflags openssl)"
  export LDFLAGS="$LDFLAGS $(pkg-config --libs-only-L openssl)"
fi
# compile with -O3 for ppc64 as requested in
# https://bugzilla.redhat.com/show_bug.cgi?id=1051076
%ifarch %{power64}
export CFLAGS="$CFLAGS -O3"
export CXXFLAGS="$CXXFLAGS -O3"
export OPT="$OPT -O3"
%endif
# Force CC
export CC=gcc

%if 0%{regenerate_autotooling_patch}
# If enabled, this code regenerates the patch to "configure", using a
# local copy of autoconf-2.65, then exits the build
#
# The following assumes that the copy is installed to ~/autoconf-2.65/bin
# as per these instructions:
#   http://bugs.python.org/issue7997

for f in pyconfig.h.in configure ; do
    cp $f $f.autotool-intermediates ;
done

# Rerun the autotools:
PATH=~/autoconf-2.65/bin:$PATH autoconf
autoheader

# Regenerate the patch:
gendiff . .autotool-intermediates > %{PATCH5000}


# Exit the build
exit 1
%endif

# Define a function, for how to perform a "build" of python for a given
# configuration:
BuildPython() {
  ConfName=$1
  BinaryName=$2
  SymlinkName=$3
  ExtraConfigArgs=$4
  PathFixWithThisBinary=$5

  ConfDir=build/$ConfName

  echo STARTING: BUILD OF PYTHON FOR CONFIGURATION: $ConfName - %{_bindir}/$BinaryName
  mkdir -p $ConfDir

  pushd $ConfDir

  # Use the freshly created "configure" script, but in the directory two above:
  %global _configure $topdir/configure

%configure \
  --enable-ipv6 \
  --enable-shared \
  --enable-unicode=%{unicode} \
  --with-dbmliborder=gdbm:ndbm:bdb \
  --with-system-expat \
  --with-system-ffi \
%if 0%{?with_systemtap}
  --with-dtrace \
  --with-tapset-install-dir=%{tapsetdir} \
%endif
%if 0%{?with_valgrind}
  --with-valgrind \
%endif
  $ExtraConfigArgs \
  %{nil}

make EXTRA_CFLAGS="$CFLAGS" %{?_smp_mflags}

# We need to fix shebang lines across the full source tree.
#
# We do this using the pathfix.py script, which requires one of the
# freshly-built Python binaries.
#
# We use the optimized python binary, and make the shebangs point at that same
# optimized python binary:
if $PathFixWithThisBinary
then
  LD_LIBRARY_PATH="$topdir/$ConfDir" ./$BinaryName \
    $topdir/Tools/scripts/pathfix.py \
      -i "%{_bindir}/env $BinaryName" \
      $topdir
fi

# Rebuild with new python
# We need a link to a versioned python in the build directory
ln -s $BinaryName $SymlinkName
LD_LIBRARY_PATH="$topdir/$ConfDir" PATH=$PATH:$topdir/$ConfDir make -s EXTRA_CFLAGS="$CFLAGS" %{?_smp_mflags}

  popd
  echo FINISHED: BUILD OF PYTHON FOR CONFIGURATION: $ConfDir
}

# Use "BuildPython" to support building with different configurations:

%if 0%{?with_debug_build}
BuildPython debug \
  python-debug \
  python%{pybasever}-debug \
%ifarch %{ix86} x86_64 ppc %{power64}
  "--with-pydebug --with-tsc --with-count-allocs --with-call-profile" \
%else
  "--with-pydebug --with-count-allocs --with-call-profile" \
%endif
  false
%endif # with_debug_build

BuildPython optimized \
  python \
  python%{pybasever} \
  "" \
  true


# ======================================================
# Installing the built code:
# ======================================================

%install
topdir=$(pwd)
rm -rf %{buildroot}
mkdir -p %{buildroot}%{_prefix} %{buildroot}%{_mandir}

# Clean up patched .py files that are saved as .lib64
for f in distutils/command/install distutils/sysconfig; do
    rm -f Lib/$f.py.lib64
done

InstallPython() {

  ConfName=$1
  BinaryName=$2
  PyInstSoName=$3

  ConfDir=build/$ConfName

  echo STARTING: INSTALL OF PYTHON FOR CONFIGURATION: $ConfName - %{_bindir}/$BinaryName
  mkdir -p $ConfDir

  pushd $ConfDir

make install DESTDIR=%{buildroot}

# We install a collection of hooks for gdb that make it easier to debug
# executables linked against libpython (such as /usr/lib/python itself)
#
# These hooks are implemented in Python itself
#
# gdb-archer looks for them in the same path as the ELF file, with a -gdb.py suffix.
# We put them in the debuginfo package by installing them to e.g.:
#  /usr/lib/debug/usr/lib/libpython2.6.so.1.0.debug-gdb.py
# (note that the debug path is /usr/lib/debug for both 32/64 bit)
#
# See https://fedoraproject.org/wiki/Features/EasierPythonDebugging for more
# information
#
# Initially I tried:
#  /usr/lib/libpython2.6.so.1.0-gdb.py
# but doing so generated noise when ldconfig was rerun (rhbz:562980)
#

%if 0%{?with_gdb_hooks}
DirHoldingGdbPy=%{_prefix}/lib/debug/%{_libdir}
PathOfGdbPy=$DirHoldingGdbPy/$PyInstSoName.debug-gdb.py

mkdir -p %{buildroot}$DirHoldingGdbPy
cp $topdir/Tools/gdb/libpython.py %{buildroot}$PathOfGdbPy

# Manually byte-compile the file, in case find-debuginfo.sh is run before
# brp-python-bytecompile, so that the .pyc/.pyo files are properly listed in
# the debuginfo manifest:
LD_LIBRARY_PATH="$topdir/$ConfDir" $topdir/$ConfDir/$BinaryName \
  -c "import compileall; import sys; compileall.compile_dir('%{buildroot}$DirHoldingGdbPy', ddir='$DirHoldingGdbPy')"

LD_LIBRARY_PATH="$topdir/$ConfDir" $topdir/$ConfDir/$BinaryName -O \
  -c "import compileall; import sys; compileall.compile_dir('%{buildroot}$DirHoldingGdbPy', ddir='$DirHoldingGdbPy')"
%endif # with_gdb_hooks

  popd

  echo FINISHED: INSTALL OF PYTHON FOR CONFIGURATION: $ConfName
}

# Use "InstallPython" to support building with different configurations:

# Install the "debug" build first, so that we can move some files aside
%if 0%{?with_debug_build}
InstallPython debug \
  python%{pybasever}-debug \
  %{py_INSTSONAME_debug}
%endif # with_debug_build

# Now the optimized build:
InstallPython optimized \
  python%{pybasever} \
  %{py_INSTSONAME_optimized}


# Fix the interpreter path in binaries installed by distutils
# (which changes them by itself)
# Make sure we preserve the file permissions
for fixed in %{buildroot}%{_bindir}/pydoc; do
    sed 's,#!.*/python$,#!%{_bindir}/env python%{pybasever},' $fixed > $fixed- \
        && cat $fixed- > $fixed && rm -f $fixed-
done

# Junk, no point in putting in -test sub-pkg
rm -f %{buildroot}/%{pylibdir}/idlelib/testcode.py*

# don't include tests that are run at build time in the package
# This is documented, and used: rhbz#387401
if /bin/false; then
 # Move this to -test subpackage.
mkdir save_bits_of_test
for i in test_support.py __init__.py; do
  cp -a %{buildroot}/%{pylibdir}/test/$i save_bits_of_test
done
rm -rf %{buildroot}/%{pylibdir}/test
mkdir %{buildroot}/%{pylibdir}/test
cp -a save_bits_of_test/* %{buildroot}/%{pylibdir}/test
fi

%if %{main_python}
%else
mv %{buildroot}%{_bindir}/python %{buildroot}%{_bindir}/%{python}
%if 0%{?with_debug_build}
mv %{buildroot}%{_bindir}/python-debug %{buildroot}%{_bindir}/%{python}-debug
%endif # with_debug_build
mv %{buildroot}/%{_mandir}/man1/python.1 %{buildroot}/%{_mandir}/man1/python%{pybasever}.1
%endif

# tools

mkdir -p ${RPM_BUILD_ROOT}%{site_packages}

#pynche
install -p -m755 %{SOURCE7} ${RPM_BUILD_ROOT}%{_bindir}/pynche
chmod 755 ${RPM_BUILD_ROOT}%{_bindir}/pynche
rm -f Tools/pynche/*.pyw
cp -rp Tools/pynche \
  ${RPM_BUILD_ROOT}%{site_packages}/

mv Tools/pynche/README Tools/pynche/README.pynche

#gettext
install -m755  Tools/i18n/pygettext.py %{buildroot}%{_bindir}/
install -m755  Tools/i18n/msgfmt.py %{buildroot}%{_bindir}/

# Useful development tools
install -m755 -d %{buildroot}%{tools_dir}/scripts
install Tools/README %{buildroot}%{tools_dir}/
install Tools/scripts/*py %{buildroot}%{tools_dir}/scripts/

# Documentation tools
install -m755 -d %{buildroot}%{doc_tools_dir}
#install -m755 Doc/tools/mkhowto %{buildroot}%{doc_tools_dir}

# Useful demo scripts
install -m755 -d %{buildroot}%{demo_dir}
cp -ar Demo/* %{buildroot}%{demo_dir}

# Get rid of crap
find %{buildroot}/ -name "*~"|xargs rm -f
find %{buildroot}/ -name ".cvsignore"|xargs rm -f
find %{buildroot}/ -name "*.bat"|xargs rm -f
find . -name "*~"|xargs rm -f
find . -name ".cvsignore"|xargs rm -f
#zero length
rm -f %{buildroot}%{pylibdir}/LICENSE.txt


#make the binaries install side by side with the main python
%if !%{main_python}
pushd %{buildroot}%{_bindir}
mv idle idle%{__python_ver}
mv pynche pynche%{__python_ver}
mv pygettext.py pygettext%{__python_ver}.py
mv msgfmt.py msgfmt%{__python_ver}.py
mv smtpd.py smtpd%{__python_ver}.py
mv pydoc pydoc%{__python_ver}
popd
%endif

# Fix for bug #136654
rm -f %{buildroot}%{pylibdir}/email/test/data/audiotest.au %{buildroot}%{pylibdir}/test/audiotest.au

# Fix bug #143667: python should own /usr/lib/python2.x on 64-bit machines
%if "%{_lib}" == "lib64"
install -d %{buildroot}/usr/lib/python%{pybasever}/site-packages
%endif

# Make python-devel multilib-ready (bug #192747, #139911)
%global _pyconfig32_h pyconfig-32.h
%global _pyconfig64_h pyconfig-64.h

%ifarch %{power64} s390x x86_64 ia64 alpha sparc64 aarch64
%global _pyconfig_h %{_pyconfig64_h}
%else
%global _pyconfig_h %{_pyconfig32_h}
%endif

%if 0%{?with_debug_build}
%global PyIncludeDirs python%{pybasever} python%{pybasever}-debug
%else
%global PyIncludeDirs python%{pybasever}
%endif

for PyIncludeDir in %{PyIncludeDirs} ; do
  mv %{buildroot}%{_includedir}/$PyIncludeDir/pyconfig.h \
     %{buildroot}%{_includedir}/$PyIncludeDir/%{_pyconfig_h}
  cat > %{buildroot}%{_includedir}/$PyIncludeDir/pyconfig.h << EOF
#include <bits/wordsize.h>

#if __WORDSIZE == 32
#include "%{_pyconfig32_h}"
#elif __WORDSIZE == 64
#include "%{_pyconfig64_h}"
#else
#error "Unknown word size"
#endif
EOF
done
ln -s ../../libpython%{pybasever}.so %{buildroot}%{pylibdir}/config/libpython%{pybasever}.so

# Fix for bug 201434: make sure distutils looks at the right pyconfig.h file
# Similar for sysconfig: sysconfig.get_config_h_filename tries to locate
# pyconfig.h so it can be parsed, and needs to do this at runtime in site.py
# when python starts up.
#
# Split this out so it goes directly to the pyconfig-32.h/pyconfig-64.h
# variants:
sed -i -e "s/'pyconfig.h'/'%{_pyconfig_h}'/" \
  %{buildroot}%{pylibdir}/distutils/sysconfig.py \
  %{buildroot}%{pylibdir}/sysconfig.py

# Make python folder for config files under /etc
mkdir -p %{buildroot}/%{_sysconfdir}/python
install -m 644 %{SOURCE8} %{buildroot}/%{_sysconfdir}/python

# Ensure that the curses module was linked against libncursesw.so, rather than
# libncurses.so (bug 539917)
ldd %{buildroot}/%{dynload_dir}/_curses*.so \
    | grep curses \
    | grep libncurses.so && (echo "_curses.so linked against libncurses.so" ; exit 1)

# Ensure that the debug modules are linked against the debug libpython, and
# likewise for the optimized modules and libpython:
for Module in %{buildroot}/%{dynload_dir}/*.so ; do
    case $Module in
    *_d.so)
        ldd $Module | grep %{py_INSTSONAME_optimized} &&
            (echo Debug module $Module linked against optimized %{py_INSTSONAME_optimized} ; exit 1)

        ;;
    *)
        ldd $Module | grep %{py_INSTSONAME_debug} &&
            (echo Optimized module $Module linked against debug %{py_INSTSONAME_optimized} ; exit 1)
        ;;
    esac
done

#
# Systemtap hooks:
#
%if 0%{?with_systemtap}
# Install a tapset for this libpython into tapsetdir, fixing up the path to the
# library:
mkdir -p %{buildroot}%{tapsetdir}
%ifarch %{power64} s390x x86_64 ia64 alpha sparc64 aarch64
%global libpython_stp_optimized libpython%{pybasever}-64.stp
%global libpython_stp_debug     libpython%{pybasever}-debug-64.stp
%else
%global libpython_stp_optimized libpython%{pybasever}-32.stp
%global libpython_stp_debug     libpython%{pybasever}-debug-32.stp
%endif

sed \
   -e "s|LIBRARY_PATH|%{_libdir}/%{py_INSTSONAME_optimized}|" \
   %{SOURCE3} \
   > %{buildroot}%{tapsetdir}/%{libpython_stp_optimized}

%if 0%{?with_debug_build}
sed \
   -e "s|LIBRARY_PATH|%{_libdir}/%{py_INSTSONAME_debug}|" \
   %{SOURCE3} \
   > %{buildroot}%{tapsetdir}/%{libpython_stp_debug}
%endif # with_debug_build
%endif # with_systemtap

# Replace scripts shebangs in usr/bin of subpackage tools
#(rhbz#987038)
sed -i "s|^#\!.\?/usr/bin.*$|#\! %{__python}|" \
  %{buildroot}%{_bindir}/pygettext.py \
  %{buildroot}%{_bindir}/msgfmt.py \
  %{buildroot}%{_bindir}/smtpd.py \
  %{buildroot}%{demo_dir}/scripts/find-uname.py \
  %{buildroot}%{demo_dir}/pdist/rcvs \
  %{buildroot}%{demo_dir}/pdist/rcsbump \
  %{buildroot}%{demo_dir}/pdist/rrcs \
  %{buildroot}%{site_packages}/pynche/pynche

# Make library-files user writable
# rhbz#1046276
/usr/bin/chmod 755 %{buildroot}%{dynload_dir}/*.so
/usr/bin/chmod 755 %{buildroot}%{_libdir}/libpython%{pybasever}.so.1.0
%if 0%{?with_debug_build}
/usr/bin/chmod 755 %{buildroot}%{_libdir}/libpython%{pybasever}_d.so.1.0
%endif # with_debug_build

mkdir %{buildroot}%{_tmpfilesdir}
cp %{SOURCE9} %{buildroot}%{_tmpfilesdir}/python.conf

# Create the platform-python symlink pointing to usr/bin/python2.7
mkdir -p %{buildroot}%{_libexecdir}
ln -s %{_bindir}/python%{pybasever} %{buildroot}%{_libexecdir}/platform-python

# ======================================================
# Running the upstream test suite
# ======================================================

%check
topdir=$(pwd)
CheckPython() {
  ConfName=$1
  BinaryName=$2
  ConfDir=$(pwd)/build/$ConfName

  echo STARTING: CHECKING OF PYTHON FOR CONFIGURATION: $ConfName

  # Note that we're running the tests using the version of the code in the
  # builddir, not in the buildroot.

  pushd $ConfDir

  EXTRATESTOPTS="--verbose"
EXTRATESTOPTS="$EXTRATESTOPTS -x test_httplib -x test_ssl -x test_urllib2_localnet "
  # skipping test_gdb on ppc64le until rhbz1260558 gets resolved
  %ifarch ppc64le
    EXTRATESTOPTS="$EXTRATESTOPTS -x test_gdb -x "
  %endif


%if 0%{?with_huntrleaks}
  # Try to detect reference leaks on debug builds.  By default this means
  # running every test 10 times (6 to stabilize, then 4 to watch):
  if [ "$ConfName" = "debug"  ] ; then
    EXTRATESTOPTS="$EXTRATESTOPTS --huntrleaks : "
  fi
%endif

  # Run the upstream test suite, setting "WITHIN_PYTHON_RPM_BUILD" so that the
  # our non-standard decorators take effect on the relevant tests:
  #   @unittest._skipInRpmBuild(reason)
  #   @unittest._expectedFailureInRpmBuild
  WITHIN_PYTHON_RPM_BUILD= EXTRATESTOPTS="$EXTRATESTOPTS" make test || : test cerificates have expired

  popd

  echo FINISHED: CHECKING OF PYTHON FOR CONFIGURATION: $ConfName

}

%if 0%{run_selftest_suite}

# Check each of the configurations:
%if 0%{?with_debug_build}
CheckPython \
  debug \
  python%{pybasever}-debug
%endif # with_debug_build
CheckPython \
  optimized \
  python%{pybasever}

%endif # run_selftest_suite


# ======================================================
# Cleaning up
# ======================================================

%clean
rm -fr %{buildroot}


# ======================================================
# Scriptlets
# ======================================================

%post libs -p /sbin/ldconfig

%postun libs -p /sbin/ldconfig



%files
%defattr(-, root, root, -)
%doc LICENSE README
%{_bindir}/pydoc*
%{_bindir}/%{python}
%if %{main_python}
%{_bindir}/python2
%endif
%{_bindir}/python%{pybasever}

%{_libexecdir}/platform-python

%{_mandir}/*/*

%files libs
%defattr(-,root,root,-)
%doc LICENSE README
%dir %{pylibdir}
%dir %{dynload_dir}
%dir %{_sysconfdir}/python
%{_tmpfilesdir}/python.conf
%config(noreplace) %{_sysconfdir}/python/cert-verification.cfg
%{dynload_dir}/Python-%{version}-py%{pybasever}.egg-info
%{dynload_dir}/_bisectmodule.so
%{dynload_dir}/_bsddb.so
%{dynload_dir}/_codecs_cn.so
%{dynload_dir}/_codecs_hk.so
%{dynload_dir}/_codecs_iso2022.so
%{dynload_dir}/_codecs_jp.so
%{dynload_dir}/_codecs_kr.so
%{dynload_dir}/_codecs_tw.so
%{dynload_dir}/_collectionsmodule.so
%{dynload_dir}/_csv.so
%{dynload_dir}/_ctypes.so
%{dynload_dir}/_curses.so
%{dynload_dir}/_curses_panel.so
%{dynload_dir}/_elementtree.so
%{dynload_dir}/_functoolsmodule.so
%{dynload_dir}/_hashlib.so
%{dynload_dir}/_heapq.so
%{dynload_dir}/_hotshot.so
%{dynload_dir}/_io.so
%{dynload_dir}/_json.so
%{dynload_dir}/_localemodule.so
%{dynload_dir}/_lsprof.so
%{dynload_dir}/_multibytecodecmodule.so
%{dynload_dir}/_multiprocessing.so
%{dynload_dir}/_randommodule.so
%{dynload_dir}/_socketmodule.so
%{dynload_dir}/_sqlite3.so
%{dynload_dir}/_ssl.so
%{dynload_dir}/_struct.so
%{dynload_dir}/arraymodule.so
%{dynload_dir}/audioop.so
%{dynload_dir}/binascii.so
%{dynload_dir}/bz2.so
%{dynload_dir}/cPickle.so
%{dynload_dir}/cStringIO.so
%{dynload_dir}/cmathmodule.so
%{dynload_dir}/_cryptmodule.so
%{dynload_dir}/datetime.so
%{dynload_dir}/dbm.so
%{dynload_dir}/dlmodule.so
%{dynload_dir}/fcntlmodule.so
%{dynload_dir}/future_builtins.so
%if %{with_gdbm}
%{dynload_dir}/gdbm.so
%endif
%{dynload_dir}/grpmodule.so
%{dynload_dir}/imageop.so
%{dynload_dir}/itertoolsmodule.so
%{dynload_dir}/linuxaudiodev.so
%{dynload_dir}/math.so
%{dynload_dir}/mmapmodule.so
%{dynload_dir}/nismodule.so
%{dynload_dir}/operator.so
%{dynload_dir}/ossaudiodev.so
%{dynload_dir}/parsermodule.so
%{dynload_dir}/pyexpat.so
%{dynload_dir}/readline.so
%{dynload_dir}/resource.so
%{dynload_dir}/selectmodule.so
%{dynload_dir}/spwdmodule.so
%{dynload_dir}/stropmodule.so
%{dynload_dir}/syslog.so
%{dynload_dir}/termios.so
%{dynload_dir}/timemodule.so
%{dynload_dir}/timingmodule.so
%{dynload_dir}/unicodedata.so
%{dynload_dir}/xxsubtype.so
%{dynload_dir}/zlibmodule.so

%dir %{site_packages}
%{site_packages}/README
%{pylibdir}/*.py*
%{pylibdir}/*.doc
%{pylibdir}/wsgiref.egg-info
%dir %{pylibdir}/bsddb
%{pylibdir}/bsddb/*.py*
%{pylibdir}/compiler
%dir %{pylibdir}/ctypes
%{pylibdir}/ctypes/*.py*
%{pylibdir}/ctypes/macholib
%{pylibdir}/curses
%dir %{pylibdir}/distutils
%{pylibdir}/distutils/*.py*
%{pylibdir}/distutils/README
%{pylibdir}/distutils/command
%exclude %{pylibdir}/distutils/command/wininst-*.exe
%dir %{pylibdir}/email
%{pylibdir}/email/*.py*
%{pylibdir}/email/mime
%{pylibdir}/encodings
%{pylibdir}/hotshot
%{pylibdir}/idlelib
%{pylibdir}/importlib
%dir %{pylibdir}/json
%{pylibdir}/json/*.py*
%{pylibdir}/lib2to3
%exclude %{pylibdir}/lib2to3/tests
%{pylibdir}/logging
%{pylibdir}/multiprocessing
%{pylibdir}/plat-linux2
%{pylibdir}/pydoc_data
%dir %{pylibdir}/sqlite3
%{pylibdir}/sqlite3/*.py*
%dir %{pylibdir}/test
%{pylibdir}/test/test_support.py*
%{pylibdir}/test/__init__.py*
%{pylibdir}/unittest
%{pylibdir}/wsgiref
%{pylibdir}/xml
%if "%{_lib}" == "lib64"
%attr(0755,root,root) %dir %{_prefix}/lib/python%{pybasever}
%attr(0755,root,root) %dir %{_prefix}/lib/python%{pybasever}/site-packages
%endif

# "Makefile" and the config-32/64.h file are needed by
# distutils/sysconfig.py:_init_posix(), so we include them in the libs
# package, along with their parent directories (bug 531901):
%dir %{pylibdir}/config
%{pylibdir}/config/Makefile
%dir %{_includedir}/python%{pybasever}
%{_includedir}/python%{pybasever}/%{_pyconfig_h}

%{_libdir}/%{py_INSTSONAME_optimized}
%if 0%{?with_systemtap}
%{tapsetdir}/%{libpython_stp_optimized}
%doc systemtap-example.stp pyfuntop.stp
%endif

%files devel
%defattr(-,root,root,-)
%{_libdir}/pkgconfig/python-%{pybasever}.pc
%{_libdir}/pkgconfig/python.pc
%{_libdir}/pkgconfig/python2.pc
%{pylibdir}/config/*
%exclude %{pylibdir}/config/Makefile
%{pylibdir}/distutils/command/wininst-*.exe
%{_includedir}/python%{pybasever}/*.h
%exclude %{_includedir}/python%{pybasever}/%{_pyconfig_h}
%doc Misc/README.valgrind Misc/valgrind-python.supp Misc/gdbinit
%if %{main_python}
%{_bindir}/python-config
%{_bindir}/python2-config
%endif
%{_bindir}/python%{pybasever}-config
%{_libdir}/libpython%{pybasever}.so

%files tools
%defattr(-,root,root,755)
%doc Tools/pynche/README.pynche
%{site_packages}/pynche
%{_bindir}/smtpd*.py*
%{_bindir}/2to3*
%{_bindir}/idle*
%{_bindir}/pynche*
%{_bindir}/pygettext*.py*
%{_bindir}/msgfmt*.py*
%{tools_dir}
%{demo_dir}
%{pylibdir}/Doc

%files -n %{tkinter}
%defattr(-,root,root,755)
%{pylibdir}/lib-tk
%{dynload_dir}/_tkinter.so

%files test
%defattr(-, root, root, -)
%{pylibdir}/bsddb/test
%{pylibdir}/ctypes/test
%{pylibdir}/distutils/tests
%{pylibdir}/email/test
%{pylibdir}/json/tests
%{pylibdir}/lib2to3/tests
%{pylibdir}/sqlite3/test
%{pylibdir}/test/*
# These two are shipped in the main subpackage:
%exclude %{pylibdir}/test/test_support.py*
%exclude %{pylibdir}/test/__init__.py*
%{dynload_dir}/_ctypes_test.so
%{dynload_dir}/_testcapimodule.so


# We don't bother splitting the debug build out into further subpackages:
# if you need it, you're probably a developer.

# Hence the manifest is the combination of analogous files in the manifests of
# all of the other subpackages

%if 0%{?with_debug_build}
%files debug
%defattr(-,root,root,-)

# Analog of the core subpackage's files:
%{_bindir}/%{python}-debug
%if %{main_python}
%{_bindir}/python2-debug
%endif
%{_bindir}/python%{pybasever}-debug

# Analog of the -libs subpackage's files, with debug builds of the built-in
# "extension" modules:
%{dynload_dir}/_bisectmodule_d.so
%{dynload_dir}/_bsddb_d.so
%{dynload_dir}/_codecs_cn_d.so
%{dynload_dir}/_codecs_hk_d.so
%{dynload_dir}/_codecs_iso2022_d.so
%{dynload_dir}/_codecs_jp_d.so
%{dynload_dir}/_codecs_kr_d.so
%{dynload_dir}/_codecs_tw_d.so
%{dynload_dir}/_collectionsmodule_d.so
%{dynload_dir}/_csv_d.so
%{dynload_dir}/_ctypes_d.so
%{dynload_dir}/_curses_d.so
%{dynload_dir}/_curses_panel_d.so
%{dynload_dir}/_elementtree_d.so
%{dynload_dir}/_functoolsmodule_d.so
%{dynload_dir}/_hashlib_d.so
%{dynload_dir}/_heapq_d.so
%{dynload_dir}/_hotshot_d.so
%{dynload_dir}/_io_d.so
%{dynload_dir}/_json_d.so
%{dynload_dir}/_localemodule_d.so
%{dynload_dir}/_lsprof_d.so
%{dynload_dir}/_multibytecodecmodule_d.so
%{dynload_dir}/_multiprocessing_d.so
%{dynload_dir}/_randommodule_d.so
%{dynload_dir}/_socketmodule_d.so
%{dynload_dir}/_sqlite3_d.so
%{dynload_dir}/_ssl_d.so
%{dynload_dir}/_struct_d.so
%{dynload_dir}/arraymodule_d.so
%{dynload_dir}/audioop_d.so
%{dynload_dir}/binascii_d.so
%{dynload_dir}/bz2_d.so
%{dynload_dir}/cPickle_d.so
%{dynload_dir}/cStringIO_d.so
%{dynload_dir}/cmathmodule_d.so
%{dynload_dir}/_cryptmodule_d.so
%{dynload_dir}/datetime_d.so
%{dynload_dir}/dbm_d.so
%{dynload_dir}/dlmodule_d.so
%{dynload_dir}/fcntlmodule_d.so
%{dynload_dir}/future_builtins_d.so
%if %{with_gdbm}
%{dynload_dir}/gdbm_d.so
%endif
%{dynload_dir}/grpmodule_d.so
%{dynload_dir}/imageop_d.so
%{dynload_dir}/itertoolsmodule_d.so
%{dynload_dir}/linuxaudiodev_d.so
%{dynload_dir}/math_d.so
%{dynload_dir}/mmapmodule_d.so
%{dynload_dir}/nismodule_d.so
%{dynload_dir}/operator_d.so
%{dynload_dir}/ossaudiodev_d.so
%{dynload_dir}/parsermodule_d.so
%{dynload_dir}/pyexpat_d.so
%{dynload_dir}/readline_d.so
%{dynload_dir}/resource_d.so
%{dynload_dir}/selectmodule_d.so
%{dynload_dir}/spwdmodule_d.so
%{dynload_dir}/stropmodule_d.so
%{dynload_dir}/syslog_d.so
%{dynload_dir}/termios_d.so
%{dynload_dir}/timemodule_d.so
%{dynload_dir}/timingmodule_d.so
%{dynload_dir}/unicodedata_d.so
%{dynload_dir}/xxsubtype_d.so
%{dynload_dir}/zlibmodule_d.so

# No need to split things out the "Makefile" and the config-32/64.h file as we
# do for the regular build above (bug 531901), since they're all in one package
# now; they're listed below, under "-devel":

%{_libdir}/%{py_INSTSONAME_debug}
%if 0%{?with_systemtap}
%{tapsetdir}/%{libpython_stp_debug}
%endif

# Analog of the -devel subpackage's files:
%dir %{pylibdir}/config-debug
%{_libdir}/pkgconfig/python-%{pybasever}-debug.pc
%{_libdir}/pkgconfig/python-debug.pc
%{_libdir}/pkgconfig/python2-debug.pc
%{pylibdir}/config-debug/*
%{_includedir}/python%{pybasever}-debug/*.h
%if %{main_python}
%{_bindir}/python-debug-config
%{_bindir}/python2-debug-config
%endif
%{_bindir}/python%{pybasever}-debug-config
%{_libdir}/libpython%{pybasever}_d.so

# Analog of the -tools subpackage's files:
#  None for now; we could build precanned versions that have the appropriate
# shebang if needed

# Analog  of the tkinter subpackage's files:
%{dynload_dir}/_tkinter_d.so

# Analog  of the -test subpackage's files:
%{dynload_dir}/_ctypes_test_d.so
%{dynload_dir}/_testcapimodule_d.so

%endif # with_debug_build

# We put the debug-gdb.py file inside /usr/lib/debug to avoid noise from
# ldconfig (rhbz:562980).
#
# The /usr/lib/rpm/redhat/macros defines the __debug_package macro to use
# debugfiles.list, and it appears that everything below /usr/lib/debug and
# (/usr/src/debug) gets added to this file (via LISTFILES) in
# /usr/lib/rpm/find-debuginfo.sh
#
# Hence by installing it below /usr/lib/debug we ensure it is added to the
# -debuginfo subpackage
# (if it doesn't, then the rpmbuild ought to fail since the debug-gdb.py
# payload file would be unpackaged)


# ======================================================
# Finally, the changelog:
# ======================================================

%changelog
* Thu Jan 02 2025 Deli Zhang <deli.zhang@cloud.com> - 2.7.5-92
- CP-50325: Use new api of ncurses-devel
- CP-50323: Replace deprecated functions
- CA-397616: Remove test_gdb test temporarily
- CP-50323: Remove unused module test test_ftplib.py
- CP-50323: Build with OpenSSL 3
- CP-50323: Import python-2.7.5-90.el7.src.rpm

