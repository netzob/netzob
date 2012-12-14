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
from gettext import gettext as _
import logging
import uuid
from lxml.etree import ElementTree
from lxml import etree

#+---------------------------------------------------------------------------+
#| Local Imports
#+---------------------------------------------------------------------------+
from netzob.Common.Field import Field
from netzob.Common.ProjectConfiguration import ProjectConfiguration
from netzob.Common.Type.TypeIdentifier import TypeIdentifier
from netzob.Common.Type.TypeConvertor import TypeConvertor
from netzob.Common.Type.UnitSize import UnitSize
from netzob.Common.Type.Format import Format
from netzob.Common.Type.Sign import Sign
from netzob.Common.Type.Endianess import Endianess
from netzob.Common.NetzobException import NetzobException
from netzob.Common.MMSTD.Symbols.AbstractSymbol import AbstractSymbol

NAMESPACE = "http://www.netzob.org/"


#+---------------------------------------------------------------------------+
#| Symbol:
#|     Class definition of a symbol
#+---------------------------------------------------------------------------+
class TrashSymbol(AbstractSymbol):

    #+-----------------------------------------------------------------------+
    #| Constructor
    #+-----------------------------------------------------------------------+
    def __init__(self, id=None):
        AbstractSymbol.__init__(self, "TrashSymbol")
        self.id = id
        if self.id == None:
            id = str(uuid.uuid4())
        self.name = "TrashSymbol"
        self.messages = []
        self.encodingFilters = []
        self.visualizationFilters = []

        # Interpretation attributes
        self.format = Format.HEX
        self.unitSize = UnitSize.NONE
        self.sign = Sign.UNSIGNED
        self.endianess = Endianess.BIG

        # Clean the symbol
        self.fields = [Field.createDefaultField()]

    def addVisualizationFilter(self, filter):
        self.visualizationFilters.append(filter)

    def cleanVisualizationFilters(self):
        self.visualizationFilters = []

    def getVisualizationFilters(self):
        return self.visualizationFilters

    def removeVisualizationFilter(self, filter):
        self.visualizationFilters.remove(filter)

    def addEncodingFilter(self, filter):
        self.encodingFilters.append(filter)

    def removeEncodingFilter(self, filter):
        if filter in self.encodingFilters:
            self.encodingFilters.remove(filter)

    def getEncodingFilters(self):
        filters = []
        for field in self.getFields():
            filters.extend(field.getEncodingFilters())
        filters.extend(self.encodingFilters)

    #+----------------------------------------------
    #| getMessageByID:
    #|  Return the message which ID is provided
    #+----------------------------------------------
    def getMessageByID(self, messageID):
        for message in self.messages:
            if str(message.getID()) == str(messageID):
                return message

        return None

    #+----------------------------------------------
    #| removeMessage : remove any ref to the given
    #| message and recompute regex and score
    #+----------------------------------------------
    def removeMessage(self, message):
        if message in self.messages:
            self.messages.remove(message)
        else:
            self.log.error("Cannot remove message {0} from symbol {1}, since it doesn't exist.".format(message.getID(), self.getName()))

    def addMessage(self, message):
        for msg in self.messages:
            if msg.getID() == message.getID():
                return
        message.setSymbol(self)
        self.messages.append(message)

    def save(self, root, namespace_project, namespace_common):
        xmlSymbol = etree.SubElement(root, "{" + namespace_project + "}trashSymbol")
        xmlSymbol.set("id", str(self.getID()))
        xmlSymbol.set("name", str(self.getName()))

        # Interpretation attributes
        if self.getFormat() is not None:
            xmlSymbolFormat = etree.SubElement(xmlSymbol, "{" + namespace_project + "}format")
            xmlSymbolFormat.text = str(self.getFormat())

        if self.getUnitSize() is not None:
            xmlSymbolUnitSize = etree.SubElement(xmlSymbol, "{" + namespace_project + "}unitsize")
            xmlSymbolUnitSize.text = str(self.getUnitSize())

        if self.getSign() is not None:
            xmlSymbolSign = etree.SubElement(xmlSymbol, "{" + namespace_project + "}sign")
            xmlSymbolSign.text = str(self.getSign())

        if self.getEndianess() is not None:
            xmlSymbolEndianess = etree.SubElement(xmlSymbol, "{" + namespace_project + "}endianess")
            xmlSymbolEndianess.text = str(self.getEndianess())

        # Save the message references
        xmlMessages = etree.SubElement(xmlSymbol, "{" + namespace_project + "}messages-ref")
        for message in self.messages:
            xmlMessage = etree.SubElement(xmlMessages, "{" + namespace_common + "}message-ref")
            xmlMessage.set("id", str(message.getID()))

    #+----------------------------------------------
    #| getXMLDefinition:
    #|   Returns the XML description of the symbol
    #|   @return a string containing the xml def.
    #+----------------------------------------------
    def getXMLDefinition(self):

        # Register the namespace
        etree.register_namespace('netzob', PROJECT_NAMESPACE)
        etree.register_namespace('netzob-common', COMMON_NAMESPACE)

        # create the file
        root = etree.Element("{" + NAMESPACE + "}netzob")
        root.set("project", str(self.getProject().getName()))

        self.save(root, PROJECT_NAMESPACE, COMMON_NAMESPACE)

        tree = ElementTree(root)
        result = etree.tostring(tree, pretty_print=True)
        return result

    #+----------------------------------------------
    #| getTextDefinition:
    #|   Returns the text description of the symbol
    #|   @return a string containing the text definition
    #+----------------------------------------------
    def getTextDefinition(self):
        result = ""
        for field in self.getFields():

            # Layer depth
            for i in range(field.getEncapsulationLevel()):
                result += "  "

            # Name
            result += field.getName()

            # Description
            if field.getDescription() is not None and field.getDescription() != "":
                result += " (" + field.getDescription() + ") "
            result += " : "
            result += "\t"

            # Value
            result += field.getEncodedVersionOfTheRegex()

            result += "\n"
        return result

    #+----------------------------------------------
    #| GETTERS
    #+----------------------------------------------
    def getID(self):
        return self.id

    def getMessages(self):
        """Computes and returns messages
        associated with the current symbol"""
        result = []
        for message in self.messages:
            if message.getSymbol() is self:
                result.append(message)
            else:
                self.removeMessage(message)
        return result

    def getName(self):
        return self.name

    def getFields(self):
        self.fields = [Field.createDefaultField()]
        return self.fields

    def getProject(self):
        return self.project

    def getFormat(self):
        return self.format

    def getUnitSize(self):
        return self.unitSize

    def getSign(self):
        return self.sign

    def getEndianess(self):
        return self.endianess

    #+----------------------------------------------
    #| SETTERS
    #+----------------------------------------------

    def setName(self, name):
        self.name = name

    def setMessages(self, mess):
        self.messages = mess

    def setFormat(self, aFormat):
        self.format = aFormat
        for field in self.getFields():
            field.setFormat(aFormat)

    def setUnitSize(self, unitSize):
        self.unitSize = unitSize
        for field in self.getFields():
            field.setUnitSize(unitSize)

    def setSign(self, sign):
        self.sign = sign
        for field in self.getFields():
            field.setSign(sign)

    def setEndianess(self, endianess):
        self.endianess = endianess
        for field in self.getFields():
            field.setEndianess(endianess)

    def __str__(self):
        return str(self.getName())

    def __repr__(self):
        return str(self.getName())

    def __cmp__(self, other):
        if other is None:
            return 1
        try:
            if self.getName() == other.getName():
                return 0
            else:
                return 1
        except:
            self.log.warn("Tried to compare a Symbol with {0}".format(str(other)))
            return 1

    #+----------------------------------------------
    #| Static methods
    #+----------------------------------------------
    @staticmethod
    def loadSymbol(xmlRoot, namespace_project, namespace_common, version, project, poolOfMessages):
        if version == "0.1":
            nameSymbol = xmlRoot.get("name")
            idSymbol = xmlRoot.get("id")
            symbol = TrashSymbol(idSymbol, project)

            # Interpretation attributes
            if xmlRoot.find("{" + namespace_project + "}format") is not None:
                symbol_format = xmlRoot.find("{" + namespace_project + "}format").text
                symbol.setFormat(symbol_format)

            if xmlRoot.find("{" + namespace_project + "}unitsize") is not None:
                symbol_unitsize = xmlRoot.find("{" + namespace_project + "}unitsize").text
                symbol.setUnitSize(symbol_unitsize)

            if xmlRoot.find("{" + namespace_project + "}sign") is not None:
                symbol_sign = xmlRoot.find("{" + namespace_project + "}sign").text
                symbol.setSign(symbol_sign)

            if xmlRoot.find("{" + namespace_project + "}endianess") is not None:
                symbol_endianess = xmlRoot.find("{" + namespace_project + "}endianess").text
                symbol.setEndianess(symbol_endianess)

            # we parse the messages
            if xmlRoot.find("{" + namespace_project + "}messages-ref") is not None:
                xmlMessages = xmlRoot.find("{" + namespace_project + "}messages-ref")
                for xmlMessage in xmlMessages.findall("{" + namespace_common + "}message-ref"):
                    id = xmlMessage.get("id")
                    message = poolOfMessages.getMessageByID(id)
                    if message is not None:
                        message.setSymbol(symbol)
                        symbol.addMessage(message)

            # we parse the fields
            if xmlRoot.find("{" + namespace_project + "}fields") is not None:
                xmlFields = xmlRoot.find("{" + namespace_project + "}fields")
                for xmlField in xmlFields.findall("{" + namespace_project + "}field"):
                    field = Field.loadFromXML(xmlField, namespace_project, version)
                    if field is not None:
                        symbol.addField(field)

            return symbol
        return None
