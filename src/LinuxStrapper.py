import os
import log
import sys

class LinuxStrapper:
    def checkenv(self):
        # Check for sudo privs
        if os.getuid() != 0:
            log.warn('Requires elevation!')
            self._elevate()

        # Ensure we are definitly admin
        if os.getuid() != 0:
            raise EnvironmentError("Not admin - could not elevate privileges!")

    def install_packages(self):
        pass

    def configure_packages(self):
        log.info("Configuring Packages...")
        self._configure_tftpd()
        self._configure_xinetd()
        self._configure_nginx()
        self._configure_dhcpd()

    def configure_startup(self):
        # enable & start
        pass

    def _configure_tftpd(self):
        pass

    def _configure_xinetd(self):
        pass

    def _configure_nginx(self):
        copy('assets/linux/nginx.conf', '/etc/nginx/nginx.conf')
        # chmod?
        # selinux? restorecon?

    def _configure_dhcpd(self):
        pass

    def _elevate(self):
        os.execvp("sudo", ["sudo"] + sys.argv)
