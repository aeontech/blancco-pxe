# Base firewall class

class Firewall:
    def refresh():
        raise NotImplementedError('%s::%s not implemented in child' % (self.__class__.__name__, 'refresh'))

    def get_zone(self, name):
        raise NotImplementedError('%s::%s not implemented in child' % (self.__class__.__name__, 'get_zone'))

    def set_zone(name):
        raise NotImplementedError('%s::%s not implemented in child' % (self.__class__.__name__, 'set_zone'))

    def supports_zones():
        raise NotImplementedError('%s::%s not implemented in child' % (self.__class__.__name__, 'supports_zones'))

    def get_zones():
        raise NotImplementedError('%s::%s not implemented in child' % (self.__class__.__name__, 'get_zones'))

    def add_zone(name):
        raise NotImplementedError('%s::%s not implemented in child' % (self.__class__.__name__, 'add_zone'))

    def remove_zone(name):
        raise NotImplementedError('%s::%s not implemented in child' % (self.__class__.__name__, 'remove_zone'))

    def get_interfaces(self):
        raise NotImplementedError('%s::%s not implemented in child' % (self.__class__.__name__, 'get_interfaces'))

    def interface_in(self, ifname):
        raise NotImplementedError('%s::%s not implemented in child' % (self.__class__.__name__, 'interface_in'))

    def add_interface(self, ifname):
        raise NotImplementedError('%s::%s not implemented in child' % (self.__class__.__name__, 'add_interface'))

    def remove_interface(self, ifname):
        raise NotImplementedError('%s::%s not implemented in child' % (self.__class__.__name__, 'remove_interface'))

    def get_ports(self):
        raise NotImplementedError('%s::%s not implemented in child' % (self.__class__.__name__, 'get_ports'))

    def get_services(self):
        raise NotImplementedError('%s::%s not implemented in child' % (self.__class__.__name__, 'get_services'))

    def is_port_allowed(port=None, protocol=None):
        raise NotImplementedError('%s::%s not implemented in child' % (self.__class__.__name__, 'is_port_allowed'))

    def is_service_allowed(service):
        raise NotImplementedError('%s::%s not implemented in child' % (self.__class__.__name__, 'is_service_allowed'))

    def is_masquerade_allowed():
        raise NotImplementedError('%s::%s not implemented in child' % (self.__class__.__name__, 'is_masquerade_allowed'))

    def allow_port(port=None, protocol=None):
        raise NotImplementedError('%s::%s not implemented in child' % (self.__class__.__name__, 'allow_port'))

    def allow_service(service):
        raise NotImplementedError('%s::%s not implemented in child' % (self.__class__.__name__, 'allow_service'))

    def allow_masquerade():
        raise NotImplementedError('%s::%s not implemented in child' % (self.__class__.__name__, 'allow_masquerade'))

    def remove_port(port=None, protocol=None):
        raise NotImplementedError('%s::%s not implemented in child' % (self.__class__.__name__, 'remove_port'))

    def remove_service(service):
        raise NotImplementedError('%s::%s not implemented in child' % (self.__class__.__name__, 'remove_service'))

    def remove_masquerade():
        raise NotImplementedError('%s::%s not implemented in child' % (self.__class__.__name__, 'remove_masquerade'))
