import dbus

class systemd:
    sysbus = None

    def __init__(self, sysbus):
        self.sysbus = sysbus

    def stop(self, unit):
        return self._getManager().StopUnit(unit, 'fail')

    def start(self, unit):
        return self._getManager().StartUnit(unit, 'fail')

    def restart(self, unit):
        return self._getManager().RestartUnit(unit, 'fail')

    def reload(self, unit):
        return self._getManager().ReloadUnit(unit, 'fail')

    def enable(self, unit):
        return self._getManager().EnableUnitFiles([unit], False, False)

    def disable(self, unit):
        return self._getManager().DisableUnitFiles([unit], False)

    def exists(self, unit):
        try:
            unit  = self._getUnit(unit)
            props = dbus.Interface(unit, 'org.freedesktop.DBus.Properties')
            load  = props.Get('org.freedesktop.systemd1.Unit', 'LoadError')[0]

            if 'org.freedesktop.DBus.Error.FileNotFound' == load:
                return False
        except dbus.exceptions.DBusException:
            return False

        return True

    def isEnabled(self, unit):
        unit  = self._getUnit(unit)
        props = dbus.Interface(unit, 'org.freedesktop.DBus.Properties')
        state = props.Get('org.freedesktop.systemd1.Unit', 'UnitFileState')

        if state in ['enabled', 'static']:
            return True
        elif state in ['enabled-runtime', 'linked', 'linked-runtime', 'masked',
                       'masked-runtime', 'disabled', 'invalid']:
            return False

        raise RuntimeError("Unknown service enabled state: %r" % state)

    def isRunning(self, unit):
        unit  = dbus.Interface(self._getUnit(unit), 'org.freedesktop.systemd1.Unit')
        props = dbus.Interface(unit, 'org.freedesktop.DBus.Properties')
        state = props.Get('org.freedesktop.systemd1.Unit', 'ActiveState')

        if state in ['active', 'reloading', 'activating']:
            return True
        elif state in ['inactive', 'failed', 'deactivating']:
            return False

        raise RuntimeError("Unknown service state: %r" % state)

    def _getManager(self):
        systemd1 = self.sysbus.get_object('org.freedesktop.systemd1', '/org/freedesktop/systemd1')

        return dbus.Interface(systemd1, 'org.freedesktop.systemd1.Manager')

    def _getUnit(self, unit):
        systemd1 = self.sysbus.get_object('org.freedesktop.systemd1', '/org/freedesktop/systemd1')
        manager  = dbus.Interface(systemd1, 'org.freedesktop.systemd1.Manager')
        path     = manager.LoadUnit(unit)
        proxy    = self.sysbus.get_object('org.freedesktop.systemd1', path)

        return dbus.Interface(proxy, 'org.freedesktop.systemd1.Unit')
