import ufw.frontend
import ufw.common

from Firewall import Firewall

class Ufw(Firewall):
    firewall = None

    def __init__(self):
        self.firewall = ufw.frontend.UFWFrontend(False)

    def refresh():
        pass

    def set_zone(name):
        pass

    def supports_zones():
        return False

    def get_zones():
        return []

    def add_zone(name):
        return False

    def remove_zone(name):
        return False

    def is_port_allowed(port=None, protocol=None):
        return True

    def is_service_allowed(service):
        return True

    def is_masquerade_allowed():
        return False

    def allow_port(port=None, protocol=None):
        pass

    def allow_service(service):
        pass

    def allow_masquerade():
        pass

    def remove_port(port=None, protocol=None):
        pass

    def remove_service(service):
        pass

    def remove_masquerade():
        pass
