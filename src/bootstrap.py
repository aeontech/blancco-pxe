import os
import log
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

    raise EnvironmentError('Unknown environment %s with dist %r' %
        (os.name, platform.linux_distribution()[0]))

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
    import Linux.systemd as systemd

    if systemd.exists('ufw.service'):
        from Linux.Firewall.Ufw import Ufw
        return Ufw()
    elif systemd.exists('firewalld.service'):
        from Linux.Firewall.Firewalld import Firewalld
        return Firewalld()
    elif systemd.exists('iptables.service'):
        log.warn("We won't be inserting firewall rules for iptables.\n" + \
           "      Please handle the firewall rules yourself.")
    else:
        log.error("Unknown firewall system in use - Ignorantly ignoring")

    # This isn't *really* meant to be used this way, but it works
    # as a stub object!
    from Linux.Firewall.Firewall import Firewall
    return Firewall()
