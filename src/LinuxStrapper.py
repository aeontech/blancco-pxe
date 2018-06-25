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
        pass

    def _elevate(self):
        os.execvp("sudo", ["sudo"] + sys.argv)
