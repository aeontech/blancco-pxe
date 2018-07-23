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
        self.reload()

    def get_zone(self, name):
        return self.zone.getShort() is name

    def set_zone(self, name):
        self.zone = self.firewall.config().getZoneByName(name)

    def supports_zones(self):
        return True

    def get_zones(self):
        return self.firewall.config().listZones()

    def add_zone(self, name):
        if name in self.get_zones():
            return False

        settings = FirewallClientZoneSettings()
        settings.setShort(name)
        settings.setDescription('"%s" zone - added by Blancco!' % name)

        self.firewall.config().addZone(name, settings)

        return True

    def remove_zone(self, name):
        if name not in self.get_zones():
            return False

        self.firewall.config().remove_zone(name)
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

        settings = self.zone.getSettings()

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

        self.zone.update(settings)

    def allow_service(self, service):
        settings = self.zone.getSettings()

        if (service in settings):
            return

        settings.addService(service)
        self.zone.update(settings)

    def allow_masquerade(self):
        settings = self.zone.getSettings()
        settings.setMasquerade(True)
        self.zone.update(settings)

    def remove_port(self, port=None, protocol=None):
        if port is None and protocol is None:
            raise ValueError('No valid values passed to %s::%s' % (__class__, __func__))

        settings = self.zone.getSettings()

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

        self.zone.update(settings)

    def remove_service(self, service):
        settings = self.zone.getSettings()

        if (service not in settings):
            return

        settings.removeService(service)
        self.zone.update(settings)

    def remove_masquerade(self):
        settings = self.zone.getSettings()
        settings.setMasquerade(False)
        self.zone.update(settings)
