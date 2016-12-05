# Copyright (c) 2003-2013 CORE Security Technologies
#
# This software is provided under under a slightly modified version
# of the Apache Software License. See the accompanying LICENSE file
# for more information.
#
# Description:
#  Convenience packet unpackers for various network protocols
#  implemented in the ImpactPacket module.
#
# Author:
#  Javier Burroni (javier)
#  Bruce Leidl (brl)
#  Aureliano Calvo

from netzob.Import.PCAPImporter import ImpactPacket

"""Classes to convert from raw packets into a hierarchy of
ImpactPacket derived objects.

The protocol of the outermost layer must be known in advance, and the
packet must be fed to the corresponding decoder. From there it will
try to decode the raw data into a hierarchy of ImpactPacket derived
objects; if a layer's protocol is unknown, all the remaining data will
be wrapped into a ImpactPacket.Data object.
"""

class Decoder:
    __decoded_protocol = None
    def decode(self, aBuffer):
        pass
        
    def set_decoded_protocol(self, protocol):
        self.__decoded_protocol = protocol
        
    def get_protocol(self, aprotocol):
        protocol = self.__decoded_protocol
        while protocol:
            if protocol.__class__ == aprotocol:
                break
            protocol=protocol.child()
        return protocol
    
    def __str__(self):
        protocol = self.__decoded_protocol
        i=0
        out=''
        while protocol:
            tabline=' '*i+'+-'+str(protocol.__class__)
            out+="%s"%tabline+'\n'
            protocol=protocol.child()
            i+=1
        return out

class EthDecoder(Decoder):
    def __init__(self):
        pass

    def decode(self, aBuffer):
        e = ImpactPacket.Ethernet(aBuffer)
        self.set_decoded_protocol( e )
        off = e.get_header_size()
        if e.get_ether_type() == ImpactPacket.IP.ethertype:
            self.ip_decoder = IPDecoder()
            packet = self.ip_decoder.decode(aBuffer[off:])
        elif e.get_ether_type() == IP6.IP6.ethertype:
            self.ip6_decoder = IP6Decoder()
            packet = self.ip6_decoder.decode(aBuffer[off:])
        elif e.get_ether_type() == ImpactPacket.ARP.ethertype:
            self.arp_decoder = ARPDecoder()
            packet = self.arp_decoder.decode(aBuffer[off:])
        # LLC ?
        elif e.get_ether_type() < 1500:
            self.llc_decoder = LLCDecoder()
            packet = self.llc_decoder.decode(aBuffer[off:])
        else:
            self.data_decoder = DataDecoder()
            packet = self.data_decoder.decode(aBuffer[off:])

        e.contains(packet)
        return e

# Linux "cooked" capture encapsulation.
# Used, for instance, for packets returned by the "any" interface.
class LinuxSLLDecoder(Decoder):
    def __init__(self):
        pass

    def decode(self, aBuffer):
        e = ImpactPacket.LinuxSLL(aBuffer)
        self.set_decoded_protocol( e )
        off = 16
        if e.get_ether_type() == ImpactPacket.IP.ethertype:
            self.ip_decoder = IPDecoder()
            packet = self.ip_decoder.decode(aBuffer[off:])
        elif e.get_ether_type() == ImpactPacket.ARP.ethertype:
            self.arp_decoder = ARPDecoder()
            packet = self.arp_decoder.decode(aBuffer[off:])
        else:
            self.data_decoder = DataDecoder()
            packet = self.data_decoder.decode(aBuffer[off:])

        e.contains(packet)
        return e

class IPDecoder(Decoder):
    def __init__(self):
        pass

    def decode(self, aBuffer):
        i = ImpactPacket.IP(aBuffer)
        self.set_decoded_protocol ( i )
        off = i.get_header_size()
        end = i.get_ip_len()
        if i.get_ip_p() == ImpactPacket.UDP.protocol:
            self.udp_decoder = UDPDecoder()
            packet = self.udp_decoder.decode(aBuffer[off:end])
        elif i.get_ip_p() == ImpactPacket.TCP.protocol:
            self.tcp_decoder = TCPDecoder()
            packet = self.tcp_decoder.decode(aBuffer[off:end])
        elif i.get_ip_p() == ImpactPacket.ICMP.protocol:
            self.icmp_decoder = ICMPDecoder()
            packet = self.icmp_decoder.decode(aBuffer[off:end])
        else:
            self.data_decoder = DataDecoder()
            packet = self.data_decoder.decode(aBuffer[off:end])
        i.contains(packet)
        return i

class HopByHopDecoder(Decoder):
    def __init__(self):
        pass

    def decode(self, buffer):
        hop_by_hop = IP6_Extension_Headers.Hop_By_Hop(buffer)
        self.set_decoded_protocol(hop_by_hop)
        start_pos = hop_by_hop.get_header_size()
        contained_protocol = hop_by_hop.get_next_header()

        multi_protocol_decoder = IP6MultiProtocolDecoder(contained_protocol)
        child_packet = multi_protocol_decoder.decode(buffer[start_pos:])
        
        hop_by_hop.contains(child_packet)
        return hop_by_hop

class DestinationOptionsDecoder(Decoder):
    def __init__(self):
        pass

    def decode(self, buffer):
        destination_options = IP6_Extension_Headers.Destination_Options(buffer)
        self.set_decoded_protocol(destination_options)
        start_pos = destination_options.get_header_size()
        contained_protocol = destination_options.get_next_header()

        multi_protocol_decoder = IP6MultiProtocolDecoder(contained_protocol)
        child_packet = multi_protocol_decoder.decode(buffer[start_pos:])
        
        destination_options.contains(child_packet)
        return destination_options

class RoutingOptionsDecoder(Decoder):
    def __init__(self):
        pass

    def decode(self, buffer):
        routing_options = IP6_Extension_Headers.Routing_Options(buffer)
        self.set_decoded_protocol(routing_options)
        start_pos = routing_options.get_header_size()
        contained_protocol = routing_options.get_next_header()

        multi_protocol_decoder = IP6MultiProtocolDecoder(contained_protocol)
        child_packet = multi_protocol_decoder.decode(buffer[start_pos:])
        
        routing_options.contains(child_packet)
        return routing_options

class ARPDecoder(Decoder):
    def __init__(self):
        pass

    def decode(self, aBuffer):
        arp = ImpactPacket.ARP(aBuffer)
        self.set_decoded_protocol( arp )
        off = arp.get_header_size()
        self.data_decoder = DataDecoder()
        packet = self.data_decoder.decode(aBuffer[off:])
        arp.contains(packet)
        return arp

class UDPDecoder(Decoder):
    def __init__(self):
        pass

    def decode(self, aBuffer):
        u = ImpactPacket.UDP(aBuffer)
        self.set_decoded_protocol( u )
        off = u.get_header_size()
        self.data_decoder = DataDecoder()
        packet = self.data_decoder.decode(aBuffer[off:])
        u.contains(packet)
        return u

class TCPDecoder(Decoder):
    def __init__(self):
        pass

    def decode(self, aBuffer):
        t = ImpactPacket.TCP(aBuffer)
        self.set_decoded_protocol( t )
        off = t.get_header_size()
        self.data_decoder = DataDecoder()
        packet = self.data_decoder.decode(aBuffer[off:])
        t.contains(packet)
        return t

class IPDecoderForICMP(Decoder):
    """This class was added to parse the IP header of ICMP unreachables packets
    If you use the "standard" IPDecoder, it might crash (see bug #4870) ImpactPacket.py
    because the TCP header inside the IP header is incomplete"""    
    def __init__(self):
        pass

    def decode(self, aBuffer):
        i = ImpactPacket.IP(aBuffer)
        self.set_decoded_protocol( i )
        off = i.get_header_size()
        if i.get_ip_p() == ImpactPacket.UDP.protocol:
            self.udp_decoder = UDPDecoder()
            packet = self.udp_decoder.decode(aBuffer[off:])
        else:
            self.data_decoder = DataDecoder()
            packet = self.data_decoder.decode(aBuffer[off:])
        i.contains(packet)
        return i

class ICMPDecoder(Decoder):
    def __init__(self):
        pass

    def decode(self, aBuffer):
        ic = ImpactPacket.ICMP(aBuffer)
        self.set_decoded_protocol( ic )
        off = ic.get_header_size()
        if ic.get_icmp_type() == ImpactPacket.ICMP.ICMP_UNREACH:
            self.ip_decoder = IPDecoderForICMP()
            packet = self.ip_decoder.decode(aBuffer[off:])
        else:
            self.data_decoder = DataDecoder()
            packet = self.data_decoder.decode(aBuffer[off:])
        ic.contains(packet)
        return ic

class DataDecoder(Decoder):
    def decode(self, aBuffer):
        d = ImpactPacket.Data(aBuffer)
        self.set_decoded_protocol( d )
        return d

class BaseDecoder(Decoder):
    
    def decode(self, buff):
        
        packet = self.klass(buff)
        self.set_decoded_protocol(packet)
        cd = self.child_decoders.get(self.child_key(packet), DataDecoder())
        packet.contains(cd.decode(packet.get_body_as_string()))
        return packet
