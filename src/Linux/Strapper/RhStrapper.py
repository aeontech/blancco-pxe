import yum
import rpm
from ... import log
from LinuxStrapper import LinuxStrapper

class RhStrapper(LinuxStrapper):
    packages = "tftp tftp-server xinetd nginx dhcp".split(" ")
    yb = None
    # No output callback - let's make things clean
    cb = yum.rpmtrans.NoOutputCallBack()


    def __init__(self, firewall_daemon):
        self.yb = yum.YumBase()
        self.yb.conf.cache = False
        super(__class__).__init__(firewall_daemon)

    def install_packages(self):
        try:
            self.yb.doLock()

            # First off, we need epel-release
            if self._install('epel-release'):
                # Read EPEL config + enable the repo
                self.yb.getReposFromConfigFile('/etc/yum.repos.d/epel.repo')
                self.yb.repos.enableRepo('epel')

                # Add repo to the package sack
                self.yb.repos.populateSack('epel')

                # Test to ensure EPEL is enabled
                for repo in self.yb.repos.repos.values():
                    if repo.id == 'epel' and not repo.isEnabled():
                        raise EnvironmentError('Failed to enable EPEL repository')

                # We just added a repo - clear cache
                self.yb.cleanHeaders()
                self.yb.cleanMetadata()

            for package in self.packages:
                if not self._install(package):
                    raise EnvironmentError('Failed to install package "%s"' % package)

        finally:
            self.yb.doUnlock()

    def configure_packages(self):
        pass

    def _install(self, pkgname):
        matching = self.yb.searchGenerator(['name'], [pkgname], False, True)

        # Loop through to find the correct package
        for (pkg, matched_value, matched_keys) in matching:
            # Not this one - skip
            if matched_keys[0] != pkgname:
                continue

            # If we're already installed, end the loop
            if self._is_installed(pkgname):
                log.debug('Package "%s" already installed - skipping' % pkgname)
                return True

            # We're not installed - so let's do that
            log.warn('Marking package "%s" for installation' % pkgname)

            self.yb.install(pkg)
            self.yb.resolveDeps()

            rc, msgs = self.yb.buildTransaction()
            if rc != 2:
                break

            try:
                self.yb.processTransaction(rpmTestDisplay=self.cb, rpmDisplay=self.cb)
                log.success('Successfully installed package "%s"' % pkgname)

                # Now we're installed, let's end the loop
                return True
            except:
                pass
        else:
            log.error('Package "%s" has no installation target!' % pkgname)

        # Uh-oh, there was an error during installation
        return False

    def _is_installed(self, pkgname):
        pkgs = self.yb.rpmdb.returnPackages()

        for pkg in pkgs:
            if pkg.name == pkgname:
                return True

        return False
