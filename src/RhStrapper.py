import yum
from src import LinuxStrapper

class RhStrapper(LinuxStrapper):
    packages = "".split(" ")

    def install_packages(self):
        yum = yum.YumBase()
        yb.conf.cache = false

        try:
            yum.doLock()

            # First off, we need epel-release
            epel = yum.searchGenerator(['name'], ['epel-release'])
            print "%r" % epel
        finally:
            yum.doUnlock()

    def configure_packages(self):
        pass
