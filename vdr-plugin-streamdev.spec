
%define plugin	streamdev
%define name	vdr-plugin-%plugin
%define version	0.5.0
%define cvsrev	0
%define rel	5

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
rm -rf %{buildroot}
cd server
%vdr_plugin_install
cd ../client
%vdr_plugin_install
cd ..

install -d -m755 %{buildroot}%{vdr_plugin_cfgdir}/%{plugin}-server
install -m755 %plugin-server/externremux.sh %{buildroot}%{vdr_plugin_cfgdir}/%{plugin}-server
install -m644 %plugin-server/streamdevhosts.conf %{buildroot}%{vdr_plugin_cfgdir}/%{plugin}-server

%clean
rm -rf %{buildroot}

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
%dir %{vdr_plugin_cfgdir}/%plugin-server
%config(noreplace) %{vdr_plugin_cfgdir}/%plugin-server/streamdevhosts.conf
%config(noreplace) %{vdr_plugin_cfgdir}/%plugin-server/externremux.sh

%files client -f client/streamdev-client.vdr
%defattr(-,root,root)
%doc README HISTORY CONTRIBUTORS


%changelog
* Sat Oct 02 2010 Anssi Hannula <anssi@mandriva.org> 0.5.0-4mdv2011.0
+ Revision: 582551
- restore configuration files of server package

* Sat Oct 02 2010 Anssi Hannula <anssi@mandriva.org> 0.5.0-3mdv2011.0
+ Revision: 582530
- remove dependencies on removed common subpackage

* Sun Aug 15 2010 Anssi Hannula <anssi@mandriva.org> 0.5.0-2mdv2011.0
+ Revision: 570212
- new stable version 0.5.0
  o config file location has changed
    (streamdevhosts.conf is automatically moved)
  o externremux.sh semantics have changed (see documentation)
- rediff xbmc recording streaming patch
- drop streamdev-common package, it is no longer needed

* Sun Feb 14 2010 Anssi Hannula <anssi@mandriva.org> 0.5.0-0.pre.20100214.1mdv2011.0
+ Revision: 505943
- new snapshot
- add patches from XBMC:
  o send messages to streamdev client (AddCallbackMsg.diff)
  o improve recording streaming (ReplaceRecordingStreaming.patch)
  o add femon support (AddFemonV1.diff)

* Sat Jan 16 2010 Anssi Hannula <anssi@mandriva.org> 0.5.0-0.pre.20100116.1mdv2010.1
+ Revision: 492513
- new snapshot
- drop format-string.patch (applied upstream)

* Tue Jul 28 2009 Anssi Hannula <anssi@mandriva.org> 0.3.4-1.20090715.2mdv2010.0
+ Revision: 401088
- rebuild for new VDR

* Wed Jul 15 2009 Anssi Hannula <anssi@mandriva.org> 0.3.4-1.20090715.1mdv2010.0
+ Revision: 396120
- new snapshot
- drop intcam.patch, remuxpatch.diff, TS-default.patch, applied upstream
- update format-string.patch
- update sysconfig file

* Sat Mar 21 2009 Anssi Hannula <anssi@mandriva.org> 0.3.4-1.20080425.4mdv2009.1
+ Revision: 359782
- fix format strings (format-string.patch)
- rebuild for new vdr

* Sun Sep 07 2008 Anssi Hannula <anssi@mandriva.org> 0.3.4-1.20080425.3mdv2009.0
+ Revision: 282129
- fix externremux.sh permissions (reported by Mikko Kuivaniemi)

* Mon Apr 28 2008 Anssi Hannula <anssi@mandriva.org> 0.3.4-1.20080425.2mdv2009.0
+ Revision: 197885
- replace configdir patch with one from upstream (P1)
- handle remote CA correctly (P2)

* Sat Apr 26 2008 Anssi Hannula <anssi@mandriva.org> 0.3.4-1.20080425.1mdv2009.0
+ Revision: 197726
- new snapshot
- fix non-threadsafe configdir call (P1)
- create streamdev-common package for shared translations
- add urpmi readme file regarding config directory change
- ship externremux.sh

* Sun Mar 02 2008 Anssi Hannula <anssi@mandriva.org> 0.3.3-1.080302.1mdv2008.1
+ Revision: 177717
- new snapshot

* Fri Jan 04 2008 Anssi Hannula <anssi@mandriva.org> 0.3.3-1.071028.3mdv2008.1
+ Revision: 145205
- rebuild for new vdr

  + Olivier Blin <oblin@mandriva.com>
    - restore BuildRoot

  + Thierry Vignaud <tv@mandriva.org>
    - kill re-definition of %%buildroot on Pixel's request

* Mon Oct 29 2007 Anssi Hannula <anssi@mandriva.org> 0.3.3-1.071028.2mdv2008.1
+ Revision: 103215
- rebuild for new vdr

* Sun Oct 28 2007 Anssi Hannula <anssi@mandriva.org> 0.3.3-1.071028.1mdv2008.1
+ Revision: 102880
- use TS by default for HTTP streaming (P0)
- new snapshot
- update URL

* Sun Jul 08 2007 Anssi Hannula <anssi@mandriva.org> 0.3.3-1.070611.4mdv2008.0
+ Revision: 50049
- rebuild for new vdr

* Fri Jun 22 2007 Anssi Hannula <anssi@mandriva.org> 0.3.3-1.070611.3mdv2008.0
+ Revision: 42695
- rebuild due to buildsystem failure
- rebuild for new vdr

* Sun Jun 10 2007 Anssi Hannula <anssi@mandriva.org> 0.3.3-1.070611.1mdv2008.0
+ Revision: 37966
- new snapshot
- drop the patch, applied upstream

* Sat May 05 2007 Anssi Hannula <anssi@mandriva.org> 1.070420.2mdv2008.0-current
+ Revision: 22698
- rebuild for new vdr

* Fri Apr 20 2007 Anssi Hannula <anssi@mandriva.org> 0.3.3-1.070420.1mdv2008.0
+ Revision: 16291
- new snapshot
- patch0: section_filters-0.5.patch by Petri Hintukainen and Rolf Ahrenberg
  (lots of changes, see README.patch for details)
- drop patch2, obsoleted by patch0


* Mon Feb 05 2007 Anssi Hannula <anssi@mandriva.org> 0.3.3-1.070205.1mdv2007.0
+ Revision: 116379
- new snapshot

* Tue Dec 05 2006 Anssi Hannula <anssi@mandriva.org> 0.3.3-1.060823.4mdv2007.1
+ Revision: 90974
- rebuild for new vdr

* Tue Oct 31 2006 Anssi Hannula <anssi@mandriva.org> 0.3.3-1.060823.3mdv2007.1
+ Revision: 74085
- rebuild for new vdr
- Import vdr-plugin-streamdev

* Thu Sep 07 2006 Anssi Hannula <anssi@mandriva.org> 0.3.3-1.060823.2mdv2007.0
- rebuild for new vdr
- use 2-digit year in cvsrev to shorten the rpm name length

* Thu Aug 24 2006 Anssi Hannula <anssi@mandriva.org> 0.3.3-0.20060823.1mdv2007.0
- new snapshot
- stricter abi requires
- drop patch1, upstream
- rediff patch2
- fix replaces in %%prep

* Mon Aug 07 2006 Anssi Hannula <anssi@mandriva.org> 0.3.3-0.20060507.4mdv2007.0
- rebuild for new vdr

* Wed Jul 26 2006 Anssi Hannula <anssi@mandriva.org> 0.3.3-0.20060507.3mdv2007.0
- rebuild for new vdr

* Tue Jun 20 2006 Anssi Hannula <anssi@mandriva.org> 0.3.3-0.20060507.2mdv2007.0
- use _ prefix for system path macros
- rpmbuildupdate friendly

* Sat Jun 10 2006 Anssi Hannula <anssi@mandriva.org> 0.3.3-0.20060507.1mdv2007.0
- initial Mandriva release

