import os
import sys
import ctypes

class WinStrapper:
    def checkenv(self):
        # Check for admin privs
        if ctypes.windll.shell32.IsUserAnAdmin() == 0:
            self._elevate()

        # Ensure we are definitely admin
        if ctypes.windll.shell32.isUserAnAdmin() == 0:
            print "Not admin - could not elevate privileges!"
            exit()

    def install_packages(self):
        pass

    def configure_packages(self):
        pass

    # elevate: https://gist.github.com/GaryLee/d1cf2089c3a515691919
    def _elevate(self):
        pass
