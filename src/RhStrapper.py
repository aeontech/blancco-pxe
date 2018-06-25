import yum
import log
from LinuxStrapper import LinuxStrapper

class RhStrapper(LinuxStrapper):
    packages = "".split(" ")

    def install_packages(self):
        yb = yum.YumBase()
        yb.conf.cache = False

        try:
            yb.doLock()

            # First off, we need epel-release
            self._mark_install(yb, 'epel-release')

            yb.buildTransaction()
            yb.processTransaction()

            for package in self.packages:
                self._mark_install(yb, package)

            # yb.buildTransaction()
            # yb.processTransaction()
        finally:
            yb.doUnlock()

    def configure_packages(self):
        pass

    def _mark_install(self, yb, pkgname):
        matching = yb.searchGenerator(['name'], [pkgname], False, True)
        for (pkg, matched_value, matched_keys) in matching:
            if matched_keys[0] == pkgname:
                log.warn('Marking package "%s" for installation' % pkgname)
                yb.install(pkg)
