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
    from Linux.Strapper.WinStrapper import WinStrapper
    return WinStrapper()

def _get_rh_strapper():
    from Linux.Strapper.RhStrapper import RhStrapper
    return RhStrapper(_get_firewall_daemon())

def _get_deb_strapper():
    from Linux.Strapper.DebStrapper import DebStrapper
    return DebStrapper(_get_firewall_daemon())

def _get_firewall_daemon():
    # ufw
    # firewalld
    # iptables
    pass
