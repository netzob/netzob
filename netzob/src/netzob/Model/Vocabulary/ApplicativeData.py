# -*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|          01001110 01100101 01110100 01111010 01101111 01100010            |
#|                                                                           |
#|               Netzob : Inferring communication protocols                  |
#+---------------------------------------------------------------------------+
#| Copyright (C) 2011-2017 Georges Bossert and Frédéric Guihéry              |
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
import uuid

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+
from lxml import etree
from lxml.etree import ElementTree
#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger


@NetzobLogger
class ApplicativeData(object):
    """An applicative data represents an information used over the application
    that generated the captured flows. It can be the player name or the user email address
    if these informations are used somehow by the protocol.

    An applicative data can be created out of any information.
    >>> from netzob.all import *
    >>> app = ApplicativeData("Username", ASCII("toto"))
    >>> print(app.name)
    Username

    >>> app1 = ApplicativeData("Email", ASCII("contact@netzob.org"))
    >>> print(app1.value)
    ASCII=contact@netzob.org ((0, 144))

    """

    def __init__(self, name, value, _id=None):
        self.name = name
        self.value = value
        if _id is None:
            _id = uuid.uuid4()
        self.id = _id

    @property
    def name(self):
        """The name of the applicative data.

        :type: :mod:`str`
        """
        return self.__name

    @name.setter
    @typeCheck(str)
    def name(self, name):
        if name is None:
            raise TypeError("Name cannot be None")
        self.__name = name

    @property
    def id(self):
        """The unique id of the applicative data.

        :type: :class:`uuid.UUID`
        """
        return self.__id

    @id.setter
    @typeCheck(uuid.UUID)
    def id(self, _id):
        if _id is None:
            raise TypeError("Id cannot be None")
        self.__id = _id

    @property
    def value(self):
        """The value of the applicative data.

        :type: object
        """
        return self.__value

    @value.setter
    def value(self, value):
        if value is None:
            raise TypeError("Value cannot be None")
        self.__value = value

    def __str__(self):
        """Redefine the string representation of the current
        applicative Data.

        :return: the string representation of the applicative data
        :rtype: str
        """
        return "Applicative Data: {0}={1})".format(self.name, self.value)

    def XMLProperties(currentAppData, xmlSession, symbol_namespace, common_namespace):
        # Save the properties

        if currentAppData.id is not None:
            xmlSession.set("id", str(currentAppData.id.hex))
        if currentAppData.name is not None:
            xmlSession.set("name", str(currentAppData.name))

        # Save the value
        if currentAppData.value is not None:
            xmlValue= etree.SubElement(xmlSession, "{" + symbol_namespace + "}value")
            currentAppData.value.saveToXML(xmlValue, symbol_namespace, common_namespace)

    def saveToXML(self, xmlRoot, symbol_namespace, common_namespace):
        xmlSession = etree.SubElement(xmlRoot, "{" + symbol_namespace + "}applicativeData")
        ApplicativeData.XMLProperties(self, xmlSession, symbol_namespace, common_namespace)

    @staticmethod
    def restoreFromXML(xmlroot, symbol_namespace, common_namespace, attributes):

        if xmlroot.get('id') is not None:
            attributes['id'] = uuid.UUID(hex=str(xmlroot.get('id')))
        if xmlroot.get('name') is not None:
            attributes['name'] = str(xmlroot.get('name'))
        else:
            attributes['name'] = None

        value = None
        if xmlroot.find("{" + symbol_namespace + "}value") is not None:
            xmlVale = xmlroot.find("{" + symbol_namespace + "}value")
            if xmlVale.find("{" + symbol_namespace + "}raw") is not None:
                xmlRaw = xmlVale.find("{" + symbol_namespace + "}raw")
                from netzob.Model.Vocabulary.Types.Raw import Raw
                raw = Raw.loadFromXML(xmlRaw, symbol_namespace, common_namespace)
                if raw is not None:
                    value = raw
            elif xmlVale.find("{" + symbol_namespace + "}ascii") is not None:
                xmlASCII = xmlVale.find("{" + symbol_namespace + "}ascii")
                from netzob.Model.Vocabulary.Types.ASCII import ASCII
                ascii = ASCII.loadFromXML(xmlASCII, symbol_namespace, common_namespace)
                if ascii is not None:
                    value = ascii
            elif xmlVale.find("{" + symbol_namespace + "}bitarray") is not None:
                xmlBitarray = xmlVale.find("{" + symbol_namespace + "}bitarray")
                from netzob.Model.Vocabulary.Types.BitArray import BitArray
                bitarray = BitArray.loadFromXML(xmlBitarray, symbol_namespace, common_namespace)
                if bitarray is not None:
                    value = bitarray
            elif xmlVale.find("{" + symbol_namespace + "}hexaString") is not None:
                xmlHexaString = xmlVale.find("{" + symbol_namespace + "}hexaString")
                from netzob.Model.Vocabulary.Types.HexaString import HexaString
                hexastring = HexaString.loadFromXML(xmlHexaString, symbol_namespace, common_namespace)
                if hexastring is not None:
                    value = hexastring
            elif xmlVale.find("{" + symbol_namespace + "}integer") is not None:
                xmlInteger = xmlVale.find("{" + symbol_namespace + "}integer")
                from netzob.Model.Vocabulary.Types.Integer import Integer
                integer = Integer.loadFromXML(xmlInteger, symbol_namespace, common_namespace)
                if integer is not None:
                    value = integer
            elif xmlVale.find("{" + symbol_namespace + "}ipv4") is not None:
                xmlIPv4 = xmlVale.find("{" + symbol_namespace + "}ipv4")
                from netzob.Model.Vocabulary.Types.IPv4 import IPv4
                ipv4 = IPv4.loadFromXML(xmlIPv4, symbol_namespace, common_namespace)
                if ipv4 is not None:
                    value = ipv4
            elif xmlVale.find("{" + symbol_namespace + "}Timestamp") is not None:
                xmlTimestamp = xmlVale.find("{" + symbol_namespace + "}Timestamp")
                from netzob.Model.Vocabulary.Types.Timestamp import Timestamp
                timestamp = Timestamp.loadFromXML(xmlTimestamp, symbol_namespace, common_namespace)
                if timestamp is not None:
                    value = timestamp
            elif xmlVale.find("{" + symbol_namespace + "}abstractType") is not None:
                xmlAbstractType = xmlVale.find("{" + symbol_namespace + "}abstractType")
                from netzob.Model.Vocabulary.Types.AbstractType import AbstractType
                abstractType = AbstractType.loadFromXML(xmlAbstractType, symbol_namespace, common_namespace)
                if abstractType is not None:
                    value = abstractType
        attributes['value'] = value

        return attributes

    @staticmethod
    def loadFromXML(xmlroot, symbol_namespace, common_namespace):

        a = ApplicativeData.restoreFromXML(xmlroot, symbol_namespace, common_namespace, dict())

        appData = None

        if 'id' in a.keys():
            appData = ApplicativeData(_id=a['id'], value=a['value'], name=a['name'])
        return appData