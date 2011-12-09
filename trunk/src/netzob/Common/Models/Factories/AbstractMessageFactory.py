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


#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.Models.Factories.FileMessageFactory import FileMessageFactory
from netzob.Common.Models.Factories.NetworkMessageFactory import NetworkMessageFactory
from netzob.Common.Models.Factories.IPCMessageFactory import IPCMessageFactory
from netzob.Common.Models.Factories.RawMessageFactory import RawMessageFactory


#+---------------------------------------------------------------------------+
#| AbstractMessageFactory :
#|     Factory dedicated to the manipulation of file messages
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.2
#+---------------------------------------------------------------------------+
class AbstractMessageFactory():
    
    @staticmethod
    #+-----------------------------------------------------------------------+
    #| save
    #|     Generate an XML representation of a message
    #+-----------------------------------------------------------------------+
    def save(message, root, namespace):
        if message.getType() == "File" :
            return FileMessageFactory.save(message, root, namespace)
        elif message.getType() == "Network" :
            return NetworkMessageFactory.save(message, root, namespace)
        elif message.getType() == "IPC" :
            return IPCMessageFactory.save(message, root, namespace)
        elif message.getType() == "RAW" :
            return RawMessageFactory.save(message, root, namespace)
        else :
            raise NameError('''There is no factory which would support 
            the generation of an xml representation of the message : ''' + str(message))
    
    
    @staticmethod
    #+---------------------------------------------------------------------------+
    #| loadFromXML :
    #|     Function which parses an XML and extract from it
    #[     the definition of a file message
    #| @param rootElement: XML root of the file message 
    #| @return an instance of a message
    #| @throw NameError if XML invalid
    #+---------------------------------------------------------------------------+
    def loadFromXML(rootElement, namespace, version):        
        
        
        # Computes which type is it
        if rootElement.get("{http://www.w3.org/2001/XMLSchema-instance}type", "abstract") == "abstract" :
            raise NameError("The parsed xml doesn't represent a valid type message.")
        
        if rootElement.get("{http://www.w3.org/2001/XMLSchema-instance}type", "abstract") == "netzob:FileMessage" :
            return FileMessageFactory.loadFromXML(rootElement, namespace, version)
        if rootElement.get("{http://www.w3.org/2001/XMLSchema-instance}type", "abstract") == "netzob:NetworkMessage" :
            return NetworkMessageFactory.loadFromXML(rootElement, namespace, version)
        if rootElement.get("{http://www.w3.org/2001/XMLSchema-instance}type", "abstract") == "netzob:IPCMessage" :
            return IPCMessageFactory.loadFromXML(rootElement, namespace, version)
        if rootElement.get("{http://www.w3.org/2001/XMLSchema-instance}type", "abstract") == "netzob:RawMessage" :
            return RawMessageFactory.loadFromXML(rootElement, namespace, version)
        else :
            raise NameError("The parsed xml doesn't represent a valid type message.")
            return None
        
