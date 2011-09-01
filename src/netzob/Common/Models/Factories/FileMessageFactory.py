#!/usr/bin/python
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
import array
import binascii
import logging.config
import uuid

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+
from xml.etree import ElementTree

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from ... import ConfigurationParser

#+---------------------------------------------------------------------------+
#| Configuration of the logger
#+---------------------------------------------------------------------------+
loggingFilePath = ConfigurationParser.ConfigurationParser().get("logging", "path")
logging.config.fileConfig(loggingFilePath)

#+---------------------------------------------------------------------------+
#| FileMessageFactory :
#|     Factory dedicated to the manipulation of file messages
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.2
#| ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~+
#| XML Definition :
#| <message type="file" id="">
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
    def saveInXML(message):
        root = ElementTree.Element("message")
        root.set("type", "file")
        root.set("id", message.getID())
        # line number
        subLineNumber = ElementTree.SubElement(root, "lineNumber")
        subLineNumber.text = str(message.getLineNumber())
        # filename
        subFilename = ElementTree.SubElement(root, "filename")
        subFilename.text = str(message.getFilename())
        # creationDate
        subCreationDate = ElementTree.SubElement(root, "creationDate")
        subCreationDate.text = message.getCreationDate()
        # modificationDate
        subModificationDate = ElementTree.SubElement(root, "modificationDate")
        subModificationDate.text = message.getModificationDate()
        # owner
        subOwner = ElementTree.SubElement(root, "owner")
        subOwner.text = message.getOwner()
        # size
        subSize = ElementTree.SubElement(root, "size")
        subSize.text = str(message.getSize())
        # data
        subData = ElementTree.SubElement(root, "data")
        subData.text = str(message.getData())
        return ElementTree.tostring(root)
    
    @staticmethod
    #+---------------------------------------------------------------------------+
    #| loadFromXML :
    #|     Function which parses an XML and extract from it
    #[     the definition of a file message
    #| @param rootElement: XML root of the file message 
    #| @return an instance of a FipSource (default 0.0.0.0)ileMessage
    #| @throw NameError if XML invalid
    #+---------------------------------------------------------------------------+
    def loadFromXML(rootElement):        
        # First we verify rootElement is a message
        if rootElement.tag != "message" :
            raise NameError("The parsed xml doesn't represent a message.")
        # Then we verify its a File Message
        if rootElement.get("type", "abstract") != "file" :
            raise NameError("The parsed xml doesn't represent a file message.")
        # Verifies the data field
        if rootElement.find("data") == None or len(rootElement.find("data").text) == 0:
            raise NameError("The parsed message has no data specified")
        
        # Parse the data field and transform it into a byte array
        msg_data = bytearray(rootElement.find("data").text)
        
        # Retrieve the id (default = -1)
        msg_id = rootElement.get('id', "-1")
        
        if msg_id == "-1" :
            msg_id = str(uuid.uuid4()) 
        
        # Retrieves the lineNumber (default -1)
        if rootElement.find("lineNumber") != None :
            msg_lineNumber = int(rootElement.find("lineNumber").text)
        else :
            msg_lineNumber = -1
            
        # Retrieves the filename (default no.filename)
        if rootElement.find("filename") != None :
            msg_filename = rootElement.find("filename").text
        else :
            msg_filename = "no.filename"
        
        # Retrieves the creation date (default 2011-08-31 11:45)
        if rootElement.find("creationDate") != None :
            msg_creationDate = rootElement.find("creationDate").text
        else :
            msg_creationDate = "2011-08-31 11:45"
            
        # Retrieves the modification date (default 2011-08-31 11:45)
        if rootElement.find("modificationDate") != None :
            msg_modificationDate = rootElement.find("modificationDate").text
        else :
            msg_modificationDate = "2011-08-31 11:45"
        
        # Retrieves the owner (default Unknown)
        if rootElement.find("owner") != None :
            msg_owner = rootElement.find("owner").text
        else :
            msg_owner = "Unknown"
            
        # Retrieves the size (default -1)
        if rootElement.find("size") != None :
            msg_size = rootElement.find("size").text
        else :
            msg_size = 0
      
        
        # TODO : verify this ! Circular imports in python !      
        # WARNING : verify this ! Circular imports in python !  
        from .. import FileMessage
        
        result = FileMessage.FileMessage()
        result.setID(msg_id)
        result.setData(msg_data)
        result.setLineNumber(msg_lineNumber)
        result.setFilename(msg_filename)
        result.setCreationDate(msg_creationDate)
        result.setModificationDate(msg_modificationDate)
        result.setOwner(msg_owner)
        result.setSize(msg_size)
        
        
        return result
    
    
