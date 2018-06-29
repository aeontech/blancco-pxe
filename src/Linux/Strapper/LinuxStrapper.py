import os
import abc
import sys
from shutil import copy
from ... import log
from .. import systemd
from .. import sysctl

class LinuxStrapper(object):
    firewalld = None

    def __init__(self, firewall_daemon):
        self.firewalld = firewall_daemon

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
        return
        self._configure_sysctl()
        self._configure_udev()
        self._configure_interfaces()
        self._configure_firewall()

        log.info("Configuring Packages...")
        self._configure_tftpd()
        self._configure_nginx()
        self._configure_dhcpd()

    def configure_startup(self):
        for service in ['nginx', 'xinetd', 'dhcpd']:
            systemd.enable("%s.service" % service)
            systemd.start ("%s.service" % service)

    def _elevate(self):
        os.execvp("sudo", ["sudo"] + sys.argv)

    def _configure_sysctl(self):
        sysctl.write('net.ipv4.ip_forward', 1)
        sysctl.write('net.ipv4.all.accept_redirects', 0)
        sysctl.write('net.ipv4.all.send_redirects', 0)

    def _configure_udev(self):
        pass

    def _configure_interfaces(self):
        pass

    def _configure_firewall(self):
        pass

    def _configure_tftpd(self):
        path = os.path.realpath(os.path.dirname(__file__) + "../../..")
        copy(path + '/assets/Linux/tftpd.conf', '/etc/xinetd.d/tftp')
        # chmod?
        # selinux? restorecon?

    def _configure_nginx(self):
        path = os.path.realpath(os.path.dirname(__file__) + "../../..")
        copy(path + '/assets/Linux/nginx.conf', '/etc/nginx/nginx.conf')
        # chmod?
        # selinux? restorecon?

    def _configure_dhcpd(self):
        # This directory will store the bulk of the DHCP configuration
        os.path.isdir("/etc/dhcp/pxe/") or os.mkdir("/etc/dhcp/pxe/")

        path = os.path.realpath(os.path.dirname(__file__) + "../../..")
        copy(path + '/assets/Linux/dhcpd/dhcpd.conf',  '/etc/dhcp/dhcpd.conf')
        copy(path + '/assets/Linux/dhcpd/legacy.conf', '/etc/dhcp/pxe/legacy.conf')
        copy(path + '/assets/Linux/dhcpd/ipxe.conf',   '/etc/dhcp/pxe/ipxe.conf')
        copy(path + '/assets/Linux/dhcpd/efi.conf',    '/etc/dhcp/pxe/efi.conf')
        copy(path + '/assets/Linux/dhcpd/bsdp.conf',   '/etc/dhcp/pxe/bsdp.conf')
