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
from lxml.etree import ElementTree

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+
from netzob.Common.TypeConvertor import TypeConvertor
from lxml import etree


#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| RawMessageFactory :
#|     Factory dedicated to the manipulation of raw messages
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.2
#| ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~+
#| XML Definition :
#| <message type="RAW" id="" timestamp="">
#|     <data></data>
#| </message>
#+---------------------------------------------------------------------------+
class RawMessageFactory():
    
    @staticmethod
    #+-----------------------------------------------------------------------+
    #| save
    #|     Generate the XML representation of a Network message
    #+-----------------------------------------------------------------------+    
    def save(message, xmlMessages, namespace):
        root = etree.SubElement(xmlMessages, "{" + namespace + "}message")
        root.set("id", str(message.getID()))
        root.set("timestamp", str(message.getTimestamp()))
        root.set("{http://www.w3.org/2001/XMLSchema-instance}type", "netzob:RawMessage")
        # data
        subData = etree.SubElement(root, "data")
        subData.text = str(message.getData())
        
    
    @staticmethod
    #+---------------------------------------------------------------------------+
    #| loadFromXML :
    #|     Function which parses an XML and extract from it
    #[     the definition of a RAW message
    #| @param rootElement: XML root of the RAW message 
    #| @return an instance of a n IPC Message
    #| @throw NameError if XML invalid
    #+---------------------------------------------------------------------------+
    def loadFromXML(rootElement, namespace, version):        
        # Then we verify its an IPC Message
        if rootElement.get("{http://www.w3.org/2001/XMLSchema-instance}type", "abstract") != "netzob:RawMessage" :
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
      
        from netzob.Common.Models.RawMessage import RawMessage
        result = RawMessage(msg_id, msg_timestamp, msg_data)
        
        
        return result
   
