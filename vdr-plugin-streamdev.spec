
%define plugin	streamdev
%define name	vdr-plugin-%plugin
%define version	0.5.0
%define cvsrev	0
%define rel	2

%if %cvsrev
%define release	%mkrel 0.pre.%cvsrev.%rel
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
Source:		http://streamdev.vdr-developer.org/releases/vdr-%plugin-%version.tgz
%endif

# From XBMC
Patch0:		streamdev-cvs100210-ReplaceRecordingStreaming.patch
Patch1:		streamdev-cvs221109-AddCallbackMsg.diff
Patch2:		streamdev-cvs221109-AddFemonV1.diff

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

%prep
%if %cvsrev
%setup -q -n %plugin
find -type d -name CVS -print0 | xargs -0 rm -rf
%else
%setup -q -n %plugin-%version
%endif
%patch0 -p1
%patch1 -p1
%patch2 -p1
cd server
%vdr_plugin_prep
cd ../client
%vdr_plugin_prep
cd ..

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

cat > README.0.5.0-1.upgrade.urpmi <<EOF
The config file location of streamdev has changed from
/var/lib/vdr/config/plugins/streamdev
to
/var/lib/vdr/config/plugins/streamdev-server.
streamdevhosts.conf has been automatically moved unless there was a conflict.
externremux.sh is not moved automatically as there has been a slight change
in the syntax (it has to provide HTTP headers).
EOF

%build
%vdr_plugin_build

%install
rm -rf %{buildroot}
cd server
%vdr_plugin_install
cd ../client
%vdr_plugin_install
cd ..

install -d -m755 %{buildroot}%{_vdr_plugin_cfgdir}/%{plugin}-server
install -m755 %plugin-server/externremux.sh %{buildroot}%{_vdr_plugin_cfgdir}/%{plugin}-server
install -m644 %plugin-server/streamdevhosts.conf %{buildroot}%{_vdr_plugin_cfgdir}/%{plugin}-server

%clean
rm -rf %{buildroot}

%pre server
if [ $1 = 2 ] && ! [ -e %{_vdr_plugin_cfgdir}/%{plugin}-server ] && [ -e %{_vdr_plugin_cfgdir}/%{plugin} ]; then
	mkdir -p %{_vdr_plugin_cfgdir}/%{plugin}-server
	touch %{_vdr_plugin_cfgdir}/%{plugin}-server/mdv-050-migration
fi

%post server
if [ $1 = 2 ] && [ -e %{_vdr_plugin_cfgdir}/%{plugin}-server/mdv-050-migration ]; then
	mv -vf %{_vdr_plugin_cfgdir}/%{plugin}/streamdevhosts.conf %{_vdr_plugin_cfgdir}/%{plugin}-server/streamdevhosts.conf
	rm -f %{_vdr_plugin_cfgdir}/%{plugin}-server/mdv-050-migration
fi
%vdr_plugin_post %plugin-server

%postun server
%vdr_plugin_postun %plugin-server

%post client
%vdr_plugin_post %plugin-client

%postun client
%vdr_plugin_postun %plugin-client

%files server -f server/streamdev-server.vdr
%defattr(-,root,root)
%doc README HISTORY CONTRIBUTORS PROTOCOL README.*.upgrade.urpmi
%dir %{_vdr_plugin_cfgdir}/%plugin-server
%config(noreplace) %{_vdr_plugin_cfgdir}/%plugin-server/streamdevhosts.conf
%config(noreplace) %{_vdr_plugin_cfgdir}/%plugin-server/externremux.sh

%files client -f client/streamdev-client.vdr
%defattr(-,root,root)
%doc README HISTORY CONTRIBUTORS
