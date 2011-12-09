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
from xml.etree import ElementTree

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| IPCMessageFactory :
#|     Factory dedicated to the manipulation of IPC messages
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.2
#| ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~+
#| XML Definition :
#| <message type="IPC" id="">
#|     <category></category>
#|     <key></key>
#|     <name></name>
#|     <type></type>
#|     <direction></direction> 
#|     <timestamp></timestamp>
#|     <data></data>
#| </message>
#+---------------------------------------------------------------------------+
class IPCMessageFactory():
    
    @staticmethod
    #+-----------------------------------------------------------------------+
    #| save
    #|     Generate the XML representation of an IPC message
    #+-----------------------------------------------------------------------+    
    def save(message, xmlMessages, namespace):
        root = ElementTree.SubElement(xmlMessages, "{" + namespace + "}message")
        root.set("id", str(message.getID()))
        root.set("timestamp", str(message.getTimestamp()))
        root.set("{http://www.w3.org/2001/XMLSchema-instance}type", "netzob:IPCMessage")
        # data
        subData = ElementTree.SubElement(root, "{" + namespace + "}data")
        subData.text = str(message.getData())
        # category
        subCategory = ElementTree.SubElement(root, "{" + namespace + "}category")
        subCategory.text = str(message.getCategory())
        # key
        subKey = ElementTree.SubElement(root, "{" + namespace + "}key")
        subKey.text = str(message.getKey())
        # type
        subType = ElementTree.SubElement(root, "{" + namespace + "}type")
        subType.text = str(message.getType())
        # direction
        subDirection = ElementTree.SubElement(root, "{" + namespace + "}direction")
        subDirection.text = str(message.getDirection())
        
    
    @staticmethod
    #+---------------------------------------------------------------------------+
    #| loadFromXML :
    #|     Function which parses an XML and extract from it
    #[     the definition of an IPC message
    #| @param rootElement: XML root of the IPC message 
    #| @return an instance of a n IPC Message
    #| @throw NameError if XML invalid
    #+---------------------------------------------------------------------------+
    def loadFromXML(rootElement, namespace, version):        
        # Then we verify its an IPC Message
        if rootElement.get("{http://www.w3.org/2001/XMLSchema-instance}type", "abstract") != "netzob:IPCMessage" :
            raise NameError("The parsed xml doesn't represent an IPC message.")
        
        # Verifies the data field
        if rootElement.find("{" + namespace + "}data") == None or len(rootElement.find("{" + namespace + "}data").text) == 0:
            raise NameError("The parsed message has no data specified")
        
        # Parse the data field and transform it into a byte array
        msg_data = bytearray(rootElement.find("{" + namespace + "}data").text)
        
        # Retrieve the id
        msg_id = rootElement.get("id")
        
        # Retrieve the timestamp
        msg_timestamp = int(rootElement.get("timestamp"))
        
        # Retrieves the category
        msg_category = rootElement.find("{" + namespace + "}category").text
       
        # Retrieves the key
        msg_key = rootElement.find("{" + namespace + "}key").text
        
        # Retrieves the type
        msg_type = rootElement.find("{" + namespace + "}type").text
            
        # Retrieves the direction
        msg_direction = rootElement.find("{" + namespace + "}direction").text
        
        
        
        # TODO : verify this ! Circular imports in python !      
        # WARNING : verify this ! Circular imports in python !  
        from netzob.Common.Models.IPCMessage import IPCMessage
        
        result = IPCMessage(msg_id, msg_timestamp, msg_data, msg_category, msg_key, msg_direction)
        
        return result
    
    
