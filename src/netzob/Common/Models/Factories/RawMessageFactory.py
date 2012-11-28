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
from lxml.etree import ElementTree
import uuid

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+
from netzob.Common.Type.TypeConvertor import TypeConvertor
from lxml import etree


#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| RawMessageFactory:
#|     Factory dedicated to the manipulation of raw messages
#| ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~+
#| XML Definition:
#| <message type="RAW" id="" timestamp="">
#|     <data></data>
#| </message>
#+---------------------------------------------------------------------------+
class RawMessageFactory(object):

    XML_SCHEMA_TYPE = "netzob-common:RawMessage"

    @staticmethod
    #+-----------------------------------------------------------------------+
    #| save
    #|     Generate the XML representation of a Network message
    #+-----------------------------------------------------------------------+
    def save(message, xmlMessage, namespace_project, namespace):
        xmlMessage.set("{http://www.w3.org/2001/XMLSchema-instance}type", RawMessageFactory.XML_SCHEMA_TYPE)

    @staticmethod
    #+---------------------------------------------------------------------------+
    #| loadFromXML:
    #|     Function which parses an XML and extract from it
    #[    the definition of a RAW message
    #| @param rootElement: XML root of the RAW message
    #| @return an instance of a n IPC Message
    #| @throw NameError if XML invalid
    #+---------------------------------------------------------------------------+
    def loadFromXML(rootElement, namespace, version, id, timestamp, data):
        # Then we verify its an IPC Message
        if rootElement.get("{http://www.w3.org/2001/XMLSchema-instance}type", "abstract") != RawMessageFactory.XML_SCHEMA_TYPE:
            raise NameError("The parsed xml doesn't represent a Raw message.")

        from netzob.Common.Models.RawMessage import RawMessage
        result = RawMessage(id, timestamp, data)

        return result
