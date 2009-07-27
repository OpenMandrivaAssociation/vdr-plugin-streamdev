
%define plugin	streamdev
%define name	vdr-plugin-%plugin
%define version	0.3.4
%define cvsrev	20090715
%define rel	2

%if %cvsrev
%define release	%mkrel 1.%cvsrev.%rel
%else
%define release	%mkrel %rel
%endif

Summary:	VDR plugin: streamdev
Name:		%name
Version:	%version
Release:	%release
Group:		Video
License:	GPL
URL:		http://streamdev.vdr-developer.org/

%if %cvsrev
# From streamdev @ :pserver:anoncvs@vdr-developer.org:/var/cvsroot
Source:		vdr-%plugin-%cvsrev.tar.xz
%else
Source:		vdr-%plugin-%version.tgz
%endif

Patch1:		streamdev-format-string.patch
BuildRoot:	%{_tmppath}/%{name}-buildroot
BuildRequires:	vdr-devel >= 1.6.0

%description
This PlugIn is a VDR implementation of the VTP (Video Transfer Protocol,
see file PROTOCOL) and a basic HTTP Streaming Protocol.

It consists of a server and a client part, but both parts are compiled together
with the PlugIn source, but appear as separate PlugIns to VDR.

%package server
Summary:	VDR plugin: VDR Streaming Server
Group:		Video
Requires:	vdr-abi = %vdr_abi
Requires:	%plugin-common >= %version-%release
Requires(post):	%plugin-common >= %version-%release

%description server
This PlugIn is a VDR implementation of the VTP (Video Transfer Protocol,
see file PROTOCOL) and a basic HTTP Streaming Protocol.

The server part acts as a Receiver-Device and works transparently in the
background within your running VDR. It can serve multiple clients and it can
distribute multiple input streams (i.e. from multiple DVB-cards) to multiple
clients using the native VTP protocol (for VDR-clients), or using the HTTP
protocol supporting clients such as XINE, MPlayer and so on. With XMMS or
WinAMP, you can also listen to radio channels over a HTTP connection.

%package client
Summary:	VDR plugin: VTP Streaming Client
Group:		Video
Requires:	vdr-abi = %vdr_abi
Requires:	%plugin-common >= %version-%release
Requires(post):	%plugin-common >= %version-%release

%description client
This PlugIn is a VDR implementation of the VTP (Video Transfer Protocol,
see file PROTOCOL) and a basic HTTP Streaming Protocol.

The client part acts as a full Input Device, so it can be used in conjunction
with a DXR3-Card, XINE, SoftDevice or others to act as a working VDR
installation without any DVB-Hardware including EPG-Handling.

%package -n %plugin-common
Summary:	Streamdev translation files
Group:		Video

%description -n %plugin-common
Streamdev translation files.

%prep
%if %cvsrev
%setup -q -n %plugin
find -type d -name CVS -print0 | xargs -0 rm -rf
%else
%setup -q -n %plugin-%version
%endif
%patch1 -p0
%vdr_plugin_prep

perl -pi -e 's/^CFLAGS =/MOREFLAGS =/' libdvbmpeg/Makefile
sed -i 's/$(CFLAGS)/$(MOREFLAGS) $(CFLAGS)/' libdvbmpeg/Makefile

%vdr_plugin_params_begin %plugin-server
# Credentials for HTTP authentication, in format "LOGIN:PASSWORD".
# Credentials are required when connecting from a host not listed in
# streamdevhosts.conf. The default (i.e. no credentials set below) is to
# not allow connection from such hosts at all.
var=AUTH
param=--auth=AUTH
# Define an external command for remuxing
var=REMUXER
param=--remux=REMUXER
%vdr_plugin_params_end

cat > README.0.3.4.upgrade.urpmi <<EOF
The config file location of streamdev has changed. In the default hierarchy,
this means that the files have been moved from /var/lib/vdr/config/plugins
to /var/lib/vdr/config/plugins/streamdev.
EOF

%build
%vdr_plugin_build

%install
rm -rf %{buildroot}

%vdr_plugin_install

install -d -m755 %{buildroot}%{_vdr_plugin_cfgdir}/%{plugin}
install -m755 %plugin/externremux.sh %{buildroot}%{_vdr_plugin_cfgdir}/%{plugin}
install -m644 %plugin/streamdevhosts.conf %{buildroot}%{_vdr_plugin_cfgdir}/%{plugin}

%find_lang vdr-%plugin

%clean
rm -rf %{buildroot}

%post server
%vdr_plugin_post %plugin-server

%postun server
%vdr_plugin_postun %plugin-server

%post client
%vdr_plugin_post %plugin-client

%postun client
%vdr_plugin_postun %plugin-client

%files server -f streamdev-server.vdr
%defattr(-,root,root)
%doc README HISTORY CONTRIBUTORS PROTOCOL README.0.3.4.upgrade.urpmi
%dir %{_vdr_plugin_cfgdir}/%plugin
%config(noreplace) %{_vdr_plugin_cfgdir}/%plugin/streamdevhosts.conf
%config(noreplace) %{_vdr_plugin_cfgdir}/%plugin/externremux.sh

%files client -f streamdev-client.vdr
%defattr(-,root,root)
%doc README HISTORY CONTRIBUTORS

%files -n %plugin-common -f vdr-streamdev.lang
%defattr(-,root,root)
