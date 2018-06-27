import apt
import sys
from .. import log
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
                pkg.mark_install()
                continue

        try:
            log.info('Installing packages...')
            cache.commit()
            log.success('Successfully installed packages')
        except Exception, arg:
            print >> sys.stderr, "Sorry, package installation failed: %s" % str(arg)
            raise RuntimeError("Package installation failed: %s" % str(arg)), None, sys.exc_info()[2]
