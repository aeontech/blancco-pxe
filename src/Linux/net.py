import fcntl
import ctypes
import socket
import struct

from os import path
from glob import glob
from binascii import hexlify

IPv4 = socket.AF_INET
IPv6 = socket.AF_INET6

class Interfaces:
    @staticmethod
    def getEthernet():
        return [iface for iface in Interfaces.getPhysical() if iface.isEthernet()]

    @staticmethod
    def getPhysical():
        return [iface for iface in Interfaces.getInterfaces() if iface.isPhysical()]

    @staticmethod
    def getInterfaces():
        return [Interface(path.basename(iface)) for iface in glob('/sys/class/net/*')]

    @staticmethod
    def isValidInterface(name):
        return path.isdir('/sys/class/net/%s/' % name)

class Interface:
    ifname = None
    sock = None

    def __init__(self, name):
        if not Interfaces.isValidInterface(name):
            raise InvalidInterface('Interface "%s" does not exist.' % name)

        self.ifname = name
        self.sock   = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def getName(self):
        """
        Returns the name of the interface
        """
        return self.ifname

    # Retrieves the MAC address
    def getAddress(self):
        """
        Returns the L2/MAC address of the interface
        """
        return self._read('address')

    def getBroadcast(self):
        """
        Returns the L2 broadcast address of the interface
        """
        return self._read('broadcast')

    def getDevId(self):
        """
        Returns the Linux Device ID associated with this interface
        """
        return self._read('dev_id')

    def getDuplex(self):
        """
        Returns 'half' or 'full' depending upon the specified duplex
        of the interface
        """
        return self._read('duplex')

    def getFlags(self):
        """
        Returns an integer representing the flags set on this interface
        """
        flags = self._read('flags')
        return int(flags, 16)

    def getAlias(self):
        """
        Returns the alias associated to the interface
        """
        return self._read('ifalias')

    def getIndex(self):
        """
        Returns the system-wide index associated with this interface
        """
        return int(self._read('ifindex'))

    def getLinkMode(self):
        """
        Returns the link mode associated with this interface

        0: Default link mode
        1: Dormant link mode
        """
        return int(self._read('link_mode'))

    def getMTU(self):
        """
        Returns the integer MTU value configured for this interface
        """
        return int(self._read('mtu'))

    def getDeviceGroup(self):
        """
        Returns the network device group associated with this interface
        """
        return int(self._read('netdev_group'))

    def getState(self):
        """
        Returns the RFC 2863 operational state of this interface
        """
        return self._read('operstate')

    def getPortID(self):
        """
        Returns the interface physical port identifier within the NIC
        """
        try:
            return self._read('phys_port_id')
        except:
            raise InvalidOperation('%s::phys_port_id not working!' % self.ifname)

    def getPortName(self):
        """
        Returns the interface physical port name within the NIC
        """
        try:
            return self._read('phys_port_name')
        except:
            raise InvalidOperation('%s::phys_port_name not working!' % self.ifname)

    def getSpeed(self):
        """
        Returns the current speed associated with this interface
        """
        return self._read('speed')

    def getTxQueueLen(self):
        """
        Returns the overall length of the TX queue associated with
        this interface
        """
        return int(self._read('tx_queue_len'))

    def getType(self):
        """
        Returns the interface protocol associated with this interface

        This protocol can be compared against net.InterfaceType to
        determine the L2 protocol this interface supports
        """
        return int(self._read('type'))

    def getSwitchID(self):
        """
        Returns the physical switch identifier of a switch this port
        belongs to, as a string
        """
        try:
            return self._read('phys_switch_id')
        except:
            raise InvalidOperation('%s::phys_switch_id not working!' % self.ifname)

    # And now our ioctl functions
    def getIpAddress(self):
        """
        Returns the L3/IP address associated with this interface
        """
        try:
            buff = self._ioctl(SIOC.GIFADDR)
            ifr  = ifreq.unpack(buff)

            return self._sockToStr(ifr.data.ifr_addr)
        except:
            return False

    def getNetmask(self):
        """
        Returns the L3 network mask associated with this interface
        """
        try:
            buff = self._ioctl(SIOC.GIFNETMASK)
            ifr  = ifreq.unpack(buff)

            return self._sockToStr(ifr.data.ifr_addr)
        except:
            return False

    def getMetric(self):
        """
        Returns the metric associated with this interface
        """
        try:
            buff = self._ioctl(SIOC.GIFMETRIC)
            ifr  = ifreq.unpack(buff)

            return ifr.data.ifr_metric
        except:
            return False

    # Now for our checking functions
    def isUp(self):
        """
        Returns true if the interface is currently in an UP state
        """
        return InterfaceFlags(self.getFlags()).up()

    def isPhysical(self):
        """
        Returns true if this interface is associated with a physical
        interface on this machine
        """
        return not InterfaceFlags(self.getFlags()).loopback()

    def isLoopback(self):
        """
        Returns true if the logical interface is a loopback
        """
        return InterfaceFlags(self.getFlags()).loopback()

    def isEthernet(self):
        """
        Returns true if the interface implements an Ethernet protocol
        """
        return InterfaceType(self.getType()).is_ether()

    def isHalfDuplex(self):
        """
        Returns true if the interface is running half duplex
        """
        return self.getDuplex() is 'half'

    def isFullDuplex(self):
        """
        Returns true if the interface is running full duplex
        """
        return self.getDuplex() is 'full'

    def isDormant(self):
        """
        Returns true if the interface is dormant
        """
        return self._read('dormant') is '1'

    # Finally, the fun stuff...
    def setName(self, name):
        """
        Set the name of the interface while it is DOWN
        """
        ifr = self._ifreq()
        ifr.data.ifr_newname = self._cbytes(name, IFNAMSIZ)

        try:
            self._ioctl(SIOC.SIFNAME, ifr)
            self.ifname = name
        except:
            return False

        return True

    def setIpAddress(self, ip):
        """
        Set the L3/IP address of the interface while it is DOWN
        """

        try:
            if type(ip) == str and self._is_ip4(ip):
                ip = (socket.AF_INET, ip)
            elif type(ip) == str and self._is_ip6(ip):
                ip = (socket.AF_INET6, ip)
            elif type(ip) == str:
                raise ValueError('Invalid IP address format')

            ifr = self._ifreq()
            ifr.data.ifr_addr = self._sockAddrFromTuple(ip)

            return self._ioctl(SIOC.SIFADDR, ifr)
        except:
            return False

    def setNetmask(self, mask):
        """
        Set the L3 network mask of the interface while it is DOWN
        """
        ifr = self._ifreq()
        ifr.data.ifr_addr = self._sockAddrFromTuple(mask)

        return self._ioctl(SIOC.SIFNETMASK, ifr)

    def setUp(self):
        """
        Bring the interface into an UP state
        """
        ifr = self._ifreq()
        ifr.data.ifr_flags = self.getFlags() | 0x1

        return self._ioctl(SIOC.SIFFLAGS, ifr)

    def setDown(self):
        """
        Bring the interface into a DOWN state
        """
        ifr = self._ifreq()
        ifr.data.ifr_flags = self.getFlags() & ~0x1

        return self._ioctl(SIOC.SIFFLAGS, ifr)

    # And some helper functions
    def _ifreq(self):
        ifr  = ifreq()
        ifr.ifr_name = (ctypes.c_ubyte * IFNAMSIZ).from_buffer_copy(self.ifname.ljust(IFNAMSIZ, '\0'))

        return ifr

    def _cbytes(self, val, size):
        return (ctypes.c_ubyte * size).from_buffer_copy(val.ljust(size, '\0'))

    def _sockToStr(self, s_addr):
        if s_addr.gen.sa_family == 0:
            return 'None'

        if s_addr.gen.sa_family == socket.AF_INET:
            sin_addr = s_addr.in4.sin_addr.s_addr
        elif s_addr.gen.sa_family == socket.AF_INET6:
            sin_addr = s_addr.in6.sin6_addr.in6_u
        else:
            raise RuntimeError('Unsupported socket address family "%d"' % s_addr.gen.sa_family)

        p = struct.pack('<L', sin_addr)
        return socket.inet_ntop(s_addr.gen.sa_family, p)

    def _sockAddrFromTuple(self, ip):
        addr = sockaddr()

        if (ip[0] == socket.AF_INET):
            addr.in4.sa_family = socket.AF_INET
            addr.in4.sin_addr.s_addr = \
                struct.unpack('<L', socket.inet_pton(ip[0], ip[1]))[0]
        elif (ip[0] == socket.AF_INET6):
            addr.in6.sa_family = socket.AF_INET6
            addr.in6.sin6_addr.in6_u = \
                hexlify(socket.inet_pton(ip[0], ip[1]))
        else:
            raise ValueError("Input must be tuple like (net.IPv4, '127.0.0.1')")

        return addr

    # Used to read data from an interface file
    def _read(self, file):
        fh = open('/sys/class/net/%s/%s' % (self.ifname, file))
        data = fh.read()
        fh.close()

        return data.rstrip()

    def _ioctl(self, SIOC, ifr=None):
        if ifr is None:
            ifr = struct.pack('256s', self.ifname[:15])

        return fcntl.ioctl(self.sock, SIOC, ifr)

    def _is_ip4(self, ip):
        try:
            parts = ip.split('.')

            # We should have exactly 4 parts
            if not len(parts) == 4:
                return False

            # The start or end should not be 0
            if parts[0] == '0' or parts[3] == '0':
                return False

            # Test each octet
            for octet in parts:
                # Octet can not be empty
                if octet == '':
                    return False

                # Octet can not have a leading zero unless it is just zero
                if octet[:1] == '0' and len(octet) > 1:
                    return False

                octet = int(octet, 10)
                # Octet must be between 0 and 255 (inclusively)
                if octet < 0 or octet > 255:
                    return False

            # We are good
            return True
        except:
            return False

    def _is_ip6(self, ip):
        try:
            parts = ip.split(':')

            # We must never have more than one substitution
            if ip.count('::') > 1:
                return False

            # We must have 8 octets
            if len(parts) > 8:
                return False

            if len(parts) < 8 and ip.count('::') == 0:
                return False

            for octet in parts:
                if octet == '':
                    continue

                # Octet can not have a leading zero unless it is just zero
                if octet[:1] == '0' and len(octet) > 1:
                    return False

                octet = int(octet, 16)
                if octet < 0 or octet > 0xffff:
                    return False

            # We are good
            return True
        except:
            return False

class InterfaceFlags:
    flags = None

    def __init__(self, flags):
        self.flags = flags

    def up(self):          return (1<<0)  & self.flags  # sysfs
    def broadcast(self):   return (1<<1)  & self.flags  # volatile
    def debug(self):       return (1<<2)  & self.flags  # sysfs
    def loopback(self):    return (1<<3)  & self.flags  # volatile
    def pointopoint(self): return (1<<4)  & self.flags  # volatile
    def notrailers(self):  return (1<<5)  & self.flags  # sysfs
    def running(self):     return (1<<6)  & self.flags  # volatile
    def noarp(self):       return (1<<7)  & self.flags  # sysfs
    def promisc(self):     return (1<<8)  & self.flags  # sysfs
    def allmulti(self):    return (1<<9)  & self.flags  # sysfs
    def master(self):      return (1<<10) & self.flags  # volatile
    def slave(self):       return (1<<11) & self.flags  # volatile
    def multicast(self):   return (1<<12) & self.flags  # sysfs
    def portsel(self):     return (1<<13) & self.flags  # sysfs
    def automedia(self):   return (1<<14) & self.flags  # sysfs
    def dynamic(self):     return (1<<15) & self.flags  # sysfs
    def lower_up(self):    return (1<<16) & self.flags  # volatile
    def dormant(self):     return (1<<17) & self.flags  # volatile
    def echo(self):        return (1<<18) & self.flags  # volatile

class InterfaceType:
    type = None

    def __init__(self, type):
        self.type = type

    # ARP protocol HARDWARE identifiers
    def is_netrom(self):    return self.type is 0       # from KA9Q: NET/ROM pseudo
    def is_ether(self):     return self.type is 1       # Ethernet 10Mbps
    def is_eether(self):    return self.type is 2       # Experimental Ethernet
    def is_ax25(self):      return self.type is 3       # AX.25 Level 2
    def is_pronet(self):    return self.type is 4       # PROnet token ring
    def is_chaos(self):     return self.type is 5       # Chaosnet
    def is_ieee802(self):   return self.type is 6       # IEEE 802.2 Ethernet/TR/TB
    def is_arcnet(self):    return self.type is 7       # ARCnet
    def is_appletlk(self):  return self.type is 8       # APPLEtalk
    def is_dlci(self):      return self.type is 15      # Frame Relay DLCI
    def is_atm(self):       return self.type is 19      # ATM
    def is_metricom(self):  return self.type is 23      # Metricom STRIP (new IANA id)
    def is_ieee1394(self):  return self.type is 24      # IEEE 1394 IPv4 - RFC 2734
    def is_eui64(self):     return self.type is 27      # EUI-64
    def is_infiniband(self):return self.type is 32      # InfiniBand

    # Dummy types for non ARP hardware
    def is_slip(self):      return self.type is 256
    def is_cslip(self):     return self.type is 257
    def is_slip6(self):     return self.type is 258
    def is_cslip6(self):    return self.type is 259
    def is_rsrvd(self):     return self.type is 260     # Notional KISS type
    def is_adapt(self):     return self.type is 264
    def is_rose(self):      return self.type is 270
    def is_x25(self):       return self.type is 271     # CCITT X.25
    def is_hwx25(self):     return self.type is 272     # Boards with X.25 in firmware
    def is_can(self):       return self.type is 280     # Controller Area Network
    def is_ppp(self):       return self.type is 512
    def is_cisco(self):     return self.type is 513     # Cisco HDLC
    def is_hdlc(self):      return self.type is 513
    def is_lapb(self):      return self.type is 516     # LAPB
    def is_ddcmp(self):     return self.type is 517     # Digital's DDCMP protocol
    def is_rawhdlc(self):   return self.type is 518     # Raw HDLC
    def is_rawip(self):     return self.type is 519     # Raw IP
    def is_tunnel(self):    return self.type is 768     # IPIP tunnel
    def is_tunnel6(self):   return self.type is 769     # IP6IP6 tunnel
    def is_frad(self):      return self.type is 770     # Frame Relay Access Device
    def is_skip(self):      return self.type is 771     # SKIP vif
    def is_loopback(self):  return self.type is 772     # Loopback device
    def is_localtlk(self):  return self.type is 773     # Localtalk device
    def is_fddi(self):      return self.type is 774     # Fiber Distributed Data Interfac
    def is_bif(self):       return self.type is 775     # AP1000 BIF
    def is_sit(self):       return self.type is 776     # sit0 device - IPv6-in-IPv
    def is_ipddp(self):     return self.type is 777     # IP over DDP tunneller
    def is_ipgre(self):     return self.type is 778     # GRE over IP
    def is_pimreg(self):    return self.type is 779     # PIMSM register interfac
    def is_hippi(self):     return self.type is 780     # High Performance Parallel Interface
    def is_ash(self):       return self.type is 781     # Nexus 64Mbps Ash
    def is_econet(self):    return self.type is 782     # Acorn Econet
    def is_irda(self):      return self.type is 783     # Linux-IrDA

    # ARP works differently on different FC media .. so
    def is_fcpp(self):      return self.type is 784     # Point to point fibrechannel
    def is_fcal(self):      return self.type is 785     # Fibrechannel arbitrated loop
    def is_fcpl(self):      return self.type is 786     # Fibrechannel public loop
    def is_fcfabric(self):  return self.type is 787     # Fibrechannel fabric

    # 787->799 reserved for fibrechannel media types
    def is_ieee802_tr(self):        return self.type is 800     # Magic type ident for TR
    def is_ieee80211(self):         return self.type is 801     # IEEE 802.11
    def is_ieee80211_prism(self):   return self.type is 802     # IEEE 802.11 + Prism2 header
    def is_ieee80211_radiotap(self):return self.type is 803     # IEEE 802.11 + radiotap header
    def is_ieee802154(self):        return self.type is 804
    def is_ieee802154_monitor(self):return self.type is 805     # IEEE 802.15.4 network monitor

    def is_phonet():        return self.type is 820     # PhoNet media type
    def is_phonet_pipe():   return self.type is 821     # PhoNet pipe header
    def is_caif():          return self.type is 822     # CAIF media type
    def is_ip6gre():        return self.type is 823     # GRE over IPv6
    def is_netlink():       return self.type is 824     # Netlink header
    def is_6lowpan():       return self.type is 825     # IPv6 over LoWPAN
    def is_vsockmon():      return self.type is 826     # Vsock monitor header

    def is_void(): return self.type is 0xFFFF           # oid type, nothing is known
    def is_none(): return self.type is 0xFFFE           # zero header length

class SIOC:
    def __set_attr(self,name,value):
        raise RuntimeError()

    ADDRT = 0x890B      # add routing table entry
    DELRT = 0x890C      # delete routing table entry
    RTMSG = 0x890D      # call to routing system

    GIFNAME         = 0x8910        # get iface name
    SIFLINK         = 0x8911        # set iface channel
    GIFCONF         = 0x8912        # get iface list
    GIFFLAGS        = 0x8913        # get flags
    SIFFLAGS        = 0x8914        # set flags
    GIFADDR         = 0x8915        # get PA address
    SIFADDR         = 0x8916        # set PA address
    GIFDSTADDR      = 0x8917        # get remote PA address
    SIFDSTADDR      = 0x8918        # set remote PA address
    GIFBRDADDR      = 0x8919        # get broadcast PA address
    SIFBRDADDR      = 0x891a        # set broadcast PA address
    GIFNETMASK      = 0x891b        # get network PA mask
    SIFNETMASK      = 0x891c        # set network PA mask
    GIFMETRIC       = 0x891d        # get metric
    SIFMETRIC       = 0x891e        # set metric
    GIFMEM          = 0x891f        # get memory address (BSD)
    SIFMEM          = 0x8920        # set memory address (BSD)
    GIFMTU          = 0x8921        # get MTU size
    SIFMTU          = 0x8922        # set MTU size
    SIFNAME         = 0x8923        # set interface name
    SIFHWADDR       = 0x8924        # set hardware address
    GIFENCAP        = 0x8925        # get/set encapsulations
    SIFENCAP        = 0x8926
    GIFHWADDR       = 0x8927        # Get hardware address
    GIFSLAVE        = 0x8929        # Driver slaving support
    SIFSLAVE        = 0x8930
    ADDMULTI        = 0x8931        # Multicast address lists
    DELMULTI        = 0x8932
    GIFINDEX        = 0x8933        # name -> if_index mapping
    IFINDEX         = GIFINDEX      # misprint compatibility :-)
    SIFPFLAGS       = 0x8934        # set/get extended flags set
    GIFPFLAGS       = 0x8935
    DIFADDR         = 0x8936        # delete PA address
    SIFHWBROADCAST  = 0x8937        # set hardware broadcast addr
    GIFCOUNT        = 0x8938        # get number of devices
    GIFBR           = 0x8940        # Bridging support
    SIFBR           = 0x8941        # Set bridging options
    GIFTXQLEN       = 0x8942        # Get the tx queue length
    SIFTXQLEN       = 0x8943        # Set the tx queue length

    DARP  = 0x8953      # delete ARP table entry
    GARP  = 0x8954      # get ARP table entry
    SARP  = 0x8955      # set ARP table entry

    DRARP = 0x8960      # delete RARP table entry
    GRARP = 0x8961      # get RARP table entry
    SRARP = 0x8962      # set RARP table entry


IFNAMSIZ    = 16
IFHWADDRLEN = 6

class in_addr(ctypes.Structure):
    _pack_   = 1
    _fields_ = [
        ('s_addr', ctypes.c_uint32),
    ]

    @staticmethod
    def unpack(data):
        return in_addr.from_buffer_copy(data)

class in6_u(ctypes.Union):
    _pack_   = 1
    _fields_ = [
        ('u6_addr8',  (ctypes.c_uint8 * 16)),
        ('u6_addr16', (ctypes.c_uint16 * 8)),
        ('u6_addr32', (ctypes.c_uint32 * 4)),
    ]

    @staticmethod
    def unpack(data):
        return in6_u.from_buffer_copy(data)

class in6_addr(ctypes.Structure):
    _pack_   = 1
    _fields_ = [
        ('in6_u', in6_u),
    ]

    @staticmethod
    def unpack(data):
        return in6_addr.from_buffer_copy(data)

class sockaddr_gen(ctypes.Structure):
    _fields_ = [
        ('sa_family', ctypes.c_uint16),
        ('sa_data',   (ctypes.c_uint8 * 22)),
    ]

    @staticmethod
    def unpack(data):
        return sockaddr_gen.from_buffer_copy(data)

class sockaddr_in(ctypes.Structure):
    _pack_   = 1
    _fields_ = [
        ('sin_family', ctypes.c_ushort),
        ('sin_port',   ctypes.c_ushort),
        ('sin_addr',   in_addr),
        ('sin_zero',   (ctypes.c_uint8 * 16)), # padding
    ]

    @staticmethod
    def unpack(data):
        return sockaddr_in.from_buffer_copy(data)

class sockaddr_in6(ctypes.Structure):
    _pack_   = 1
    _fields_ = [
        ('sin6_family',   ctypes.c_ushort),
        ('sin6_port',     ctypes.c_ushort),
        ('sin6_flowinfo', ctypes.c_uint32),
        ('sin6_addr',     in6_addr),
        ('sin6_scope_id', ctypes.c_uint32),
    ]

    @staticmethod
    def unpack(data):
        return sockaddr_in6.from_buffer_copy(data)

class sockaddr(ctypes.Union):
    _pack_   = 1
    _fields_ = [
        ('gen', sockaddr_gen),
        ('in4', sockaddr_in),
        ('in6', sockaddr_in6),
    ]

    @staticmethod
    def unpack(data):
        return sockaddr.from_buffer_copy(data)

class ifmap(ctypes.Structure):
    _pack_   = 1
    _fields_ = [
        ('mem_start', ctypes.c_ulong),
        ('mem_end',   ctypes.c_ulong),
        ('base_addr', ctypes.c_ushort),
        ('irq',       ctypes.c_ubyte),
        ('dma',       ctypes.c_ubyte),
        ('port',      ctypes.c_ubyte),
    ]

    @staticmethod
    def unpack(data):
        return ifmap.from_buffer_copy(data)

class ifr_data(ctypes.Union):
    _pack_   = 1
    _fields_ = [
        ('ifr_addr',      sockaddr),
        ('ifr_dstaddr',   sockaddr),
        ('ifr_broadaddr', sockaddr),
        ('ifr_netmask',   sockaddr),
        ('ifr_hwaddr',    sockaddr),
        ('ifr_flags',     ctypes.c_short),
        ('ifr_ifindex',   ctypes.c_int),
        ('ifr_ifqlen',    ctypes.c_int),
        ('ifr_metric',    ctypes.c_int),
        ('ifr_mtu',       ctypes.c_int),
        ('ifr_map',       ifmap),
        ('ifr_slave',     (ctypes.c_ubyte * IFNAMSIZ)),
        ('ifr_newname',   (ctypes.c_ubyte * IFNAMSIZ)),
        ('ifr_data',      ctypes.c_void_p),
    ]

    @staticmethod
    def unpack(data):
        return ifr_data.from_buffer_copy(data)

class ifreq(ctypes.Structure):
    _pack_   = 1
    _fields_ = [
        ('ifr_name', (ctypes.c_ubyte * IFNAMSIZ)),
        ('data',     ifr_data),
    ]

    @staticmethod
    def unpack(data):
        return ifreq.from_buffer_copy(data)

class InvalidInterface(EnvironmentError): pass
class InvalidOperation(EnvironmentError): pass
