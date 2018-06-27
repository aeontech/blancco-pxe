# See https://wiki.freedesktop.org/www/Software/systemd/dbus/#methods

import dbus

def stop(unit):
    return _getManager().StopUnit(unit, 'fail')

def start(unit):
    return _getManager().StartUnit(unit, 'fail')

def restart(unit):
    return _getManager().RestartUnit(unit, 'fail')

def reload(unit):
    return _getManager().ReloadUnit(unit, 'fail')

def enable(unit):
    return _getManager().EnableUnitFiles(unit, True)

def disable(unit):
    return _getManager().DisableUnitFiles(unit, True)

def isEnabled(unit):
    unit  = _getUnit(unit)
    state = unit.Get('org.freedesktop.systemd1.Unit', 'isEnabled',
                     'org.freedektop.DBus.Properties')

    if state in ['loaded', 'static']:
        return True
    elif state in ['enabled-runtime', 'linked', 'linked-runtime', 'masked',
                   'masked-runtime', 'disabled', 'invalid']:
        return False

    raise RuntimeError("Unknown service enabled state: %r" % state)

def isRunning(unit):
    unit  = _getUnit(unit)
    state = unit.Get('org.freedesktop.systemd1.Unit', 'ActiveState',
                    'org.freedektop.DBus.Properties')

    if state in ['active', 'reloading', 'activating']:
        return True
    elif state in ['inactive', 'failed', 'deactivating']:
        return False

    raise RuntimeError("Unknown service state: %r" % state)

def _getManager():
    sysbus   = dbus.SystemBus()
    systemd1 = sysbus.get_object('org.freedesktop.systemd1', '/org/freedesktop/systemd1')

    return dbus.Interface(systemd1, 'org.freedesktop.systemd1.Manager')

def _getUnit(unit):
    manager = _getManager()
    path    = manager.LoadUnit(unit)
    proxy   = dbus.get_object('org.freedesktop.systemd1', path)

    return dbus.Interface(proxy, 'org.freedesktop.systemd1.Unit')
