import yum
import rpm
import log
from LinuxStrapper import LinuxStrapper

class RhStrapper(LinuxStrapper):
    packages = "tftp tftp-server xinetd nginx dhcp".split(" ")
    yb = None

    def __init__(self):
        self.yb = yum.YumBase()
        self.yb.conf.cache = False

    def install_packages(self):
        # No output callback - let's make things clean
        cb = yum.rpmtrans.NoOutputCallBack()

        try:
            self.yb.doLock()

            # First off, we need epel-release
            if not self._is_installed("epel-release")
                self._mark_install('epel-release')
                rc, msgs = self.yb.buildTransaction()
                if rc != 2:
                    print "nope"
                    return False

                try:
                    self.yb.processTransaction(rpmTestDisplay=cb, rpmDisplay=cb)
                except:
                    print "wtf"
                    return False

                # We just added a repo - clear cache
                self.yb.cleanHeaders()
                self.yb.cleanMetadata()

            for package in self.packages:
                self._mark_install(package)

            self.yb.resolveDeps()
            rc, msgs = self.yb.buildTransaction()
            if rc != 2:
                print "nope"
                return False

            try:
                self.yb.processTransaction()
            except:
                print "wtf"
                return False
        finally:
            self.yb.doUnlock()

    def configure_packages(self):
        pass

    def _mark_install(self, pkgname):
        matching = self.yb.searchGenerator(['name'], [pkgname], False, True)

        for (pkg, matched_value, matched_keys) in matching:
            if matched_keys[0] != pkgname:
                continue

            if not self._is_installed(pkgname):
                log.warn('Marking package "%s" for installation' % pkgname)
                self.yb.install(pkg)
            else:
                log.debug('Package "%s" already installed - skipping' % pkgname)

            # Installed, or marked for install
            break
        else:
            log.error('Package "%s" has no installation target!' % pkgname)

    def _is_installed(self, pkgname):
        pkgs = self.yb.rpmdb.returnPackages()

        for pkg in pkgs:
            if pkg.name == pkgname:
                return True

        return False
