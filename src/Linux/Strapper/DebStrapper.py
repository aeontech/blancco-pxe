import os
import apt
import sys
from ... import log
from LinuxStrapper import LinuxStrapper

class DebStrapper(LinuxStrapper):
    packages = "tftp tftpd xinetd nginx dnsmasq isc-dhcp-server".split(" ")

    def install_packages(self):
        cache = apt.cache.Cache()
        cache.update()
        cache.open()

        for package in self.packages:
            pkg = cache[package]

            if pkg.is_installed:
                log.debug('Package "%s" already installed - skipping' % pkg)
                continue
            else:
                log.warn('Marking package "%s" for installation' % pkg)
                pkg.mark_install()
                continue

        try:
            log.info('Installing packages...')
            cache.commit()
            log.success('Successfully installed packages')
        except Exception, arg:
            print >> sys.stderr, "Sorry, package installation failed: %s" % str(arg)
            raise RuntimeError("Package installation failed: %s" % str(arg)), None, sys.exc_info()[2]

    def _configure_interfaces(self):
        super(self.__class__, self)._configure_interfaces()

        if os.path.isfile('/run/network/ifstate'):
            self._configure_ifupdown()
        else:
            self._configure_netplan()

    def _configure_ifupdown(self):
        pass

    def _configure_netplan(self):
        file = '''
        network:
            version: 2
            ethernets:
                corp0:
                    dhcp4: yes
                pxe0:
                    dhcp4: no
                    dhcp6: no
                    addresses: [%s/%d]
                    nameservers:
                        addresses: [%s]
        ''' % (
            self._pxe_int.getIpAddress(),
            self._pxe_int.getCidrMask(),
            self._pxe_int.getIpAddress()
        )

        f = open('/etc/netplan/01-netcfg.yaml', 'w')
        f.write(file)
        f.close()

        os.system('netplan apply')
