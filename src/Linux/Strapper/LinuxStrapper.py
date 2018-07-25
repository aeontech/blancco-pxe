import os
import abc
import sys
import uuid
from shutil import copy
from .. import net
from ... import log
from .. import systemd
from .. import sysctl
from ..dialog import dialog

class LinuxStrapper(object):
    firewall = None
    corp_int = None
    _pxe_int = None

    def __init__(self, systemd, firewall_daemon):
        self.systemd  = systemd
        self.firewall = firewall_daemon

    def checkenv(self):
        # Check for sudo privs
        if os.getuid() != 0:
            log.warn('Requires elevation!')
            self._elevate()

        # Ensure we are definitly admin
        if os.getuid() != 0:
            raise EnvironmentError("Not admin - could not elevate privileges!")

    @abc.abstractmethod
    def install_packages(self):
        pass

    def configure_packages(self):
        log.info("Configuring System...")
        self._configure_sysctl()
        self._configure_interface_names()
        self._configure_interfaces()
        self._configure_firewall()

        log.info("Configuring Packages...")
        self._configure_tftpd()
        self._configure_nginx()
        self._configure_dhcpd()

    def configure_startup(self):
        for service in ['nginx', 'xinetd', 'dhcpd']:
            self.systemd.enable("%s.service" % service)
            self.systemd.start ("%s.service" % service)

    def _elevate(self):
        os.execvp("sudo", ["sudo"] + sys.argv)

    def _configure_sysctl(self):
        sysctl.write('net.ipv4.ip_forward', 1)
        sysctl.write('net.ipv4.all.accept_redirects', 0)
        sysctl.write('net.ipv4.all.send_redirects', 0)

    def _configure_interface_names(self):
        inter   = net.Interfaces.getEthernet()
        options = ["%s %s" % (i.getName().ljust(8),i.getIpAddress() or "No IP Address") for i in inter]

        extdesc = 'Blancco PXE server requires connection to your network. ' \
                  'Please specify through which interface we will connect.'

        chosen_idx = dialog("Choose External Interface", extdesc, options)
        chosen_ext = options[chosen_idx].split(' ')[0]

        # Find chosen interface
        for i in inter:
            if i.getName() == chosen_ext:
                corp = i
                break

        # Remove chosen interface from options
        options.remove(options[chosen_idx])

        extdesc = 'Please specify through which interface we will connect to' \
                  ' your PXE network.'

        chosen_idx = dialog("Choose PXE Interface", extdesc, options)
        chosen_ext = options[chosen_idx].split(' ')[0]

        # Find chosen interface
        for i in inter:
            if i.getName() == chosen_ext:
                _pxe = i
                break

        self.corp_int = corp
        self._pxe_int = _pxe

        # Start modifying interfaces
        if corp.isUp(): corp.setDown()
        if _pxe.isUp(): _pxe.setDown()

        corp_nm = corp.getName()
        _pxe_nm = _pxe.getName()

        if not corp.setName('corp0'):
            raise EnvironmentError("Couldn't set Corporate interface name")
        if not _pxe.setName('pxe0'):
            raise EnvironmentError("Couldn't set PXE interface name")

        # Delete original interface files
        basepath = '/etc/sysconfig/network-scripts/ifcfg-%s'
        if os.path.isfile(basepath % corp_nm): os.remove(basepath % corp_nm)
        if os.path.isfile(basepath % _pxe_nm): os.remove(basepath % _pxe_nm)

        # Setup interface names in udev
        basepath = '/usr/lib/udev/rules.d/%s.rules'
        if os.path.isfile(basepath % '60-net'): os.remove(basepath % '60-net')

        line = 'ACTION=="add", SUBSYSTEM=="net", DRIVERS=="?*", ' \
               'ATTR{address}=="%s", NAME="%s"'
        f = open(basepath % '70-persistent-net', 'w+')
        f.write(line % (corp.getAddress(), corp.getName()))
        f.write(line % (_pxe.getAddress(), _pxe.getName()))
        f.close()

    def _configure_interfaces(self):
        corp = self.corp_int
        _pxe = self._pxe_int

        if not _pxe.setIpAddress('192.168.100.1'):
            raise EnvironmentError("Couldn't set PXE interface IP")
        if not _pxe.setNetmask(24):
            raise EnvironmentError("Couldn't set PXE interface Netmask")

        corp.setUp()
        _pxe.setUp()

        basepath = '/etc/sysconfig/network-scripts/ifcfg-%s'

        # Modify network files - corp
        f = open(basepath % 'corp0', 'w')
        f.write('DEVICE=corp0\n')
        f.write('BOOTPROTO=dhcp\n')
        f.write('DEFROUTE=yes\n')
        f.write('ONBOOT=yes\n')
        f.write('ZONE=corporate\n')
        f.write('UUID=%s\n' % str(uuid.uuid4()))
        f.close()

        # Modify network files - pxe
        f = open(basepath % 'pxe0', 'w')
        f.write('DEVICE=pxe0\n')
        f.write('BOOTPROTO=none\n')
        f.write('ONBOOT=yes\n')
        f.write('IPADDR=%s\n' % _pxe.getIpAddress())
        f.write('DNS1=%s\n'   % _pxe.getIpAddress())
        f.write('PREFIX=%d\n' % _pxe.getCidrMask())
        f.write('USERCTL=no\n')
        f.write('ZONE=pxe\n')
        f.write('UUID=%s\n' % str(uuid.uuid4()))
        f.close()

    def _configure_firewall(self):
        self.firewall.add_zone('pxe')
        self.firewall.add_zone('corporate')

        self.firewall.refresh()
        self.firewall.set_default_zone('corporate')

        self.firewall.set_zone('pxe')
        self.firewall.add_interface('pxe0')
        self.firewall.allow_service('http')
        self.firewall.allow_service('dhcp')
        self.firewall.allow_service('tftp')
        self.firewall.allow_service('dns')

        self.firewall.set_zone('corporate')
        self.firewall.add_interface('corp0')
        self.firewall.allow_service('ssh')
        self.firewall.allow_masquerade()

        self.firewall.refresh()

    def _configure_tftpd(self):
        path = os.path.realpath(os.path.dirname(__file__) + "/../../..")
        copy(path + '/assets/Linux/tftpd.conf', '/etc/xinetd.d/tftp')
        # chmod?
        # selinux? restorecon?

    def _configure_nginx(self):
        path = os.path.realpath(os.path.dirname(__file__) + "/../../..")
        copy(path + '/assets/Linux/nginx.conf', '/etc/nginx/nginx.conf')
        # chmod?
        # selinux? restorecon?

    def _configure_dhcpd(self):
        # This directory will store the bulk of the DHCP configuration
        os.path.isdir("/etc/dhcp/pxe/") or os.mkdir("/etc/dhcp/pxe/")

        path = os.path.realpath(os.path.dirname(__file__) + "/../../..")
        copy(path + '/assets/Linux/dhcpd/dhcpd.conf',  '/etc/dhcp/dhcpd.conf')
        copy(path + '/assets/Linux/dhcpd/legacy.conf', '/etc/dhcp/pxe/legacy.conf')
        copy(path + '/assets/Linux/dhcpd/ipxe.conf',   '/etc/dhcp/pxe/ipxe.conf')
        copy(path + '/assets/Linux/dhcpd/efi.conf',    '/etc/dhcp/pxe/efi.conf')
        copy(path + '/assets/Linux/dhcpd/bsdp.conf',   '/etc/dhcp/pxe/bsdp.conf')
