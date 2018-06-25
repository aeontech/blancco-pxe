import os
import platform

rh_dists = [
    "CentOS Linux",
    "Red Hat Enterprise Linux Server"
]

deb_dists = [
    "debian",
    "Ubuntu"
]

def get_strapper():
    if os.name == "nt":
        return _get_win_strapper()

    if os.name == "posix" and platform.linux_distribution()[0] in rh_dists:
        return _get_rh_strapper()

    if os.name == "posix" and platform.linux_distribution()[0] in deb_dists:
        return _get_deb_strapper()

    raise EnvironmentError('Unknown environment ' + os.name + ' with dist %r' %
        platform.linux_distribution()[0])

def _get_win_strapper():
    print "Windows strapper"

def _get_rh_strapper():
    print "RH strapper"

def _get_deb_strapper():
    from DebStrapper import DebStrapper
    return DebStrapper()
