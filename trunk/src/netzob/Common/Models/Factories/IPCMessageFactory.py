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
import uuid

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
    #| saveInXML
    #|     Generate the XML representation of an IPC message
    #| @return a string which include the xml definition of the msg
    #+-----------------------------------------------------------------------+    
    def saveInXML(message):
        root = ElementTree.Element("message")
        root.set("type", "IPC")
        root.set("id", str(message.getID()))
        # category
        subCategory = ElementTree.SubElement(root, "category")
        subCategory.text = str(message.getCategory())
        # key
        subKey = ElementTree.SubElement(root, "key")
        subKey.text = str(message.getKey())
        # name
        subName = ElementTree.SubElement(root, "name")
        subName.text = message.getName()
        # type
        subType = ElementTree.SubElement(root, "type")
        subType.text = message.getType()
        # direction
        subDirection = ElementTree.SubElement(root, "direction")
        subDirection.text = message.getDirection()
        # timestamp
        subTimestamp = ElementTree.SubElement(root, "timestamp")
        subTimestamp.text = str(message.getTimestamp())
        # data
        subData = ElementTree.SubElement(root, "data")
        subData.text = str(message.getData())
        return ElementTree.tostring(root)
    
    @staticmethod
    #+---------------------------------------------------------------------------+
    #| loadFromXML :
    #|     Function which parses an XML and extract from it
    #[     the definition of an IPC message
    #| @param rootElement: XML root of the IPC message 
    #| @return an instance of a n IPC Message
    #| @throw NameError if XML invalid
    #+---------------------------------------------------------------------------+
    def loadFromXML(rootElement):        
        # First we verify rootElement is a message
        if rootElement.tag != "message" :
            raise NameError("The parsed xml doesn't represent a message.")
        # Then we verify its an IPC Message
        if rootElement.get("type", "abstract") != "IPC" :
            raise NameError("The parsed xml doesn't represent an IPC message.")
        # Verifies the data field
        if rootElement.find("data") == None or len(rootElement.find("data").text) == 0:
            raise NameError("The parsed message has no data specified")
        
        # Parse the data field and transform it into a byte array
        msg_data = bytearray(rootElement.find("data").text)
        
        # Retrieve the id (default = -1)
        msg_id = rootElement.get('id', "-1")
        
        if msg_id == "-1" :
            msg_id = str(uuid.uuid4()) 
        
        # Retrieves the category (default none)
        if rootElement.find("category") != None :
            msg_category = rootElement.find("category").text
        else :
            msg_category = "none"
            
        # Retrieves the key (default none)
        if rootElement.find("key") != None :
            msg_key = rootElement.find("key").text
        else :
            msg_key = "none"
            
        # Retrieves the name (default none)
        if rootElement.find("name") != None :
            msg_name = rootElement.find("name").text
        else :
            msg_name = "none"
        
        # Retrieves the type (default none)
        if rootElement.find("type") != None :
            msg_type = rootElement.find("type").text
        else :
            msg_type = "none"
            
        # Retrieves the direction (default none)
        if rootElement.find("direction") != None :
            msg_direction = rootElement.find("direction").text
        else :
            msg_direction = "none"
        
        # Retrieves the timestamp (default -1)
        if rootElement.find("timestamp") != None :
            msg_timestamp = int(rootElement.find("timestamp").text)
        else :
            msg_timestamp = -1
              
        
        # TODO : verify this ! Circular imports in python !      
        # WARNING : verify this ! Circular imports in python !  
        from .. import IPCMessage
        
        result = IPCMessage.IPCMessage()
        result.setID(msg_id)
        result.setData(msg_data)
        result.setCategory(msg_category)
        result.setKey(msg_key)
        result.setName(msg_name)
        result.setType(msg_type)
        result.setDirection(msg_direction)
        result.setTimestamp(msg_timestamp)
        
        
        return result
    
    
