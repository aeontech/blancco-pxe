from FirewallError import FirewallError
from firewall.client import FirewallClient
from firewall.client import FirewallClientZoneSettings

from Firewall import Firewall

class Firewalld(Firewall):
    firewall = None
    zone = None

    def __init__(self, sysbus):
        self.firewall = FirewallClient(sysbus)
        self.set_zone(self.firewall.getDefaultZone())

    def refresh(self):
        self.firewall.reload()

    def get_default_zone(self):
        return self.firewall.getDefaultZone()

    def set_default_zone(self, zone):
        if not self.zone_exists(zone):
            raise RuntimeError('Zone "%s" doesn\'t exist.' % zone)

        return self.firewall.setDefaultZone(zone)

    def is_zone(self, name):
        return self.zone.getShort() is name

    def get_zone_name(self):
        return self.zone.getShort()

    def set_zone(self, name):
        self.zone = self.firewall.config().getZoneByName(name)

    def supports_zones(self):
        return True

    def zone_exists(self, zone):
        return zone in self.get_zones()

    def get_zones(self):
        return self.firewall.config().getZoneNames()

    def add_zone(self, name):
        if name in self.get_zones():
            return False

        settings = FirewallClientZoneSettings()
        settings.setShort(name)
        settings.setDescription('"%s" zone - added by Blancco!' % name)

        try:
            self.firewall.config().addZone(name, settings)
        except dbus.DBusException, ex:
            raise FirewallError(ex.message)

        return True

    def remove_zone(self, name):
        if name not in self.get_zones():
            return False

        try:
            self.firewall.config().remove_zone(name)
        except dbus.DBusException, ex:
            raise FirewallError(ex.message)

        return True

    def get_interfaces(self):
        return self.zone.getInterfaces()

    def interface_in(self, ifname):
        return self.zone.queryInterface(ifname)

    def add_interface(self, ifname):
        if self.interface_in(ifname):
            return False

        try:
            self.zone.addInterface(ifname)
        except dbus.DBusException, ex:
            raise FirewallError(ex.message)

        return True

    def remove_interface(self, ifname):
        if not self.interface_in(ifname):
            return False

        try:
            self.zone.removeInterface(ifname)
        except dbus.DBusException, ex:
            raise FirewallError(ex.message)

        return True

    def get_ports(self):
        return self.zone.getPorts()

    def get_services(self):
        return self.zone.getServices()

    def is_port_allowed(self, port=None, protocol=None):
        if port is None and protocol is None:
            raise ValueError('No valid values passed to %s::%s' % (__class__, __func__))

        settings  = self.zone.getSettings()

        if port is not None and protocol is None:
            return settings.queryPort(port, 'tcp') or \
                   settings.queryPort(port, 'udp')
        elif port is None and protocol is not None:
            return settings.queryProtocol(protocol)
        else:
            return settings.queryPort(port, protocol)

    def is_service_allowed(self, service):
        return self.zone.getSettings().queryService(service)

    def is_masquerade_allowed(self):
        return self.zone.getSettings().queryMasquerade()

    def allow_port(self, port=None, protocol=None):
        if port is None and protocol is None:
            raise ValueError('No valid values passed to %s::%s' % (__class__, __func__))

        old = settings = self.zone.getSettings()

        if port is not None and protocol is None:
            if not self.is_port_allowed(port, 'tcp'):
                settings.addPort(port, 'tcp')

            if not self.is_port_allowed(port, 'udp'):
                settings.addPort(port, 'udp')
        elif port is None and protocol is not None:
            if not self.is_port_allowed(protocol=protocol):
                settings.addProtocol(protocol)
        else:
            if not self.is_port_allowed(port=port):
                settings.addPort(port, protocol)

        if old == settings:
            return False

        try:
            self.zone.update(settings)
        except dbus.DBusException, ex:
            raise FirewallError(ex.message)

        return True

    def allow_service(self, service):
        if (self.is_service_allowed(service)):
            return False

        settings = self.zone.getSettings()
        settings.addService(service)

        try:
            self.zone.update(settings)
        except dbus.DBusException, ex:
            raise FirewallError(ex.message)

        return True

    def allow_masquerade(self):
        if self.is_masquerade_allowed():
            return False

        settings = self.zone.getSettings()
        settings.setMasquerade(True)

        try:
            self.zone.update(settings)
        except dbus.DBusException, ex:
            raise FirewallError(ex.message)

        return True

    def remove_port(self, port=None, protocol=None):
        if port is None and protocol is None:
            raise ValueError('No valid values passed to %s::%s' % (__class__, __func__))

        old = settings = self.zone.getSettings()

        if port is not None and protocol is None:
            if self.is_port_allowed(port, 'tcp'):
                settings.removePort(port, 'tcp')

            if self.is_port_allowed(port, 'udp'):
                settings.removePort(port, 'udp')
        elif port is None and protocol is not None:
            if self.is_port_allowed(protocol=protocol):
                settings.removeProtocol(protocol)
        else:
            if self.is_port_allowed(port=port):
                settings.removePort(port, protocol)

        if old == settings:
            return False

        try:
            self.zone.update(settings)
        except dbus.DBusException, ex:
            raise FirewallError(ex.message)

        return True

    def remove_service(self, service):
        if (not self.is_service_allowed(service)):
            return False

        settings = self.zone.getSettings()
        settings.removeService(service)

        try:
            self.zone.update(settings)
        except dbus.DBusException, ex:
            raise FirewallError(ex.message)

        return True

    def remove_masquerade(self):
        if not self.is_masquerade_allowed():
            return False

        settings = self.zone.getSettings()
        settings.setMasquerade(False)

        try:
            self.zone.update(settings)
        except dbus.DBusException, ex:
            raise FirewallError(ex.message)

        return True
