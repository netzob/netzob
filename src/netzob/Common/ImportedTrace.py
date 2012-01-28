# -*- coding: utf-8 -*-


#+---------------------------------------------------------------------------+
#|          01001110 01100101 01110100 01111010 01101111 01100010            |
#|                                                                           |
#|               Netzob : Inferring communication protocols                  |
#+---------------------------------------------------------------------------+
#| Copyright (C) 2011 Georges Bossert and Frédéric Guihéry                   |
#| This program is free software: you can redistribute it and/or modify      |
#| it under the terms of the GNU General Public License as published by      |
#| the Free Software Foundation, either version 3 of the License, or         |
#| (at your option) any later version.                                       |
#|                                                                           |
#| This program is distributed in the hope that it will be useful,           |
#| but WITHOUT ANY WARRANTY; without even the implied warranty of            |
#| MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the              |
#| GNU General Public License for more details.                              |
#|                                                                           |
#| You should have received a copy of the GNU General Public License         |
#| along with this program. If not, see <http://www.gnu.org/licenses/>.      |
#+---------------------------------------------------------------------------+
#| @url      : http://www.netzob.org                                         |
#| @contact  : contact@netzob.org                                            |
#| @sponsors : Amossys, http://www.amossys.fr                                |
#|             Supélec, http://www.rennes.supelec.fr/ren/rd/cidre/           |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+ 
#| Standard library imports
#+---------------------------------------------------------------------------+
import logging
import time
from lxml.etree import ElementTree
from lxml import etree
from netzob.Common.Type.TypeConvertor import TypeConvertor
from netzob.Common.Models.Factories.AbstractMessageFactory import AbstractMessageFactory

#+---------------------------------------------------------------------------+
#| Local Imports
#+---------------------------------------------------------------------------+



#+---------------------------------------------------------------------------+
#| ImportedTrace :
#|     Class definition of an imported trace registered in a workspace
#+---------------------------------------------------------------------------+
class ImportedTrace(object):
    
    #+-----------------------------------------------------------------------+
    #| Constructor
    #+-----------------------------------------------------------------------+
    def __init__(self, importID, date, dataType, description, projectName):
        self.importID = importID
        self.date = date
        self.dataType = dataType
        self.description = description
        self.projectName = projectName
        self.messages = []
    
    def save(self, root, namespace_workspace, namespace_common):
        xmlSymbol = etree.SubElement(root, "{" + namespace_workspace + "}import")
        xmlSymbol.set("date", str(TypeConvertor.pythonDatetime2XSDDatetime(self.getDate())))
        xmlSymbol.set("type", str(self.getDataType()))
        xmlSymbol.set("description", str(self.getDescription()))
        xmlSymbol.set("projectName", str(self.getProjectName()))
        xmlSymbol.set("importID", str(self.getImportID()))
        logging.warn("saving the following imported trace")
        # Save the messages
        xmlMessages = etree.SubElement(xmlSymbol, "{" + namespace_workspace + "}messages")
        for message in self.getMessages() :
            AbstractMessageFactory.save(message, xmlMessages, namespace_workspace, namespace_common)
            
    
    
    def addMessage(self, message):
        self.messages.append(message)
        
    def getImportID(self):
        return self.importID
    def getDate(self):
        return self.date
    def getDataType(self):
        return self.dataType
    def getDescription(self):
        return self.description
    def getProjectName(self):
        return self.projectName
    def getMessages(self):
        return self.messages
    
    def setImportID(self, importID):
        self.importID = importID
    def setDate(self, date):
        self.date = date
    def setDataType(self, dataType):
        self.dataType = dataType
    def setDescription(self, description):
        self.description = description
    def setProjectName(self, projectName):
        self.projectName = projectName
        
    
    
    #+---------------------------------------------- 
    #| Static methods
    #+----------------------------------------------       
    @staticmethod
    def loadSymbol(xmlRoot, namespace, namespace_common, version):
        
        if version == "0.1" :
            print str(xmlRoot.get("date"))
            date = TypeConvertor.xsdDatetime2PythonDatetime(str(xmlRoot.get("date")))
            dataType = xmlRoot.get("type")
            description = xmlRoot.get("description", "")
            importID = xmlRoot.get("importID")
            projectName = xmlRoot.get("projectName")
            
            importedTrace = ImportedTrace(importID, date, dataType, description, projectName)
            
            # we parse the messages
            if xmlRoot.find("{" + namespace + "}messages") != None :
                xmlMessages = xmlRoot.find("{" + namespace + "}messages")
                for xmlMessage in xmlMessages.findall("{" + namespace_common + "}message") :
                    message = AbstractMessageFactory.loadFromXML(xmlMessage, namespace_common, version)
                    if message != None :
                        importedTrace.addMessage(message)
                    
            return importedTrace
        return None
        
