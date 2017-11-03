#-*- coding: utf-8 -*-

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
#| File contributors :                                                       |
#|       - Georges Bossert <georges.bossert (a) supelec.fr>                  |
#|       - Frédéric Guihéry <frederic.guihery (a) amossys.fr>                |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Standard library imports                                                  |
#+---------------------------------------------------------------------------+
import abc
import uuid

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+
from lxml import etree
from lxml.etree import ElementTree
#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+


class VisualizationFunction(object):
    """Represents a function which applies to modify the visualiation attributes of a data"""

    TYPE = "VisualizationFunction"

    def __init__(self, start, end):
        self.start = start
        self.end = end
        self.id = uuid.uuid4()

    @abc.abstractmethod
    def getTags(self):
        self.log.error("The function class (" + self.getType() +
                       ") doesn't define 'getTags' !")
        raise NotImplementedError("The function class (" + self.getType() +
                                  ") doesn't define 'getTags' !")

    def XMLProperties(currentFunction, xmlVisuFunction, symbol_namespace, common_namespace):
        # Save the Properties
        if currentFunction.TYPE is not None:
            xmlVisuFunction.set("TYPE", str(currentFunction.TYPE))
        if currentFunction.start is not None:
            xmlVisuFunction.set("start", str(currentFunction.start))
        if currentFunction.end is not None:
            xmlVisuFunction.set("end", str(currentFunction.end))
        if currentFunction.id is not None:
            xmlVisuFunction.set("id", str(currentFunction.id.hex))

    def saveToXML(self, xmlRoot, symbol_namespace, common_namespace):
        xmlVisuFunction = etree.SubElement(xmlRoot, "{" + symbol_namespace + "}VisualizationFunction")

        VisualizationFunction.XMLProperties(self, xmlVisuFunction, symbol_namespace, common_namespace)

    @staticmethod
    def restoreFromXML(xmlroot, symbol_namespace, common_namespace, attributes):

        if xmlroot.get('TYPE') is not None:
            attributes['TYPE'] = str(xmlroot.get('TYPE'))
        if xmlroot.get('start') is not None:
            attributes['start'] = int(xmlroot.get('start'))
        if xmlroot.get('end') is not None:
            attributes['end'] = int(xmlroot.get('end'))
        if xmlroot.get('id') is not None:
            attributes['id'] = uuid.UUID(hex=str(xmlroot.get('id')))
        return attributes

    @staticmethod
    def loadFromXML(xmlroot, symbol_namespace, common_namespace):

        a = VisualizationFunction.restoreFromXML(xmlroot, symbol_namespace, common_namespace, dict())

        VisuFunc = None

        if 'start' in a.keys() and 'end' in a.keys():
            VisuFunc = VisualizationFunction(start=a['start'], end=a['end'])
            if 'id' in a.keys():
                VisuFunc.id = a['id']
            # This is not possible and necessary
            # if 'TYPE' in a.keys():
            #     VisuFunc.TYPE = a['TYPE']
        return VisuFunc
