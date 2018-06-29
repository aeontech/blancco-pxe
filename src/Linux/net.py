from os import path
from glob import glob

from .. import log

class Interfaces:
    def getPhysical():
        return [iface for iface in self.getInterfaces() if iface.isPhysical()]

    def getInterfaces():
        return [Interface(path.basename(iface) for iface in glob('/sys/class/net/*')]

    def isValidInterface(self=None,name=None):
        return path.isdir('/sys/class/net/%s/' % name)

class Interface:
    ifname = None

    def __init__(self, name):
        if not Interfaces.isValidInterface(name):
            raise InvalidInterface('Interface "%s" does not exist.' % name)

        self.ifname = name

    # Retrieves the MAC address
    def getAddress(self):
        return _read(self.ifname, 'address')

    def getBroadcast(self):
        return _read(self.ifname, 'broadcast')

    def getDevId(self):
        return _read(self.ifname, 'dev_id')

    def getDuplex(self):
        return _read(self.ifname, 'duplex')

    def getFlags(self):
        flags = _read(self.ifname, 'flags')
        return int(flags, 16)

    def getAlias(self):
        return _read(self.ifname, 'ifalias')

    def isUp(self):
        return InterfaceFlags(self.getFlags()).up()

    def isPhysical(self):
        return not InterfaceFlags(self.getFlags()).loopback()

    def isLoopback(self):
        return InterfaceFlags(self.getFlags()).loopback()

    def isHalfDuplex(self):
        return self.getDuplex() is 'half'

    def isFullDuplex(self):
        return self.getDuplex() is 'full'

    def isDormant(self):
        return _read(self.ifname, 'dormant')

class InterfaceFlags:
    flags = None

    def __init__(self, flags):
        self.flags = flags;

    def up():          return (1<<0)  & self.flags  # sysfs
    def broadcast():   return (1<<1)  & self.flags  # volatile
	def debug():       return (1<<2)  & self.flags  # sysfs
	def loopback():    return (1<<3)  & self.flags  # volatile
	def pointopoint(): return (1<<4)  & self.flags  # volatile
	def notrailers():  return (1<<5)  & self.flags  # sysfs
	def running():     return (1<<6)  & self.flags  # volatile
	def noarp():       return (1<<7)  & self.flags  # sysfs
	def promisc():     return (1<<8)  & self.flags  # sysfs
	def allmulti():    return (1<<9)  & self.flags  # sysfs
	def master():      return (1<<10) & self.flags  # volatile
	def slave():       return (1<<11) & self.flags  # volatile
	def multicast():   return (1<<12) & self.flags  # sysfs
	def portsel():     return (1<<13) & self.flags  # sysfs
	def automedia():   return (1<<14) & self.flags  # sysfs
	def dynamic():     return (1<<15) & self.flags  # sysfs
	def lower_up():    return (1<<16) & self.flags  # volatile
	def dormant():     return (1<<17) & self.flags  # volatile
	def echo():        return (1<<18) & self.flags  # volatile

# Interface thrown on invalid interfaces
class InvalidInterface(EnvironmentError): pass

# Used to read data from an interface file
def _read(ifname, file):
    fh = open('/sys/class/net/%s/%s' % (ifname, file))
    data = fh.read()
    fh.close()

    return data.rstrip()
