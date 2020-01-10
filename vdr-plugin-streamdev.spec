%define plugin	streamdev
%define snap	0

Summary:	VDR plugin: streamdev
Name:		vdr-plugin-%plugin
Version:	0.6.0
%if %snap
Release:	0.%snap.1
%else
Release:	1
%endif
Group:		Video
# Several .c files cause GPLv2+, others are GPL+
License:	GPLv2+
URL:		http://streamdev.vdr-developer.org/

%if %snap
# git://projects.vdr-developer.org/vdr-plugin-streamdev.git
# git archive --prefix streamdev/ master | xz > vdr-streamdev-git20120225.tar.xz
Source:		vdr-%plugin-git%snap.tar.xz
%else
Source:		http://streamdev.vdr-developer.org/releases/vdr-%plugin-%{version}.tgz
%endif
# The default writerbuffer seems to be either too small for high-bitrate
# streams or buffer-full situation is handled wrongly.
# I suspect the latter. TODO: investigate
# -Anssi 10/2013
# same for streamerbuffer
# -Anssi 11/2014
Patch0:		streamdev-buffers-size.patch
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

%description client
This PlugIn is a VDR implementation of the VTP (Video Transfer Protocol,
see file PROTOCOL) and a basic HTTP Streaming Protocol.

The client part acts as a full Input Device, so it can be used in conjunction
with a DXR3-Card, XINE, SoftDevice or others to act as a working VDR
installation without any DVB-Hardware including EPG-Handling.

%prep
%if %snap
%setup -q -n %plugin
%else
%setup -q -n %plugin-%{version}
%endif
%autopatch -p1
cd server
%vdr_plugin_prep
cd ../client
%vdr_plugin_prep
cd ..

perl -pi -e 's/^CFLAGS =/MOREFLAGS =/' libdvbmpeg/Makefile
sed -i 's/$(CFLAGS)/$(MOREFLAGS) $(CFLAGS)/' libdvbmpeg/Makefile

cd server
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
cd ..

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
cd server

%vdr_plugin_install
cd ../client

%vdr_plugin_install
cd ..

install -d -m755 %{buildroot}%{vdr_plugin_cfgdir}/%{plugin}-server
install -m755 %plugin-server/externremux.sh %{buildroot}%{vdr_plugin_cfgdir}/%{plugin}-server
install -m644 %plugin-server/streamdevhosts.conf %{buildroot}%{vdr_plugin_cfgdir}/%{plugin}-server

%pre server
if [ $1 = 2 ] && ! [ -e %{vdr_plugin_cfgdir}/%{plugin}-server ] && [ -e %{vdr_plugin_cfgdir}/%{plugin} ]; then
	mkdir -p %{vdr_plugin_cfgdir}/%{plugin}-server
	touch %{vdr_plugin_cfgdir}/%{plugin}-server/mdv-050-migration
fi

%post server
if [ $1 = 2 ] && [ -e %{vdr_plugin_cfgdir}/%{plugin}-server/mdv-050-migration ]; then
	mv -vf %{vdr_plugin_cfgdir}/%{plugin}/streamdevhosts.conf %{vdr_plugin_cfgdir}/%{plugin}-server/streamdevhosts.conf
	rm -f %{vdr_plugin_cfgdir}/%{plugin}-server/mdv-050-migration
fi

%files server -f server/streamdev-server.vdr
%doc README HISTORY CONTRIBUTORS PROTOCOL README.*.upgrade.urpmi
%dir %{vdr_plugin_cfgdir}/%plugin-server
%config(noreplace) %{vdr_plugin_cfgdir}/%plugin-server/streamdevhosts.conf
%config(noreplace) %{vdr_plugin_cfgdir}/%plugin-server/externremux.sh

%files client -f client/streamdev-client.vdr
%doc README HISTORY CONTRIBUTORS


