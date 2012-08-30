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
#| Standard library imports                                                  |
#+---------------------------------------------------------------------------+
from gettext import gettext as _
from lxml import etree
import logging
import re
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
from netzob.Common.MMSTD.Dictionary.DataTypes.BinaryType import BinaryType
from netzob.Common.MMSTD.Dictionary.Variables.AbstractVariable import \
    AbstractVariable
from netzob.Common.MMSTD.Dictionary.Variables.AggregateVariable import \
    AggregateVariable
from netzob.Common.MMSTD.Dictionary.Variables.AlternateVariable import \
    AlternateVariable
from netzob.Common.MMSTD.Dictionary.Variables.DataVariable import DataVariable
from netzob.Common.Type.Endianess import Endianess
from netzob.Common.Type.Format import Format
from netzob.Common.Type.Sign import Sign
from netzob.Common.Type.TypeConvertor import TypeConvertor
from netzob.Common.Type.UnitSize import UnitSize


class Field(object):
    """Field:
            Class definition of a field.
    """

    def __init__(self, name, index, regex, symbol):
        """Constructor of Field:

                @type name: string
                @param name: the name of the field
                @type index: integer
                @param index: the index of the field in the symbol structure.
                @type regex: string
                @param regex: a regex that rules values of the field.
                @type symbol: netzob.Common.Symbol.Symbol
                @param symbol: the symbol the field belongs to.
        """
        self.name = name
        self.index = index
        self.regex = regex
        self.symbol = symbol

        # Default values
        self.encapsulation_level = 0
        self.description = ""
        self.color = "black"
        self.symbol.addField(self, index)

        # Interpretation attributes
        self.format = Format.HEX
        self.unitSize = UnitSize.NONE
        self.sign = Sign.UNSIGNED
        self.endianess = Endianess.BIG
        self.mathematicFilters = []

        self.variable = None
        self.variable = self.getDefaultVariable()

    def getEncodedVersionOfTheRegex(self):
        """getEncodedVersionOfTheRegex:
                Encode the regex in a dedicated format (IPv4, Binary...).

                @rtype: string
                @return: the encoded version or the regex itself if it did not manage to encode.
        """
        if self.regex == "" or self.regex is None or self.regex == "None":  # TODO: be careful with the fact that XML files may store None as a string...
            return ""
        elif self.regex.find("{") != -1:  # This is a real regex
            return self.regex
        else:  # This is a simple value
            return TypeConvertor.encodeNetzobRawToGivenType(self.regex, self.format)

    def isStatic(self):
        """isStatic:
                Tells if a regex is static (does not contain a '{n,p}').

                @rtype: boolean
                @return: True if the regex is static.
        """
        if self.regex.find("{") == -1 or self.getName() == "__sep__":
            return True
        else:
            return False

    def isRegexOnlyDynamic(self):
        """isRegexOnlyDynamic:
                Tells if a regex is only dynamic (does not contain a static subregex).

                @rtype: boolean
                @return: True if the regex is only dynamic.
        """
        if re.match("\(\.\{\d?,\d+\}\)", self.regex) is not None:
            return True
        else:
            return False

    def getDefaultVariable(self):
        """getDefaultVariable:
                Generates and returns a variable which is an aggregate that has one child which is an alternate of all default values of the field picked in the current symbol values.

                @rtype: netzob.Common.MMSTD.Dictionary.Variables.AggregateVariable.AggregateVariable
                @return: the generated variable
        """
        if self.isStatic():
            value = TypeConvertor.netzobRawToBitArray(self.getRegex())
            variable = DataVariable(uuid.uuid4(), self.getName(), False, False, BinaryType(True, len(value), len(value)), value.to01())  # A static field is neither mutable nor random.
            return variable
        else:
            # The default variable is an alternative of all the possibilities (in binary type)
            cells = self.symbol.getUniqValuesByField(self)
            tmpDomain = set()
            for cell in cells:
                tmpDomain.add(TypeConvertor.netzobRawToBitArray(cell))
            domain = sorted(tmpDomain)

            variable = AggregateVariable(uuid.uuid4(), "Aggregate", True, False, None)
            alternateVar = AlternateVariable(uuid.uuid4(), "Alternate", True, False, None)
            for d in domain:
                child = DataVariable(uuid.uuid4(), "defaultVariable", False, False, BinaryType(True, len(d), len(d)), d.to01())
                alternateVar.addChild(child)
            variable.addChild(alternateVar)
            return variable

    def getVisualizationFilters(self):
        """getVisualizationFilters:
                Get the visualization filters applied on this field.

                @rtype: netzob.Common.Filters List
                @return: a list of all needed filters.
        """
        filters = []

        # dynamic fields are in Blue
        if not self.isStatic():
            filters.append(TextColorFilter("Dynamic Field", "blue"))
#            # fields with no variable define are in yellow
            if self.variable is None:
                filters.append(BackgroundColorFilter("Default variable", "yellow"))

        return filters

    def getEncodingFilters(self):
        """getEncodingFilters:
                Calls computeFormatEncodingFilter.
        """
        filters = []
        # Following filters must be considered :
        filters.append(self.computeFormatEncodingFilter())
        return filters

    def removeMathematicFilter(self, filter):
        """removeMathematicFilter:
                Remove a precised mathematic filter.

                @type filter: netzob.Common.Filters
                @param filter: the filter that is removed.
        """
        fToRemove = None
        for mFilter in self.mathematicFilters:
            if mFilter.getName() == filter.getName():
                fToRemove = mFilter
                break
        if fToRemove is not None:
            self.mathematicFilters.remove(fToRemove)

    def addMathematicFilter(self, filter):
        """addMathematicFilter:
                Add a precised mathematic filter.

                @type filter: netzob.Common.Filters
                @param filter: the filter that is added.
        """
        self.mathematicFilters.append(filter)

    def computeFormatEncodingFilter(self):
        """computeFormatEncodingFilter:
                Get the format filter applied on this field. It tells how the data are displayed.

                @rtype: netzob.Common.Filters.FormatFilter
                @return: the computed format filter.
        """
        return FormatFilter("Field Format Encoding", self.format, self.unitSize, self.endianess, self.sign)

    def computeSignEncodingFilter(self):
        """computeSignEncodingFilter:
                Does nothing.

                @return: None
        """
        return None

    def computeEndianessEncodingFilter(self):
        """computeEndianessEncodingFilter:
                Does nothing.

                @return: None
        """
        return None

    def save(self, root, namespace):
        """save:
                Creates an xml tree from a given xml root, with all necessary elements for the reconstruction of this field.

                @type root: lxml.etree.Element
                @param root: the root of this xml tree.
                @type namespace: string
                @param namespace: a precision for the xml subtree.
        """
        xmlField = etree.SubElement(root, "{" + namespace + "}field")
        xmlField.set("name", str(self.getName()))
        xmlField.set("index", str(self.getIndex()))

        if self.getEncapsulationLevel() is not None:
            xmlFieldEncapsulationLevel = etree.SubElement(xmlField, "{" + namespace + "}encapsulation_level")
            xmlFieldEncapsulationLevel.text = str(self.getEncapsulationLevel())

        if self.getRegex() is not None:
            xmlFieldRegex = etree.SubElement(xmlField, "{" + namespace + "}regex")
            xmlFieldRegex.text = str(self.getRegex())

        if self.getFormat() is not None:
            xmlFieldFormat = etree.SubElement(xmlField, "{" + namespace + "}format")
            xmlFieldFormat.text = str(self.getFormat())

        if self.getUnitSize() is not None:
            xmlFieldUnitSize = etree.SubElement(xmlField, "{" + namespace + "}unitsize")
            xmlFieldUnitSize.text = str(self.getUnitSize())

        if self.getSign() is not None:
            xmlFieldSign = etree.SubElement(xmlField, "{" + namespace + "}sign")
            xmlFieldSign.text = str(self.getSign())

        if self.getEndianess() is not None:
            xmlFieldEndianess = etree.SubElement(xmlField, "{" + namespace + "}endianess")
            xmlFieldEndianess.text = str(self.getEndianess())

        if self.getDescription() is not None:
            xmlFieldDescription = etree.SubElement(xmlField, "{" + namespace + "}description")
            xmlFieldDescription.text = str(self.getDescription())

        if self.getColor() is not None:
            xmlFieldColor = etree.SubElement(xmlField, "{" + namespace + "}color")
            xmlFieldColor.text = str(self.getColor())

        if self.getVariable() is not None:
            self.getVariable().toXML(xmlField, namespace)

#+---------------------------------------------------------------------------+
#| Getters                                                                   |
#+---------------------------------------------------------------------------+
    def getName(self):
        return self.name

    def getEncapsulationLevel(self):
        return self.encapsulation_level

    def getRegex(self):
        return self.regex

    def getSymbol(self):
        return self.symbol

    def getDescription(self):
        return self.description

    def getColor(self):
        if not self.isStatic():
            return "blue"
        return self.color

    def getIndex(self):
        return self.index

    def getBackgroundColor(self):
        if self.getVariable() is None:
            return "yellow"
        return None

    def getFormat(self):
        return self.format

    def getUnitSize(self):
        return self.unitSize

    def getSign(self):
        return self.sign

    def getEndianess(self):
        return self.endianess

    def getMathematicFilters(self):
        return self.mathematicFilters

    def getVariable(self):
        return self.variable

#+---------------------------------------------------------------------------+
#| Setters                                                                   |
#+---------------------------------------------------------------------------+
    def setName(self, name):
        self.name = name

    def setEncapsulationLevel(self, level):
        self.encapsulation_level = level

    def setRegex(self, regex):
        self.regex = regex

    def setDescription(self, description):
        self.description = description

    def setColor(self, color):
        self.color = color

    def setIndex(self, index):
        self.index = index

    def setFormat(self, aFormat):
        self.format = aFormat

    def setUnitSize(self, unitSize):
        self.unitSize = unitSize

    def setSign(self, sign):
        self.sign = sign

    def setEndianess(self, endianess):
        self.endianess = endianess

    def setVariable(self, variable):
        self.variable = variable

#+---------------------------------------------------------------------------+
#| Static methods                                                            |
#+---------------------------------------------------------------------------+
    @staticmethod
    def createDefaultField(symbol):
        """createDefaultField:
                Creates and returns the default field.

                @rtype: netzob.Commons.Field.Field
                @return: the built field.
        """
        return Field("Default", 0, "(.{,})", symbol)

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
                @rtype: netzob.Commons.Field.Field
                @return: the built field.
        """
        if version == "0.1":
            # logging.debug(_("[ Field: loadFromXML: {0}").format(etree.tostring(xmlRoot)))  # a bit heavy
            logging.debug(_("[ Field: loadFromXML:").format())
            field_name = xmlRoot.get("name")
            field_index = int(xmlRoot.get("index"))
            field_regex = ""
            if xmlRoot.find("{" + namespace + "}regex") is not None:
                field_regex = xmlRoot.find("{" + namespace + "}regex").text

            field = Field(field_name, field_index, field_regex, symbol)

            if xmlRoot.find("{" + namespace + "}encapsulation_level") is not None:
                field_encapsulation_level = xmlRoot.find("{" + namespace + "}encapsulation_level").text
                field.setEncapsulationLevel(int(field_encapsulation_level))

            if xmlRoot.find("{" + namespace + "}format") is not None:
                field_format = xmlRoot.find("{" + namespace + "}format").text
                field.setFormat(field_format)

            if xmlRoot.find("{" + namespace + "}unitsize") is not None:
                field_unitsize = xmlRoot.find("{" + namespace + "}unitsize").text
                field.setUnitSize(field_unitsize)

            if xmlRoot.find("{" + namespace + "}sign") is not None:
                field_sign = xmlRoot.find("{" + namespace + "}sign").text
                field.setSign(field_sign)

            if xmlRoot.find("{" + namespace + "}endianess") is not None:
                field_endianess = xmlRoot.find("{" + namespace + "}endianess").text
                field.setEndianess(field_endianess)

            if xmlRoot.find("{" + namespace + "}description") is not None:
                field_description = xmlRoot.find("{" + namespace + "}description").text
                field.setDescription(field_description)

            if xmlRoot.find("{" + namespace + "}color") is not None:
                field_color = xmlRoot.find("{" + namespace + "}color").text
                field.setColor(field_color)

            if xmlRoot.find("{" + namespace + "}variable") is not None:
                var = AbstractVariable.loadFromXML(xmlRoot.find("{" + namespace + "}variable"), namespace, version, symbol)
                field.setVariable(var)

            logging.debug(_("Field: loadFromXML: {0} ]").format(field.getName()))
            return field

        return None
