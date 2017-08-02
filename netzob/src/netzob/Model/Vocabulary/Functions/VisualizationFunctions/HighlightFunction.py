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

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+
from lxml import etree
from lxml.etree import ElementTree
#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Model.Vocabulary.Functions.VisualizationFunction import VisualizationFunction


class HighlightFunction(VisualizationFunction):
    """Represents a function which applies to modify the visualiation attributes of a data"""

    TYPE = "HighlightFunction"
    TAG_START = "\033[1;41m"
    TAG_END = "\033[1;m"

    def __init__(self, start, end):
        super(HighlightFunction, self).__init__(start, end)

    def getTags(self):
        return (self.TAG_START, self.TAG_END)

    def XMLProperties(currentFunction, xmlHighlightFunction, symbol_namespace, common_namespace):
        # Save the Properties
        VisualizationFunction.XMLProperties(currentFunction, xmlHighlightFunction, symbol_namespace, common_namespace)

    def saveToXML(self, xmlRoot, symbol_namespace, common_namespace):
        xmlHighlightFunction = etree.SubElement(xmlRoot, "{" + symbol_namespace + "}HighlightFunction")

        HighlightFunction.XMLProperties(self, xmlHighlightFunction, symbol_namespace, common_namespace)

    @staticmethod
    def restoreFromXML(xmlroot, symbol_namespace, common_namespace, attributes):

        VisualizationFunction.restoreFromXML(xmlroot, symbol_namespace, common_namespace, attributes)
        return attributes

    @staticmethod
    def loadFromXML(xmlroot, symbol_namespace, common_namespace):
        a = HighlightFunction.restoreFromXML(xmlroot, symbol_namespace, common_namespace, dict())

        HighLightFunc = None

        if 'start' in a.keys() and 'end' in a.keys():
            HighLightFunc = HighlightFunction(start=a['start'], end=a['end'])
            if 'id' in a.keys():
                HighLightFunc.id = a['id']
        return HighLightFunc
