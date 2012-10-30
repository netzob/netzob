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
#| File contributors :                                                       |
#|       - Georges Bossert <georges.bossert (a) supelec.fr>                  |
#|       - Frédéric Guihéry <frederic.guihery (a) amossys.fr>                |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Standard library imports                                                  |
#+---------------------------------------------------------------------------+
from gettext import gettext as _
from lxml import etree
from lxml.etree import ElementTree
from operator import attrgetter
import logging
import re
import struct
import uuid

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Field import Field
from netzob.Common.MMSTD.Dictionary.Variables.AggregateVariable import \
    AggregateVariable
from netzob.Common.MMSTD.Symbols.AbstractSymbol import AbstractSymbol
from netzob.Common.NetzobException import NetzobException
from netzob.Common.Property import Property
from netzob.Common.Type.Format import Format
from netzob.Common.Type.TypeConvertor import TypeConvertor


#+---------------------------------------------------------------------------+
#| Namespaces                                                                |
#+---------------------------------------------------------------------------+
NAMESPACE = "http://www.netzob.org/"

# TODO: Note: this is probably useless, as it is already specified in Project.py
PROJECT_NAMESPACE = "http://www.netzob.org/project"
COMMON_NAMESPACE = "http://www.netzob.org/common"


#+---------------------------------------------------------------------------+
#| Symbol:
#|     Class definition of a symbol
#+---------------------------------------------------------------------------+
class Symbol(AbstractSymbol):

    TYPE = "Symbol"

    #+-----------------------------------------------------------------------+
    #| Constructor
    #+-----------------------------------------------------------------------+
    def __init__(self, ID, name, project):
        AbstractSymbol.__init__(self, Symbol.TYPE)
        self.id = ID
        self.project = project
        self.messages = []
        self.field = Field.createDefaultField(self)
        self.field.setName(name)
        self.project = project
        self.pattern = None

    #+----------------------------------------------
    #| getVariables:
    #|  Extract from the fields definitions the included variables
    #+----------------------------------------------
    def getVariables(self):
        result = []
        for field in self.getExtendedFields():
            if field.getVariable() is not None:
                # We add all variable that has the root variable of field as ancestor.
                result.extend(field.getVariable().getProgeny())
            else:
                self.log.debug(_("Field {0} has no variable, considering default one.").format(str(field.getName())))
                result.extend(field.getDefaultVariable(self).getProgeny())

        return result

    ### Messages ###
    def getMessageByID(self, messageID):
        """getMessageByID: Return the message which ID is provided.
        """
        for message in self.messages:
            if str(message.getID()) == str(messageID):
                return message
        return None

    def removeMessage(self, message):
        """removeMessage: remove any ref to the given message and
        recompute regex and score.
        """
        if message in self.messages:
            self.messages.remove(message)
        else:
            self.log.error("Cannot remove message {0} from symbol {1}, since it doesn't exist.".format(message.getID(), self.getName()))

    def addMessages(self, messages):
        """Add the provided messages in the symbol"""
        for message in messages:
            self.addMessage(message)

    def addMessage(self, message):
        for msg in self.messages:
            if msg.getID() == message.getID():
                return
        message.setSymbol(self)
        self.messages.append(message)

    def save(self, root, namespace_project, namespace_common):
        xmlSymbol = etree.SubElement(root, "{" + namespace_project + "}symbol")
        xmlSymbol.set("id", str(self.getID()))

        # Save the message references
        xmlMessages = etree.SubElement(xmlSymbol, "{" + namespace_project + "}messages-ref")
        for message in self.messages:
            xmlMessage = etree.SubElement(xmlMessages, "{" + namespace_common + "}message-ref")
            xmlMessage.set("id", str(message.getID()))
        # Save the field
        if self.getField() is not None:
            self.getField().save(xmlSymbol, namespace_project)

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
        for field in self.getExtendedFields():
            # We exclude separator fields
            if self.getAlignmentType() == "delimiter":
                if field.isStatic():
                    continue

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
    #| getScapyDissector:
    #|   @return a string containing the scapy dissector of the symbol
    #+----------------------------------------------
    def getScapyDissector(self):
        self.refineRegexes()  # In order to force the calculation of each field limits
        s = ""
        s += "class " + self.getName() + "(Packet):\n"
        s += "    name = \"" + self.getName() + "\"\n"
        s += "    fields_desc = [\n"

        for field in self.getExtendedFields():
            if self.field.isStatic():
                s += "                    StrFixedLenField(\"" + field.getName() + "\", " + field.getEncodedVersionOfTheRegex() + ")\n"
            else:  # Variable field of fixed size
                s += "                    StrFixedLenField(\"" + field.getName() + "\", None)\n"
            ## If this is a variable field  # TODO
                # StrLenField("the_varfield", "the_default_value", length_from = lambda pkt: pkt.the_lenfield)
        s += "                 ]\n"

        ## Bind current layer with the underlying one  # TODO
        # bind_layers(TCP, HTTP, sport=80)
        # bind_layers(TCP, HTTP, dport=80)
        return s

    def write(self, writingToken):
        """write:
                Grants a writing access to the symbol and its variables. Retrieve and return the value issued from this access.

                @type writingToken: netzob.Common.MMSTD.Dictionary.VariableProcessingToken.VariableWritingToken.VariableWritingToken
                @param writingToken: a token which contains all critical information on this writing access.
                @rtype: bitarray
                @return: the value this acces writes.
        """
        self.getRoot().write(writingToken)
        result = writingToken.getValue()

        return result

    def getRoot(self):
        # We create an aggregate of all the fields
        rootSymbol = AggregateVariable(self.getID(), self.getName(), False, False, None)
        for field in self.getExtendedFields():
            if field.getVariable() is None:
                variable = field.getDefaultVariable(self)
            else:
                variable = field.getVariable()
            rootSymbol.addChild(variable)
        return rootSymbol

    def getProperties(self):
        properties = []
        prop = Property('name', Format.STRING, self.getName())
        prop.setIsEditable(True)
        properties.append(prop)

        properties.append(Property('messages', Format.DECIMAL, len(self.getMessages())))
        properties.append(Property('fields', Format.DECIMAL, len(self.getExtendedFields())))
        minMsgSize = None
        maxMsgSize = 0
        avgMsgSize = 0
        if len(self.getMessages()) > 0:
            for m in self.getMessages():
                s = len(m.getData()) * 2
                if minMsgSize is None or s < minMsgSize:
                    minMsgSize = s
                if maxMsgSize is None or s > maxMsgSize:
                    maxMsgSize = s
                avgMsgSize += s
            avgMsgSize = avgMsgSize / len(self.getMessages())
        properties.append(Property('avg msg size (bytes)', Format.DECIMAL, avgMsgSize))
        properties.append(Property('min msg size (bytes)', Format.DECIMAL, minMsgSize))
        properties.append(Property('max msg size (bytes)', Format.DECIMAL, maxMsgSize))

        return properties

#+---------------------------------------------------------------------------+
#| Getters                                                                   |
#+---------------------------------------------------------------------------+

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

    def getMinEqu(self):
        return self.minEqu

    def getPattern(self):
        return self.pattern

    def getPatternString(self):
        return str(self.pattern[0]) + ";" + str([str(i) for i in self.pattern[1]])

    def getField(self):
        return self.field

    def getFieldByID(self, idField):
        """getFieldByID:
        Retrieves all the fields and searches for
        a field which ID is provided.
        Returns None, if cannot be found"""
        fields = self.getAllFields()
        for field in fields:
            if str(field.getID()) == str(idField):
                return field
        return None

    def getAllFields(self):
        """getAllFields: return all the fields (both layers and
        leafs) starting from the current object
        """
        res = []
        res.append(self.getField())
        res.extend(self.getField().getAllFields())
        return res

    def getExtendedFields(self):
        return self.getField().getExtendedFields()

    def getFieldByIndex(self, i):
        return self.getField().getFieldByIndex(i)

    def getName(self):
        return self.getField().getName()

    def getProject(self):
        return self.project

#+---------------------------------------------------------------------------+
#| Setters                                                                   |
#+---------------------------------------------------------------------------+
    def setField(self, field):
        self.field = field

    def setName(self, name):
        self.getField().setName(name)

    def setMessages(self, mess):
        self.messages = mess

    def setMinEqu(self, minEqu):
        self.minEqu = minEqu

    def setPattern(self, pattern):
        self.pattern = pattern

    def __str__(self):
        return str(self.getName())

    def __repr__(self):
        return str(self.getName())

    def __cmp__(self, other):
        if other is None:
            return 1
        try:
            if self.getID() == other.getID():
                return 0
            else:
                return 1
        except:
            self.log.warn(_("Tried to compare a Symbol with {0}").format(str(other)))
            return 1

#+---------------------------------------------------------------------------+
#| Static methods                                                            |
#+---------------------------------------------------------------------------+
    @staticmethod
    def loadSymbol(xmlRoot, namespace_project, namespace_common, version, project, poolOfMessages):
        if version == "0.1":
            idSymbol = uuid.UUID(xmlRoot.get("id"))
            symbol = Symbol(idSymbol, "", project)

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
            if xmlRoot.find("{" + namespace_project + "}field") is not None:
                xmlField = xmlRoot.find("{" + namespace_project + "}field")
                field = Field.loadFromXML(xmlField, namespace_project, version, symbol)
                if field != None:
                    symbol.setField(field)

            return symbol
        return None
