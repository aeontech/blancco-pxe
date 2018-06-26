# See https://wiki.freedesktop.org/www/Software/systemd/dbus/#methods

import dbus

def stop(unit):
    mgr = _getManager()
    return manager.StopUnit(unit, 'fail')

def start(unit):
    mgr = _getManager()
    return manager.StartUnit(unit, 'fail')

def restart(unit):
    mgr = _getManager()
    return manager.RestartUnit(unit, 'fail')

def reload(unit):
    mgr = _getManager()
    return manager.ReloadUnit(unit, 'fail')

def enable(unit):
    mgr = _getManager()
    return manager.EnableUnitFiles(unit, True)

def disable(unit):
    mgr = _getManager()
    return manager.DisableUnitFiles(unit, True)

def isEnabled(unit):

def isRunning(unit):

def _getManager():
    sysbus   = dbus.SystemBus()
    systemd1 = sysbus.get_object('org.freedesktop.systemd1', '/org/freedesktop/systemd1')

    return dbus.Interface(systemd1, 'org.freedesktop.systemd1.Manager')
                                  #  org.freedesktop.systemd1.Unit
