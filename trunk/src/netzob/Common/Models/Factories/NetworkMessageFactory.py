# -*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|         01001110 01100101 01110100 01111010 01101111 01100010             | 
#+---------------------------------------------------------------------------+
#| NETwork protocol modeliZatiOn By reverse engineering                      |
#| ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~+
#| @license      : GNU GPL v3                                                |
#| @copyright    : Georges Bossert and Frederic Guihery                      |
#| @url          : http://code.google.com/p/netzob/                          |
#| ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~+
#| @author       : {gbt,fgy}@amossys.fr                                      |
#| @organization : Amossys, http://www.amossys.fr                            |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+ 
#| Standard library imports
#+---------------------------------------------------------------------------+


#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+
from lxml.etree import ElementTree
from netzob.Common.TypeConvertor import TypeConvertor
from lxml import etree

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| NetworkMessageFactory :
#|     Factory dedicated to the manipulation of network messages
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.2
#| ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~+
#+---------------------------------------------------------------------------+
class NetworkMessageFactory():
    
    @staticmethod
    #+-----------------------------------------------------------------------+
    #| save
    #|     Generate the XML representation of a Network message
    #+-----------------------------------------------------------------------+    
    def save(message, xmlMessages, namespace):
        root = etree.SubElement(xmlMessages, "{" + namespace + "}message")
        root.set("id", str(message.getID()))
        root.set("timestamp", str(message.getTimestamp()))
        root.set("{http://www.w3.org/2001/XMLSchema-instance}type", "netzob:NetworkMessage")
        # data
        subData = etree.SubElement(root, "{" + namespace + "}data")
        subData.text = str(message.getData())
        # ipSource
        subIpSource = etree.SubElement(root, "{" + namespace + "}ip_source")
        subIpSource.text = message.getIPSource()
        # ipTarget
        subIpTarget = etree.SubElement(root, "{" + namespace + "}ip_destination")
        subIpTarget.text = message.getIPDestination()
        # protocol
        subProtocol = etree.SubElement(root, "{" + namespace + "}protocol")
        subProtocol.text = message.getProtocol()
        # l4 source port
        subL4SourcePort = etree.SubElement(root, "{" + namespace + "}l4_source_port")
        subL4SourcePort.text = str(message.getL4SourcePort())
        # l4 target port
        subL4TargetPort = etree.SubElement(root, "{" + namespace + "}l4_destination_port")
        subL4TargetPort.text = str(message.getL4DestinationPort())
        return etree.tostring(root)
    
    @staticmethod
    #+---------------------------------------------------------------------------+
    #| loadFromXML :
    #|     Function which parses an XML and extract from it
    #[     the definition of a network message
    #| @param rootElement: XML root of the network message 
    #| @return an instance of a NetworkMessage
    #| @throw NameError if XML invalid
    #+---------------------------------------------------------------------------+
    def loadFromXML(rootElement, namespace, version):        
        
        # Then we verify its an IPC Message
        if rootElement.get("{http://www.w3.org/2001/XMLSchema-instance}type", "abstract") != "netzob:NetworkMessage" :
            raise NameError("The parsed xml doesn't represent a Network message.")
        
        # Verifies the data field
        if rootElement.find("{" + namespace + "}data") == None or len(rootElement.find("{" + namespace + "}data").text) == 0:
            raise NameError("The parsed message has no data specified")
        
        # Parse the data field and transform it into a byte array
        msg_data = bytearray(rootElement.find("{" + namespace + "}data").text)
        
        # Retrieve the id
        msg_id = rootElement.get("id")
        
        # Retrieve the timestamp
        msg_timestamp = int(rootElement.get("timestamp"))
        
        # Retrieves the ip source
        msg_ipSource = rootElement.find("{" + namespace + "}ip_source").text
            
        # Retrieves the ip target
        msg_ipDestination = rootElement.find("{" + namespace + "}ip_destination").text
        
        # Retrieves the protocol
        msg_protocol = rootElement.find("{" + namespace + "}protocol").text
            
        # Retrieves the l4 source port
        msg_l4SourcePort = rootElement.find("{" + namespace + "}l4_source_port").text
            
        # Retrieves the l4 target port (default 0)
        msg_l4TargetPort = rootElement.find("{" + namespace + "}l4_destination_port").text
        
        # TODO : verify this ! Circular imports in python !      
        # WARNING : verify this ! Circular imports in python !  
        from netzob.Common.Models.NetworkMessage import NetworkMessage
        
        result = NetworkMessage(msg_id, msg_timestamp, msg_data, msg_ipSource, msg_ipDestination, msg_protocol, msg_l4SourcePort, msg_l4TargetPort)

        return result
    
    
