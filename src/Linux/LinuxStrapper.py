import os
import abc
import log
import sys
from shutil import copy
import systemd
import sysctl

class LinuxStrapper:
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
        copy(os.getcwd() + '/assets/Linux/tftpd.conf', '/etc/xinetd.d/tftp')
        # chmod?
        # selinux? restorecon?

    def _configure_nginx(self):
        copy(os.getcwd() + '/assets/Linux/nginx.conf', '/etc/nginx/nginx.conf')
        # chmod?
        # selinux? restorecon?

    def _configure_dhcpd(self):
        # This directory will store the bulk of the DHCP configuration
        os.path.isdir("/etc/dhcp/pxe/") or os.mkdir("/etc/dhcp/pxe/")

        copy(os.getcwd() + '/assets/Linux/dhcpd/dhcpd.conf',  '/etc/dhcp/dhcpd.conf')
        copy(os.getcwd() + '/assets/Linux/dhcpd/legacy.conf', '/etc/dhcp/pxe/legacy.conf')
        copy(os.getcwd() + '/assets/Linux/dhcpd/ipxe.conf',   '/etc/dhcp/pxe/ipxe.conf')
        copy(os.getcwd() + '/assets/Linux/dhcpd/efi.conf',    '/etc/dhcp/pxe/efi.conf')
        copy(os.getcwd() + '/assets/Linux/dhcpd/bsdp.conf',   '/etc/dhcp/pxe/bsdp.conf')
