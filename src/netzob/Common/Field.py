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
import re
from lxml import etree
import uuid

#+---------------------------------------------------------------------------+
#| Local imports
#+---------------------------------------------------------------------------+
from netzob.Common.MMSTD.Dictionary.Variables.BinaryVariable import BinaryVariable
from netzob.Common.MMSTD.Dictionary.Variables.WordVariable import WordVariable
from netzob.Common.MMSTD.Dictionary.Variable import Variable
from netzob.Common.Type.Format import Format
from netzob.Common.Type.UnitSize import UnitSize
from netzob.Common.Type.Sign import Sign
from netzob.Common.Type.Endianess import Endianess
from netzob.Common.Type.TypeConvertor import TypeConvertor
from netzob.Common.MMSTD.Dictionary.Variables.AggregateVariable import AggregateVariable
from netzob.Common.MMSTD.Dictionary.Variables.AlternateVariable import AlternateVariable
from netzob.Common.MMSTD.Dictionary.Memory import Memory
from netzob.Common.Filters.Encoding.FormatFilter import FormatFilter
from netzob.Common.Filters.Visualization.TextColorFilter import TextColorFilter
from netzob.Common.Filters.Visualization.BackgroundColorFilter import BackgroundColorFilter
from netzob.Common.Filters.Mathematic.Base64Filter import Base64Filter
from netzob.Common.Filters.Mathematic.GZipFilter import GZipFilter


#+---------------------------------------------------------------------------+
#| Field:
#|     Class definition of a field
#+---------------------------------------------------------------------------+
class Field(object):

    #+-----------------------------------------------------------------------+
    #| Constructor
    #+-----------------------------------------------------------------------+
    def __init__(self, name, index, regex):
        self.name = name
        self.index = index
        self.regex = regex

        # Default values
        self.encapsulation_level = 0
        self.description = ""
        self.color = "black"
        self.variable = None

        # Interpretation attributes
        self.format = Format.HEX
        self.unitSize = UnitSize.NONE
        self.sign = Sign.UNSIGNED
        self.endianess = Endianess.BIG

        self.mathematicFilters = []

    def getEncodedVersionOfTheRegex(self):
        if self.regex == "" or self.regex == None or self.regex == "None":  # TODO: becareful with the fact that XML files may store None as a string...
            return ""
        elif self.regex.find("{") != -1:  # This is a real regex
            return self.regex
        else:  # This is a simple value
            return TypeConvertor.encodeNetzobRawToGivenType(self.regex, self.format)

    def isStatic(self):
        if self.regex.find("{") == -1 or self.getName() == "__sep__":
            return True
        else:
            return False

    def isRegexOnlyDynamic(self):
        if re.match("\(\.\{\d?,\d+\}\)", self.regex) != None:
            return True
        else:
            return False

    def getVariable(self):
        if self.isStatic():
            value = TypeConvertor.netzobRawToBitArray(self.getRegex())
            variable = BinaryVariable(uuid.uuid4(), self.getName(), value, len(value), len(value))
            return variable
        return self.variable

    def getDefaultVariable(self, symbol):
        # The default variable is an alternative of all the possibilities (in binary type)
        cells = symbol.getUniqValuesByField(self)
        tmpDomain = set()
        for cell in cells:
            tmpDomain.add(TypeConvertor.netzobRawToBitArray(cell))
        domain = sorted(tmpDomain)

        variable = AggregateVariable(uuid.uuid4(), "Aggregate", None)
        alternateVar = AlternateVariable(uuid.uuid4(), "Alternate", None)
        for d in domain:
            binaryVariable = BinaryVariable(uuid.uuid4(), "defaultVariable", d, len(d), len(d))
            alternateVar.addChild(binaryVariable)
        variable.addChild(alternateVar)

        return variable

    def setVariable(self, variable):
        self.variable = variable

    def getVisualizationFilters(self):
        filters = []

        # dynamic fields are in Blue
        if not self.isStatic():
            filters.append(TextColorFilter("Dynamic Field", "blue"))
#            # fields with no variable define are in yellow
            if self.variable == None:
                filters.append(BackgroundColorFilter("Default variable", "yellow"))

        return filters

    def getEncodingFilters(self):
        filters = []
        # Following filters must be considered :
        filters.append(self.computeFormatEncodingFilter())

        return filters

    def removeMathematicFilter(self, filter):
        fToRemove = None
        for mFilter in self.mathematicFilters:
            if mFilter.getName() == filter.getName():
                fToRemove = mFilter
                break
        if fToRemove != None:
            self.mathematicFilters.remove(fToRemove)

    def addMathematicFilter(self, filter):
        self.mathematicFilters.append(filter)

    def computeFormatEncodingFilter(self):
        return FormatFilter("Field Format Encoding", self.format, self.unitSize, self.endianess, self.sign)

    def computeSignEncodingFilter(self):
        return None

    def computeEndianessEncodingFilter(self):
        return None

    def save(self, root, namespace):
        xmlField = etree.SubElement(root, "{" + namespace + "}field")
        xmlField.set("name", str(self.getName()))
        xmlField.set("index", str(self.getIndex()))

        if self.getEncapsulationLevel() != None:
            xmlFieldEncapsulationLevel = etree.SubElement(xmlField, "{" + namespace + "}encapsulation_level")
            xmlFieldEncapsulationLevel.text = str(self.getEncapsulationLevel())

        if self.getRegex() != None:
            xmlFieldRegex = etree.SubElement(xmlField, "{" + namespace + "}regex")
            xmlFieldRegex.text = str(self.getRegex())

        if self.getFormat() != None:
            xmlFieldFormat = etree.SubElement(xmlField, "{" + namespace + "}format")
            xmlFieldFormat.text = str(self.getFormat())

        if self.getUnitSize() != None:
            xmlFieldUnitSize = etree.SubElement(xmlField, "{" + namespace + "}unitsize")
            xmlFieldUnitSize.text = str(self.getUnitSize())

        if self.getSign() != None:
            xmlFieldSign = etree.SubElement(xmlField, "{" + namespace + "}sign")
            xmlFieldSign.text = str(self.getSign())

        if self.getEndianess() != None:
            xmlFieldEndianess = etree.SubElement(xmlField, "{" + namespace + "}endianess")
            xmlFieldEndianess.text = str(self.getEndianess())

        if self.getDescription() != None:
            xmlFieldDescription = etree.SubElement(xmlField, "{" + namespace + "}description")
            xmlFieldDescription.text = str(self.getDescription())

        if self.getColor() != None:
            xmlFieldColor = etree.SubElement(xmlField, "{" + namespace + "}color")
            xmlFieldColor.text = str(self.getColor())

        if self.getVariable() != None:
            self.getVariable().toXML(xmlField, namespace)

    #+----------------------------------------------
    #| GETTERS
    #+----------------------------------------------
    def getName(self):
        return self.name

    def getEncapsulationLevel(self):
        return self.encapsulation_level

    def getRegex(self):
        return self.regex

    def getDescription(self):
        return self.description

    def getColor(self):
        if not self.isStatic():
            return "blue"
        return self.color

    def getIndex(self):
        return self.index

    def getBackgroundColor(self):
        if self.getVariable() == None:
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

    #+----------------------------------------------
    #| SETTERS
    #+----------------------------------------------
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

    #+----------------------------------------------
    #| Static methods
    #+----------------------------------------------
    @staticmethod
    def createDefaultField():
        return Field("Default", 0, "(.{,})")

    @staticmethod
    def loadFromXML(xmlRoot, namespace, version):
        if version == "0.1":
            field_name = xmlRoot.get("name")
            field_index = int(xmlRoot.get("index"))
            field_regex = ""
            if xmlRoot.find("{" + namespace + "}regex") != None:
                field_regex = xmlRoot.find("{" + namespace + "}regex").text

            field = Field(field_name, field_index, field_regex)

            if xmlRoot.find("{" + namespace + "}encapsulation_level") != None:
                field_encapsulation_level = xmlRoot.find("{" + namespace + "}encapsulation_level").text
                field.setEncapsulationLevel(int(field_encapsulation_level))

            if xmlRoot.find("{" + namespace + "}format") != None:
                field_format = xmlRoot.find("{" + namespace + "}format").text
                field.setFormat(field_format)

            if xmlRoot.find("{" + namespace + "}unitsize") != None:
                field_unitsize = xmlRoot.find("{" + namespace + "}unitsize").text
                field.setUnitSize(field_unitsize)

            if xmlRoot.find("{" + namespace + "}sign") != None:
                field_sign = xmlRoot.find("{" + namespace + "}sign").text
                field.setSign(field_sign)

            if xmlRoot.find("{" + namespace + "}endianess") != None:
                field_endianess = xmlRoot.find("{" + namespace + "}endianess").text
                field.setEndianess(field_endianess)

            if xmlRoot.find("{" + namespace + "}description") != None:
                field_description = xmlRoot.find("{" + namespace + "}description").text
                field.setDescription(field_description)

            if xmlRoot.find("{" + namespace + "}color") != None:
                field_color = xmlRoot.find("{" + namespace + "}color").text
                field.setColor(field_color)

            if xmlRoot.find("{" + namespace + "}variable") != None:
                var = Variable.loadFromXML(xmlRoot.find("{" + namespace + "}variable"), namespace, version)
                field.setVariable(var)

            return field

        return None
