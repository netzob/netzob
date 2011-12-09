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
import re
import datetime

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+
from xml.etree import ElementTree
from netzob.Common.TypeConvertor import TypeConvertor

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+


#+---------------------------------------------------------------------------+
#| FileMessageFactory :
#|     Factory dedicated to the manipulation of file messages
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.2
#| ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~+
#| XML Definition
#| <message type="file" id="" timestamp="">
#|     <data></data>
#|     <lineNumber></lineNumber>
#|     <filename></filename>
#|     <creationDate></creationDate>
#|     <modificationDate></modificationDate>
#|     <owner></owner> 
#|     <size></size>
#|     <data></data>
#| </message>
#+---------------------------------------------------------------------------+
class FileMessageFactory():
    
    @staticmethod
    #+-----------------------------------------------------------------------+
    #| saveInXML
    #|     Generate the XML representation of a file message
    #| @return a string which include the xml definition of the file msg
    #+-----------------------------------------------------------------------+    
    def save(message, xmlMessages, namespace):
        root = ElementTree.SubElement(xmlMessages, "{" + namespace + "}message")
        root.set("id", str(message.getID()))
        root.set("timestamp", str(message.getTimestamp()))
        root.set("{http://www.w3.org/2001/XMLSchema-instance}type", "netzob:FileMessage")
        # data
        subData = ElementTree.SubElement(root, "{" + namespace + "}data")
        subData.text = str(message.getData())
        # line number
        subLineNumber = ElementTree.SubElement(root, "{" + namespace + "}lineNumber")
        subLineNumber.text = str(message.getLineNumber())
        # filename
        subFilename = ElementTree.SubElement(root, "{" + namespace + "}filename")
        subFilename.text = str(message.getFilename())
        # creationDate
        subCreationDate = ElementTree.SubElement(root, "{" + namespace + "}creationDate")
        subCreationDate.text = TypeConvertor.pythonDatetime2XSDDatetime(message.getCreationDate())
        # creationDate
        subModificationDate = ElementTree.SubElement(root, "{" + namespace + "}modificationDate")
        subModificationDate.text = TypeConvertor.pythonDatetime2XSDDatetime(message.getModificationDate())
        
        # owner
        subOwner = ElementTree.SubElement(root, "{" + namespace + "}owner")
        subOwner.text = message.getOwner()
        # size
        subSize = ElementTree.SubElement(root, "{" + namespace + "}size")
        subSize.text = str(message.getSize())
        
        
    
    @staticmethod
    #+---------------------------------------------------------------------------+
    #| loadFromXML :
    #|     Function which parses an XML and extract from it
    #[     the definition of a file message
    #| @param rootElement: XML root of the file message 
    #| @return an instance of a FipSource (default 0.0.0.0)ileMessage
    #| @throw NameError if XML invalid
    #+---------------------------------------------------------------------------+
    def loadFromXML(rootElement, namespace, version):        
        
        # Then we verify its an IPC Message
        if rootElement.get("{http://www.w3.org/2001/XMLSchema-instance}type", "abstract") != "netzob:FileMessage" :
            raise NameError("The parsed xml doesn't represent a File message.")
        
        # Verifies the data field
        if rootElement.find("{" + namespace + "}data") == None or len(rootElement.find("{" + namespace + "}data").text) == 0:
            raise NameError("The parsed message has no data specified")
        
        # Parse the data field and transform it into a byte array
        msg_data = bytearray(rootElement.find("{" + namespace + "}data").text)
        
        # Retrieve the id
        msg_id = rootElement.get("id")
        
        # Retrieve the timestamp
        msg_timestamp = int(rootElement.get("timestamp"))
        
        # Retrieves the lineNumber (default -1)
        msg_lineNumber = int(rootElement.find("{" + namespace + "}lineNumber").text)
            
        # Retrieves the filename
        msg_filename = rootElement.find("{" + namespace + "}filename").text
        
        # Retrieves the creation date
        msg_creationDate = TypeConvertor.xsdDatetime2PythonDatetime(rootElement.find("{" + namespace + "}creationDate").text)
            
        # Retrieves the modification date
        msg_modificationDate = TypeConvertor.xsdDatetime2PythonDatetime(rootElement.find("{" + namespace + "}modificationDate").text)
        
        # Retrieves the owner
        msg_owner = rootElement.find("{" + namespace + "}owner").text
            
        # Retrieves the size
        msg_size = int(rootElement.find("{" + namespace + "}size").text)
      
        
        # TODO : verify this ! Circular imports in python !      
        # WARNING : verify this ! Circular imports in python !  
        from netzob.Common.Models.FileMessage import FileMessage
        
        result = FileMessage(msg_id, msg_timestamp, msg_data, msg_filename, msg_creationDate, msg_modificationDate, msg_owner, msg_size, msg_lineNumber)
        
        return result
 
