import yum
import rpm
import log
from LinuxStrapper import LinuxStrapper

class RhStrapper(LinuxStrapper):
    packages = "tftp tftp-server xinetd nginx dhcpd".split(" ")

    def install_packages(self):
        yb = yum.YumBase()
        yb.conf.cache = False
        # No output callback - let's make things clean
        cb = yum.rpmtrans.NoOutputCallBack()

        try:
            yb.doLock()

            # First off, we need epel-release
            self._mark_install(yb, 'epel-release')

            yb.buildTransaction()
            yb.processTransaction(rpmTestDisplay=cb, rpmDisplay=cb)

            # We just added a repo - clear cache
            yb.cleanHeaders()
            yb.cleanMetadata()

            for package in self.packages:
                self._mark_install(yb, package)

            yb.resolveDeps()
            yb.buildTransaction()
            yb.processTransaction()
        finally:
            yb.doUnlock()

    def configure_packages(self):
        pass

    def _mark_install(self, yb, pkgname):
        matching = yb.searchGenerator(['name'], [pkgname], False, True)
        for (pkg, matched_value, matched_keys) in matching:
            if matched_keys[0] != pkgname:
                continue

            if Not self._is_installed(yb, pkgname):
                log.warn('Marking package "%s" for installation' % pkgname)
                yb.install(pkg)
            else
                log.debug('Package "%s" already installed - skipping' % pkgname)

            # Installed, or marked for install
            break

    def _is_installed(self, yb, pkgname):
        pkgs = yb.rpmdb.returnPackages()

        for pkg in pkgs:
            if pkg.name == pkgname:
                return True

        return False
