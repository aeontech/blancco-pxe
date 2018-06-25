import yum
from LinuxStrapper import LinuxStrapper

class RhStrapper(LinuxStrapper):
    packages = "".split(" ")

    def install_packages(self):
        yb = yum.YumBase()
        yb.conf.cache = false

        try:
            yb.doLock()

            # First off, we need epel-release
            epel = yb.searchGenerator(['name'], ['epel-release'])
            print "%r" % epel
        finally:
            yb.doUnlock()

    def configure_packages(self):
        pass
