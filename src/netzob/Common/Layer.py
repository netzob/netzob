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
#|       - Frédéric Guihéry <frederic.guihery (a) amossys.fr>                |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Standard library imports                                                  |
#+---------------------------------------------------------------------------+
from gettext import gettext as _
from lxml import etree
import logging
import uuid

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+


#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Filters.Encoding.FormatFilter import FormatFilter
from netzob.Common.Filters.Visualization.BackgroundColorFilter import \
    BackgroundColorFilter
from netzob.Common.Filters.Visualization.TextColorFilter import TextColorFilter
from netzob.Common.Type.Endianess import Endianess
from netzob.Common.Type.Format import Format
from netzob.Common.Type.Sign import Sign
from netzob.Common.Type.UnitSize import UnitSize
from netzob.Common.Type.TypeConvertor import TypeConvertor


class Layer(object):
    """Layer:
            Class definition of a layer of a protocol.
    """

    def __init__(self, ID, name):
        """Constructor of Field:

                @type name: string
                @param name: the name of the field
        """
        self.id = ID
        self.name = name

        # Default values
        self.description = ""
        self.color = "black"
        self.bgcolor = "white"

        # Interpretation attributes
        self.format = Format.HEX
        self.unitSize = UnitSize.NONE
        self.sign = Sign.UNSIGNED
        self.endianess = Endianess.BIG

        # Data
        self.fields = []

    def save(self, root, namespace):
        """save:
                Creates an xml tree from a given xml root, with all necessary elements for the reconstruction of this layer.

                @type root: lxml.etree.Element
                @param root: the root of this xml tree.
                @type namespace: string
                @param namespace: a precision for the xml subtree.
        """
        xmlLayer = etree.SubElement(root, "{" + namespace + "}layer")
        xmlLayer.set("id", str(self.getID()))
        xmlLayer.set("name", str(self.getName()))

        if self.getFormat() is not None:
            xmlLayerFormat = etree.SubElement(xmlLayer, "{" + namespace + "}format")
            xmlLayerFormat.text = str(self.getFormat())

        if self.getUnitSize() is not None:
            xmlLayerUnitSize = etree.SubElement(xmlLayer, "{" + namespace + "}unitsize")
            xmlLayerUnitSize.text = str(self.getUnitSize())

        if self.getSign() is not None:
            xmlLayerSign = etree.SubElement(xmlLayer, "{" + namespace + "}sign")
            xmlLayerSign.text = str(self.getSign())

        if self.getEndianess() is not None:
            xmlLayerEndianess = etree.SubElement(xmlLayer, "{" + namespace + "}endianess")
            xmlLayerEndianess.text = str(self.getEndianess())

        if self.getDescription() is not None:
            xmlLayerDescription = etree.SubElement(xmlLayer, "{" + namespace + "}description")
            xmlLayerDescription.text = str(self.getDescription())

        if self.getColor() is not None:
            xmlLayerColor = etree.SubElement(xmlLayer, "{" + namespace + "}color")
            xmlLayerColor.text = str(self.getColor())

        if self.getBGColor() is not None:
            xmlLayerBGColor = etree.SubElement(xmlLayer, "{" + namespace + "}bgcolor")
            xmlLayerBGColor.text = str(self.getBGColor())

        # Save the field references
        xmlFields = etree.SubElement(xmlLayer, "{" + namespace + "}fields-ref")
        for field in self.fields:
            xmlField = etree.SubElement(xmlFields, "{" + namespace + "}field-ref")
            xmlField.set("index", str(field.getIndex()))

    def addField(self, field):
        self.fields.append(field)

#+---------------------------------------------------------------------------+
#| Getters                                                                   |
#+---------------------------------------------------------------------------+
    def getID(self):
        return self.id

    def getName(self):
        return self.name

    def getDescription(self):
        return self.description

    def getColor(self):
        return self.color

    def getBGColor(self):
        return self.bgcolor

    def getFormat(self):
        return self.format

    def getUnitSize(self):
        return self.unitSize

    def getSign(self):
        return self.sign

    def getEndianess(self):
        return self.endianess

    def getFields(self):
        return self.fields

#+---------------------------------------------------------------------------+
#| Setters                                                                   |
#+---------------------------------------------------------------------------+
    def setID(self, ID):
        self.id = ID

    def setName(self, name):
        self.name = name

    def setDescription(self, description):
        self.description = description

    def setColor(self, color):
        self.color = color

    def setBGColor(self, color):
        self.bgcolor = color

    def setFormat(self, aFormat):
        self.format = aFormat

    def setUnitSize(self, unitSize):
        self.unitSize = unitSize

    def setSign(self, sign):
        self.sign = sign

    def setEndianess(self, endianess):
        self.endianess = endianess

    def setFields(self, fields):
        self.fields = fields

#+---------------------------------------------------------------------------+
#| Static methods                                                            |
#+---------------------------------------------------------------------------+
    @staticmethod
    def loadFromXML(xmlRoot, namespace, version, symbol):
        """loadFromXML:
                Loads a field from an xml file. This file ought to be written with the previous toXML function.
                This function is called by the symbol loadFromXML function.

                @type xmlRoot: lxml.etree.Element
                @param xmlRoot: the xml root of the file we will read.
                @type namespace: string
                @param namespace: a precision for the xml tree.
                @type version: string
                @param version: if not 0.1, the function will done nothing.
                @type symbol: netzob.Commons.Symbol.Symbol
                @param symbol: the symbol which loadFromXML function called this function.
                @rtype: netzob.Commons.Layer
                @return: the built layer.
        """
        if version == "0.1":
            layer_id = xmlRoot.get("id")
            layer_name = xmlRoot.get("name")
            layer = Layer(layer_id, layer_name)

            if xmlRoot.find("{" + namespace + "}format") is not None:
                layer_format = xmlRoot.find("{" + namespace + "}format").text
                layer.setFormat(layer_format)

            if xmlRoot.find("{" + namespace + "}unitsize") is not None:
                layer_unitsize = xmlRoot.find("{" + namespace + "}unitsize").text
                layer.setUnitSize(layer_unitsize)

            if xmlRoot.find("{" + namespace + "}sign") is not None:
                layer_sign = xmlRoot.find("{" + namespace + "}sign").text
                layer.setSign(layer_sign)

            if xmlRoot.find("{" + namespace + "}endianess") is not None:
                layer_endianess = xmlRoot.find("{" + namespace + "}endianess").text
                layer.setEndianess(layer_endianess)

            if xmlRoot.find("{" + namespace + "}description") is not None:
                layer_description = xmlRoot.find("{" + namespace + "}description").text
                layer.setDescription(layer_description)

            if xmlRoot.find("{" + namespace + "}color") is not None:
                layer_color = xmlRoot.find("{" + namespace + "}color").text
                layer.setColor(layer_color)

            if xmlRoot.find("{" + namespace + "}bgcolor") is not None:
                layer_bgcolor = xmlRoot.find("{" + namespace + "}bgcolor").text
                layer.setBGColor(layer_bgcolor)

            # we parse the field references
            if xmlRoot.find("{" + namespace + "}fields-ref") is not None:
                xmlFields = xmlRoot.find("{" + namespace + "}fields-ref")
                for xmlField in xmlFields.findall("{" + namespace + "}field-ref"):
                    index = xmlField.get("index")
                    field = symbol.getFieldByIndex(index)
                    if field is not None:
                        layer.addField(field)

            return layer

        return None
