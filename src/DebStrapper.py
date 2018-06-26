import apt
import sys
import log
from shutil import copy
from LinuxStrapper import LinuxStrapper

class DebStrapper(LinuxStrapper):
    packages = "tftp tftpd xinetd nginx isc-dhcp-server".split(" ")

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
                continue

                pkg.mark_install()

        try:
            log.info('Installing packages...')
            cache.commit()
            log.success('Successfully installed packages')
        except Exception, arg:
            print >> sys.stderr, "Sorry, package installation failed [{err}]".format(err=str(arg))
            raise RuntimeException("Package installation failed: err")

    def configure_packages(self):
        log.info("Configuring Packages...")
        self._configure_tftpd()
        self._configure_xinetd()
        self._configure_nginx()
        self._configure_dhcpd()

    def _configure_tftpd(self):
        copy('assets/nginx.conf', '/etc/nginx/nginx.conf')
        # chmod?
        # selinux? restorecon?

    def _configure_xinetd(self):
        pass

    def _configure_nginx(self):
        pass

    def _configure_dhcpd(self):
        pass
