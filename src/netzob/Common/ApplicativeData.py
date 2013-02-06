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
from lxml.etree import ElementTree
from lxml import etree
import uuid
import csv


#+---------------------------------------------------------------------------+
#| Local Imports
#+---------------------------------------------------------------------------+
class ApplicativeDataException(Exception):
    pass


class ApplicativeData(object):
    """Class definition of an applicative data"""

    #+-----------------------------------------------------------------------+
    #| Constructor
    #+-----------------------------------------------------------------------+
    def __init__(self, id, name, type, value):
        self.id = id
        self.name = name
        self.type = type
        self.value = value

    def getID(self):
        return self.id

    def getName(self):
        return self.name

    def getType(self):
        return self.type

    def getValue(self):
        return self.value

    def setID(self, id):
        self.id = id

    def setName(self, name):
        self.name = name

    def setType(self, type):
        self.type = type

    def setValue(self, value):
        self.value = value

    def save(self, root, namespace_common):
        xmlData = etree.SubElement(root, "{" + namespace_common + "}data")
        xmlData.set("id", str(self.getID()))
        xmlData.set("name", str(self.getName()))
        xmlData.set("type", str(self.getType()))
        xmlData.text = self.value

    #+----------------------------------------------
    #| Static methods
    #+----------------------------------------------
    @staticmethod
    def loadFromXML(xmlRoot, namespace_common, version):
        if version == "0.1":
            idData = xmlRoot.get('id')
            nameData = xmlRoot.get('name')
            typeData = xmlRoot.get('type')
            valueData = xmlRoot.text
            if idData is not None and nameData is not None and typeData is not None and valueData is not None:
                return ApplicativeData(uuid.UUID(idData), nameData, typeData, valueData)
            else:
                return None
        return None

    @staticmethod
    def loadFromCSV(fileToImport):
        result = []
        with open(fileToImport, 'rb') as csvFile:
            # We use the sniffer to compute which dialect is used in current CSV
            dialect = csv.Sniffer().sniff(csvFile.read(1024))
            csvFile.seek(0)
            dataReader = csv.reader(csvFile, dialect)
            errorMessage = None
            idLine = 0
            for row in dataReader:
                idLine += 1
                if len(row) != 3:
                    errorMessage = _("line {0} in CSV has not 3 columns, format must be : Name, Type, Value".format(idLine))
                    break
                else:
                    try:
                        data = ApplicativeData(uuid.uuid4(), row[0], row[1], row[2])
                        result.append(data)
                    except ApplicativeDataException, e:
                        errorMessage = _("line {0} in CSV, invalid format of data : {1}".format(idLine, e))
                        break
        if errorMessage is not None:
            raise ApplicativeDataException(errorMessage)

        return result
