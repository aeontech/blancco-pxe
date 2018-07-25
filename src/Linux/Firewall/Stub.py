from Firewall import Firewall
from FirewallError import FirewallError

class Stub(Firewall):
    def refresh():
        pass

    def get_zone(name):
        raise FirewallError("Stub Firewall doesn't support zones")

    def set_zone(name):
        raise FirewallError("Stub Firewall doesn't support zones")

    def supports_zones():
        return False

    def get_zones():
        raise FirewallError("Stub Firewall doesn't support zones")

    def add_zone(name):
        raise FirewallError("Stub Firewall doesn't support zones")

    def remove_zone(name):
        raise FirewallError("Stub Firewall doesn't support zones")

    def get_interfaces(self):
        return []

    def interface_in(self, ifname):
        return False

    def add_interface(self, ifname):
        raise FirewallError("Stub Firewall doesn't support zones")

    def remove_interface(self, ifname):
        raise FirewallError("Stub Firewall doesn't support zones")

    def get_ports(self):
        return []

    def get_services(self):
        return []

    def is_port_allowed(port=None, protocol=None):
        return True

    def is_service_allowed(service):
        return True

    def is_masquerade_allowed():
        return False

    def allow_port(port=None, protocol=None):
        return True

    def allow_service(service):
        return True

    def allow_masquerade():
        return True

    def remove_port(port=None, protocol=None):
        return True

    def remove_service(service):
        return True

    def remove_masquerade():
        return True
