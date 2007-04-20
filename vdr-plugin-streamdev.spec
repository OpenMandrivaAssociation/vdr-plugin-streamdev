
%define plugin	streamdev
%define name	vdr-plugin-%plugin
%define version	0.3.3
%define cvsrev	20%shortrev
%define shortrev	070420
%define rel	1
%define release	%mkrel 1.%shortrev.%rel

Summary:	VDR plugin: streamdev
Name:		%name
Version:	%version
Release:	%release
Group:		Video
License:	GPL
URL:		http://www.magoa.net/linux/

# From streamdev @ :pserver:anoncvs@vdr-developer.org:/var/cvsroot
Source:		vdr-%plugin-%cvsrev.tar.bz2
Source1:	http://phivdr.dyndns.org/vdr/vdr-streamdev-patches/README
Patch0:		http://phivdr.dyndns.org/vdr/vdr-streamdev-patches/section_filters-0.5.patch

BuildRoot:	%{_tmppath}/%{name}-buildroot
BuildRequires:	vdr-devel >= 1.4.1-6

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
%setup -q -n %plugin
%patch0 -p0

cp %SOURCE1 README.patch

perl -pi -e 's/^CFLAGS =/MOREFLAGS =/' libdvbmpeg/Makefile
sed -i 's/$(CFLAGS)/$(MOREFLAGS) $(CFLAGS)/' libdvbmpeg/Makefile

sed -i 's,STREAMERBUFSIZE MEGABYTE(4),STREAMERBUFSIZE MEGABYTE(16),' server/streamer.h

%build
%vdr_plugin_build

%install
rm -rf %{buildroot}

%vdr_plugin_install

install -d -m755 %{buildroot}%{_vdr_plugin_cfgdir}
install -m644 streamdevhosts.conf.example 	%{buildroot}%{_vdr_plugin_cfgdir}/streamdevhosts.conf

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
%doc README* HISTORY CONTRIBUTORS PROTOCOL
%config(noreplace) %{_vdr_plugin_cfgdir}/streamdevhosts.conf

%files client -f streamdev-client.vdr
%defattr(-,root,root)
%doc README* HISTORY CONTRIBUTORS


