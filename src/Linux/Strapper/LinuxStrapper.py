import os
import abc
import sys
from shutil import copy
from .. import net
from ... import log
from .. import systemd
from .. import sysctl
from ..dialog import dialog

class LinuxStrapper(object):
    firewall = None

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
        # self._configure_interfaces()
        # self._configure_firewall()

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
        options = ["%s %s" % (i.getName().ljust(8),i.getIpAddress()) for i in inter]

        extdesc = '''
Blancco PXE server requires connection to your network.
Please specify through which interface we will connect.
'''

        chosen_ext = dialog("Choose External Interface", extdesc, options)

    def _configure_interfaces(self):
        pass

    def _configure_firewall(self):
        self.firewall.add_zone('pxe')
        self.firewall.add_zone('corporate')

        self.firewall.set_zone('pxe')
        # assign pxe0 to pxe zone
        self.firewall.add_service('http')
        self.firewall.add_service('dhcp')
        self.firewall.add_service('tftp')
        self.firewall.add_service('dns')

        self.firewall.set_zone('corporate')
        # assign corp0 to corporate zone
        self.firewall.add_service('ssh')
        self.firewall.add_masquerade()

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
