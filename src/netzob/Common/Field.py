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
from netzob.Common.Property import Property
from netzob.Common.ProjectConfiguration import ProjectConfiguration


class Field(object):
    """Field:
            Class definition of a field.
    """

    def __init__(self, name, regex, symbol):
        """Constructor of Field:

                @type name: string
                @param name: the name of the field
                @type regex: string
                @param regex: a regex that rules values of the field
                @type symbol: string
                @param symbol: the parent symbol
        """
        self.id = uuid.uuid4()
        self.name = name
        self.symbol = symbol
        self.description = ""
        self.color = "black"

        # Partitionment
        self.score = 0.0
        self.alignment = ""
        self.regex = regex

        # Filters
        self.encodingFilters = []
        self.visualizationFilters = []
        self.mathematicFilters = []

        # Interpretation attributes
        self.format = self.symbol.project.getConfiguration().getVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_GLOBAL_FORMAT)
        self.unitSize = self.symbol.project.getConfiguration().getVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_GLOBAL_UNITSIZE)
        self.sign = self.symbol.project.getConfiguration().getVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_GLOBAL_SIGN)
        self.endianess = self.symbol.project.getConfiguration().getVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_GLOBAL_ENDIANESS)

        # Data
        self.variable = None
        self.defaultVariable = None
        self.fields = []

    def __str__(self):
        return str(self.getName())

    def __repr__(self):
        return str(self.getName())

    ## Filters
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
        for field in self.getExtendedFields():
            filters.extend(field.getEncodingFilters())
        filters.extend(self.encodingFilters)

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
            # fields with no variable define are in yellow
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

    ## Regex
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
        if (self.regex.find("{") == -1 and self.regex.find("*") == -1) or self.getName() == "__sep__":
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

    def isRegexValidForMessage(self, message):
        """Offers to verify if the provided message
        can be splitted in fields following their definition
        in the current symbol"""
        regex = []
        for field in self.getExtendedFields():
            regex.append(field.getRegex())
        # Now we apply the regex over the message
        try:
            compiledRegex = re.compile("".join(regex))
            data = message.getReducedStringData()
            dynamicDatas = compiledRegex.match(data)
        except AssertionError:
            return False

        if dynamicDatas is None:
            return False
        return True

    #+----------------------------------------------
    #| forcePartitioning:
    #|  Specify a delimiter for partitioning
    #+----------------------------------------------
    def forcePartitioning(self, aFormat, rawDelimiter):
        self.resetPartitioning()

        minNbSplit = 999999
        maxNbSplit = -1
        for cell in self.getCells():
            tmpStr = cell.split(rawDelimiter)
            minNbSplit = min(minNbSplit,
                             len(tmpStr))
            maxNbSplit = max(maxNbSplit,
                             len(tmpStr))
        self.removeLocalFields()
        if minNbSplit <= 1:  # If the delimiter does not create splitted fields
            field = Field(_("Name"), "(.{,})", self.getSymbol())
            field.setFormat(aFormat)
            field.setColor("blue")
            self.addField(field)
            return

        # Else, we add (maxNbSplit + maxNbSplit - 1) fields
        iField = -1
        for i in range(maxNbSplit):
            iField += 1
            field = Field(_("Name"), "((?:(?!" + rawDelimiter + ").)*)", self.getSymbol())
            field.setFormat(aFormat)
            field.setColor("blue")
            self.addField(field)
            iField += 1
            field = Field("__sep__", "(" + rawDelimiter + ")?", self.getSymbol())
            field.setFormat(aFormat)
            field.setColor("black")
            self.addField(field)
        self.popField()

    #+----------------------------------------------
    #| simplePartitioning:
    #|  Do message partitioning according to column variation
    #+----------------------------------------------
    def simplePartitioning(self, unitSize, status_cb=None, idStop_cb=None):
        logging.debug("Compute the simple partitioning on current symbol")
        self.alignmentType = "regex"
        self.rawDelimiter = ""
        # Restore fields to the default situation
        self.resetPartitioning()
        # Retrieve the biggest message
        maxLen = 0
        for cell in self.getCells():
            curLen = len(cell)
            if curLen > maxLen:
                maxLen = curLen
        logging.debug("Size of the longest message : {0}".format(maxLen))

        # Try to see if the column is static or variable
        resultString = ""
        resultMask = ""

        # Stop and clean if requested
        if idStop_cb is not None:
            if idStop_cb():
                self.removeLocalFields()
                return

        step = float(100) / float(maxLen)
        totalPercent = 0
        # Loop until maxLen
        for it in range(maxLen):
            ref = ""
            isDifferent = False

            # Stop and clean if requested
            if it % 10 == 0 and idStop_cb is not None:
                if idStop_cb():
                    self.removeLocalFields()
                    return

            # Loop through each cells of the column
            for cell in self.getCells():
                try:
                    tmp = cell[it]
                    if ref == "":
                        ref = tmp
                    if ref != tmp:
                        isDifferent = True
                        break
                except IndexError:
                    isDifferent = True

            if isDifferent:
                resultString += "-"
                resultMask += "1"
            else:
                resultString += ref
                resultMask += "0"

            totalPercent += step
            if it % 20 == 0 and status_cb is not None:
                status_cb(totalPercent, None)

        # Apply unitSize
        if unitSize != UnitSize.NONE:
            unitSize = UnitSize.getSizeInBits(unitSize)
            nbLetters = unitSize / 4
            tmpResultString = ""
            tmpResultMask = ""
            for i in range(0, len(resultString), nbLetters):

                # Stop and clean if requested
                if idStop_cb is not None:
                    if idStop_cb():
                        self.removeLocalFields()
                        return

                tmpText = resultString[i:i + nbLetters]
                if tmpText.count("-") >= 1:
                    for j in range(len(tmpText)):
                        tmpResultString += "-"
                        tmpResultMask += "1"
                else:
                    tmpResultString += tmpText
                    for j in range(len(tmpText)):
                        tmpResultMask += "0"
            resultString = tmpResultString
            resultMask = tmpResultMask
 
        ## Build of the fields
        self.removeLocalFields()
        currentStaticField = ""
        if resultMask[0] == "1":  # The first column is dynamic
            isLastDyn = True
        else:
            currentStaticField += resultString[0]
            isLastDyn = False

        nbElements = 1
        iField = -1
        for it in range(1, len(resultMask)):
            if resultMask[it] == "1":  # The current column is dynamic
                if isLastDyn:
                    nbElements += 1
                else:
                    # We change the field
                    iField += 1
                    field = Field(_("Name"), "(" + currentStaticField + ")", self.getSymbol())
                    field.setColor("black")
                    self.addField(field)
                    # We start a new field
                    currentStaticField = ""
                    nbElements = 1
                isLastDyn = True
            else:  # The current column is static
                if isLastDyn:  # We change the field
                    iField += 1
                    field = Field(_("Name"), "(.{," + str(nbElements) + "})", self.getSymbol())
                    field.setColor("blue")
                    self.addField(field)
                    # We start a new field
                    currentStaticField = resultString[it]
                    nbElements = 1
                else:
                    currentStaticField += resultString[it]
                    nbElements += 1
                isLastDyn = False

        # Stop and clean if requested
        if idStop_cb is not None:
            if idStop_cb():
                self.removeLocalFields()
                return

        # We add the last field
        iField += 1
        if resultMask[-1] == "1":  # If the last column is dynamic
            field = Field(_("Name"), "(.{," + str(nbElements) + "})", self.getSymbol())
            field.setColor("blue")
        else:
            field = Field(_("Name"), currentStaticField, self.getSymbol())
            field.setColor("black")
        self.addField(field)

    #+----------------------------------------------
    #| slickRegex:
    #|  try to make smooth the regex, by deleting tiny static
    #|  sequences that are between big dynamic sequences
    #+----------------------------------------------
    def slickRegex(self, project):
        # Use the default protocol type for representation
        aFormat = project.getConfiguration().getVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_GLOBAL_FORMAT)

        res = False
        i = 1
        nbFields = len(self.getExtendedFields())
        while i < nbFields - 1:
            aField = self.getFieldByIndex(i)
            if aField.isStatic():
                if len(aField.getRegex()) <= 2:  # Means a potential negligeable element that can be merged with its neighbours
                    precField = self.getFieldByIndex(i - 1)
                    if precField.isRegexOnlyDynamic():
                        nextField = self.getFieldByIndex(i + 1)
                        if nextField.isRegexOnlyDynamic():
                            res = True
                            minSize = len(aField.getRegex())
                            maxSize = len(aField.getRegex())

                            # Build the new field
                            regex = re.compile(".*{(\d*),(\d*)}.*")

                            # Get the minSize/maxSize of precField
                            m = regex.match(precField.getRegex())
                            if m.group(1) != "":
                                minSize += int(m.group(1))
                            if m.group(2) != "":
                                maxSize += int(m.group(2))

                            # Get the minSize/maxSize of nextField
                            m = regex.match(nextField.getRegex())
                            if m.group(1) != "":
                                minSize += int(m.group(1))
                            if m.group(2) != "":
                                maxSize += int(m.group(2))

                            minSize = str(minSize)
                            maxSize = str(maxSize)

                            aField.setIndex(precField.getIndex())
                            aField.setRegex("(.{" + minSize + "," + maxSize + "})")
                            aField.setFormat(aFormat)

                            # Delete the old ones
                            self.fields.remove(nextField)
                            self.fields.remove(precField)

                            # Update the index of the fields placed after the new one
                            for field in self.fields:
                                if field.getIndex() > aField.getIndex():
                                    field.setIndex(field.getIndex() - 2)
                            # Sort fields by their index
                            self.fields = sorted(self.fields, key=attrgetter('index'), reverse=False)
                            break  # Just do it one time to avoid conflicts in self.fields structure
            i += 1

        if res:
            self.slickRegex(project)  # Try to loop until no more merges are done
            logging.debug("The regex has been slicked")

    #+----------------------------------------------
    #| resetPartitioning:
    #|   Reset the current partitioning
    #+----------------------------------------------
    def resetPartitioning(self):
        # Reset values
        self.removeLocalFields()
        field = self.createDefaultField(self.getSymbol())
        self.addField(field)

    #+----------------------------------------------
    #| computeFieldsLimits:
    #|
    #+----------------------------------------------
    def computeFieldsLimits(self):
        for field in self.getExtendedFields():
            tmpRegex = field.getRegex()
            if field.isStatic():
                continue
            elif field.isRegexOnlyDynamic():
                cells = field.getCells()
                if len(cells) != len(self.getMessages()):
                    # There exists empty cells
                    continue
                min = 999999
                max = 0
                for cell in cells:
                    if len(cell) > max:
                        max = len(cell)
                    if len(cell) < min:
                        min = len(cell)
                if min == max:
                    field.setRegex("(.{" + str(min) + "})")
                else:
                    field.setRegex("(.{" + str(min) + "," + str(max) + "})")
            else:
                # TODO: handle complex regex
                continue

    #+----------------------------------------------
    #| concatWithNextField:
    #|  Concatenate the current field with the next one at the same level
    #+----------------------------------------------
    def concatWithNextField(self):
        # Retrieve the 2 fields to concatenate
        parentField = self.getParentField()
        localFields = parentField.getLocalFields()
        indexField1 = localFields.index(self)
        indexField2 = indexField1 + 1
        field1 = self
        try:
            field2 = localFields[indexField2]
        except IndexError:
            return -1

        # Remove children of each fields
        field1.removeLocalFields()
        field2.removeLocalFields()

        # Concatenate fields
        field1.setRegex("(" + field1.getRegex()[1:-1] + field1.getRegex()[1:-1] + ")")
        localFields.remove(field2)
        return 1

    #+----------------------------------------------
    #| splitField:
    #|  Split a field in two fields
    #|  return False if the split does not occure, else True
    #+----------------------------------------------
    def splitField(self, field, split_position, split_align):
        if split_position == 0:
            return False

        # Find the static/dynamic cols
        cells = field.getCells()
        ref1 = cells[0][:split_position]
        ref2 = cells[0][split_position:]
        isStatic1 = True
        isStatic2 = True
        lenDyn1 = len(cells[0][:split_position])
        lenDyn2 = len(cells[0][split_position:])
        for m in cells[1:]:
            if m[:split_position] != ref1:
                isStatic1 = False
                if len(m[:split_position]) > lenDyn1:
                    lenDyn1 = len(m[:split_position])
            if m[split_position:] != ref2:
                isStatic2 = False
                if len(m[split_position:]) > lenDyn2:
                    lenDyn2 = len(m[split_position:])

        # Build the new sub-regex
        if isStatic1:
            regex1 = ref1
        else:
            if split_align == "left":
                # The size is fixed
                regex1 = "(.{" + str(lenDyn1) + "})"
            else:
                regex1 = "(.{," + str(lenDyn1) + "})"
        if isStatic2:
            regex2 = ref2
        else:
            if split_align == "right":
                # The size is fixed
                regex2 = "(.{" + str(lenDyn2) + "})"
            else:
                regex2 = "(.{," + str(lenDyn2) + "})"

        if regex1 == "":
            return False
        if regex2 == "":
            return False

        new_format = field.getFormat()
        new_encapsulationLevel = field.getEncapsulationLevel()

        # We Build the two new fields
        field1 = Field(field.getName() + "-1", regex1, self.getSymbol())
        field1.setEncapsulationLevel(new_encapsulationLevel)
        field1.setFormat(new_format)
        field1.setColor(field.getColor())
        if field.getDescription() is not None and len(field.getDescription()) > 0:
            field1.setDescription(field.getDescription() + "-1")
        field2 = Field(field.getName() + "-2", regex2, self.getSymbol())

        field2.setEncapsulationLevel(new_encapsulationLevel)
        field2.setFormat(new_format)
        field2.setColor(field.getColor())
        if field.getDescription() is not None and len(field.getDescription()) > 0:
            field2.setDescription(field.getDescription() + "-2")

        # Remove the truncated one
        self.fields.remove(field)

        # Modify index to adapt
        for field in self.getExtendedFields():
            if field.getIndex() > field1.getIndex():
                field.setIndex(field.getIndex() + 1)

        self.fields.append(field1)
        self.fields.append(field2)
        # sort fields by their index
        self.fields = sorted(self.fields, key=attrgetter('index'), reverse=False)
        return True

    #+-----------------------------------------------------------------------+
    #| getPossibleTypesForAField:
    #|     Retrieve all the possible types for a field
    #+-----------------------------------------------------------------------+
    def getPossibleTypesForAField(self, field):
        # first we verify the field exists in the symbol
        if not field in self.fields:
            logging.warn("The computing field is not part of the current symbol")
            return []

        # Retrieve all the part of the messages which are in the given field
        cells = self.getUniqValuesByField()
        typeIdentifier = TypeIdentifier()
        return typeIdentifier.getTypes(cells)

    #+-----------------------------------------------------------------------+
    #| getStyledPossibleTypesForAField:
    #|     Retrieve all the possibles types for a field and we colorize
    #|     the selected one we an HTML RED SPAN
    #+-----------------------------------------------------------------------+
    def getStyledPossibleTypesForAField(self, field):
        tmpTypes = self.getPossibleTypesForAField(field)
        for i in range(len(tmpTypes)):
            if tmpTypes[i] == field.getFormat():
                tmpTypes[i] = "<span foreground=\"red\">" + field.getFormat() + "</span>"
        return ", ".join(tmpTypes)

    ## Variable
    def getDefaultVariable(self, symbol):
        """getDefaultVariable:
                Generates and returns a variable which is an aggregate that has one child which is an alternate of all default values of the field picked in the current symbol values.

                @type symbol: netzob.Common.Symbol
                @param symbol: the parent symbol.
                @rtype: netzob.Common.MMSTD.Dictionary.Variables.AggregateVariable.AggregateVariable
                @return: the generated variable
        """
        if self.isStatic():
            value = TypeConvertor.netzobRawToBitArray(self.getRegexData())
            variable = DataVariable(uuid.uuid4(), self.getName(), False, False, BinaryType(True, len(value), len(value)), value.to01())  # A static field is neither mutable nor random.
            return variable
        else:
            if self.defaultVariable is None:
                self.defaultVariable = self.generateDefaultVariable(symbol)
            return self.defaultVariable

    def generateDefaultVariable(self, symbol):
        """generateDefaultVariable:
                generates the default variable and returns it

                @type symbol: netzob.Common.Symbol
                @param symbol: the parent symbol.
                @rtype: netzob.Common.MMSTD.Dictionary.Variables.AggregateVariable.AggregateVariable
                @return: the generated variable
        """
        # The default variable is an alternative of all the possibilities (in binary type)
        cells = self.getUniqValuesByField()
        tmpDomain = set()
        for cell in cells:
            tmpDomain.add(TypeConvertor.netzobRawToBitArray(cell))
        domain = sorted(tmpDomain)

        variable = AggregateVariable(uuid.uuid4(), "Aggregate", False, False, None)
        alternateVar = AlternateVariable(uuid.uuid4(), "Alternate", False, False, None)
        for d in domain:
            child = DataVariable(uuid.uuid4(), "defaultVariable", False, False, BinaryType(True, len(d), len(d)), d.to01())
            alternateVar.addChild(child)
        variable.addChild(alternateVar)
        return variable

    ## Fields
    def getAllFields(self):
        """getAllFields: return all the fields (both layers and
        leafs) starting from the current object
        """
        res = []
        res.extend(self.getLocalFields())
        for field in self.getLocalFields():
            res.extend(field.getAllFields())
        return res

    def getParentField(self):
        """getParentField: return the parent field
        """
        for field in self.getSymbol().getAllFields():
            if self in field.getLocalFields():
                return field

    def addField(self, field, index=None):
        if index is None:
            self.fields.append(field)
        else:
            self.fields.insert(index, field)

        realIndex = self.fields.index(field)
        return realIndex

    def removeLocalFields(self):
        while len(self.fields) != 0:
            self.fields.pop()

    def flattenLocalFields(self):
        """flattenLocalFields: merge the local fields of the current
        layer at the layer level.
        """
        if not self.isLayer():
            return
        # Concatenate all children of the current layer
        childrenFields = []
        for child in self.getExtendedFields():
            childrenFields.append(child)

        # Insert all the child at the place of the current field
        parentField = self.getParentField()
        indexInParentLayer = parentField.getLocalFields().index(self)
        parentField.getLocalFields().remove(self)
        index = indexInParentLayer
        for child in childrenFields:
            parentField.getLocalFields().insert(index, child)
            index += 1

    def popField(self, index=None):
        if index is None:
            self.fields.pop()
        else:
            self.fields.pop(index)

    def isLayer(self):
        if len(self.getLocalFields()) > 0:  # Means inner fields exist
            return True
        else:
            return False

    def getFieldByIndex(self, index):
        field = None
        try:
            field = self.getSymbol().getField().getExtendedFields()[index]
        finally:
            return field

    def getFieldLayers(self):
        layers = []
        for field in self.getLocalFields():
            if field.isLayer():
                layers.append(field)
        return layers

    def getFieldByID(self, ID):
        """getFieldByID: Return the field which ID is provided.
        """
        for field in self.getLocalFields():
            if str(field.getID()) == str(ID):
                return field
            elif field.isLayer():
                res = field.getFieldByID(ID)
                if res is not None:
                    return res
        return None

    def getCells(self):
        """getCells:
        Return all the messages parts which are in
        the specified field
        """
        # First we verify the field exists in the symbol
        if not self in self.getSymbol().getAllFields():
            logging.warn(_("The computing field is not part of the current symbol"))
            return []

        # Retrieve all sub-cells
        if self.isLayer():
            res = []
            for subField in self.getExtendedFields():
                res.append(subField.getCells())
            # Concatenate sub-cells
            finalRes = []
            for i in range(len(self.getMessages())):
                finalRes.append("")
            for i in range(len(res)):
                for j in range(len(res[i])):
                    finalRes[j] += res[i][j]
            return finalRes
        else:  # A leaf field
            res = []
            for message in self.getMessages():
                messageTable = message.applyAlignment()
                messageElt = messageTable[self.getIndex()]
                res.append(messageElt)
            return res

    def getUniqValuesByField(self):
        # First we verify the field exists in the symbol
        res = []
        for cell in self.getCells():
            if len(cell) > 0 and not cell in res:
                res.append(cell)
        return res

    ## Messages
    def getMessages(self):
        """Computes and returns messages
        associated with the current field"""
        return self.getSymbol().getMessages()

    def getMessageByID(self, ID):
        return self.getSymbol().getMessageByID(ID)

    ## Properties
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

        prop = Property("format", Format.STRING, self.format)
        prop.setIsEditable(True)
        prop.setPossibleValues(Format.getSupportedFormats())
        properties.append(prop)

        prop = Property("unitSize", Format.STRING, self.unitSize)
        prop.setIsEditable(True)
        prop.setPossibleValues([UnitSize.NONE, UnitSize.BITS4, UnitSize.BITS8, UnitSize.BITS16, UnitSize.BITS32, UnitSize.BITS64])
        properties.append(prop)

        prop = Property("sign", Format.STRING, self.sign)
        prop.setIsEditable(True)
        prop.setPossibleValues([Sign.SIGNED, Sign.UNSIGNED])
        properties.append(prop)

        prop = Property("endianess", Format.STRING, self.endianess)
        prop.setIsEditable(True)
        prop.setPossibleValues([Endianess.BIG, Endianess.LITTLE])
        properties.append(prop)
        return properties

    def save(self, root, namespace):
        """save:
                Creates an xml tree from a given xml root, with all necessary elements for the reconstruction of this field.

                @type root: lxml.etree.Element
                @param root: the root of this xml tree.
                @type namespace: string
                @param namespace: a precision for the xml subtree.
        """
        xmlField = etree.SubElement(root, "{" + namespace + "}field")
        xmlField.set("id", str(self.getID()))
        xmlField.set("name", str(self.getName()))
        xmlField.set("alignment", str(self.getAlignment()))
        xmlField.set("score", str(self.getScore()))

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

        xmlInnerFields = etree.SubElement(xmlField, "{" + namespace + "}fields")
        for innerField in self.getLocalFields():
            innerField.save(xmlInnerFields, namespace)

#+---------------------------------------------------------------------------+
#| Getters                                                                   |
#+---------------------------------------------------------------------------+
    def getID(self):
        return self.id

    def getName(self):
        return self.name

    def getSymbol(self):
        return self.symbol

    def getRegex(self):
        return self.regex

    def getRegexData(self):
        if self.isStatic():
            return self.regex.replace("(", "").replace(")", "").replace("?", "")
        else:
            return ""

    def getDescription(self):
        return self.description

    def getColor(self):
        if not self.isStatic():
            return "blue"
        return self.color

    def getIndex(self):
        return self.getSymbol().getExtendedFields().index(self)

    def getBackgroundColor(self):
        if self.getVariable() is None:
            return "yellow"
        return None

    def getScore(self):
        return self.score

    def getAlignment(self):
        return self.alignment.strip()

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

    def getLocalFields(self):
        return self.fields

    def getExtendedFields(self):
        result = []
        if self.isLayer():
            for field in self.getLocalFields():
                result.extend(field.getExtendedFields())
        else:
            result.append(self)
        return result

    def getFieldLayers(self):
        result = []
        for field in self.fields:
            if field.isLayer():
                result.append(field)
        return result

#+---------------------------------------------------------------------------+
#| Setters                                                                   |
#+---------------------------------------------------------------------------+
    def setID(self, ID):
        self.id = ID

    def setName(self, name):
        self.name = name

    def setSymbol(self, symbol):
        self.symbol = symbol

    def setRegex(self, regex):
        self.regex = regex

    def setDescription(self, description):
        self.description = description

    def setColor(self, color):
        self.color = color

    def setAlignment(self, alignment):
        self.alignment = alignment

    def setScore(self, score):
        self.score = score

    def setFormat(self, aFormat):
        self.format = aFormat
        for field in self.getLocalFields():
            field.setFormat(aFormat)

    def setUnitSize(self, unitSize):
        self.unitSize = unitSize
        for field in self.getLocalFields():
            field.setUnitSize(unitSize)

    def setSign(self, sign):
        self.sign = sign
        for field in self.getLocalFields():
            field.setSign(sign)

    def setEndianess(self, endianess):
        self.endianess = endianess
        for field in self.getLocalFields():
            field.setEndianess(endianess)

    def setVariable(self, variable):
        self.variable = variable

    def setFields(self, fields):
        self.fields = fields

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
        return Field("Default", "(.{,})", symbol)

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
            field_id = xmlRoot.get("id")
            field_name = xmlRoot.get("name")
            field_regex = ""
            if xmlRoot.find("{" + namespace + "}regex") is not None:
                field_regex = xmlRoot.find("{" + namespace + "}regex").text
            if field_regex is None:
                field_regex = ""
            alignmentSymbol = xmlRoot.get("alignment", None)
            scoreSymbol = float(xmlRoot.get("score", "0"))

            field = Field(field_name, field_regex, symbol)
            field.setID(field_id)
            field.setAlignment(alignmentSymbol)
            field.setScore(scoreSymbol)

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

            if xmlRoot.find("{" + namespace + "}fields") is not None:
                xmlInnerFields = xmlRoot.find("{" + namespace + "}fields")
                for xmlInnerField in xmlInnerFields.findall("{" + namespace + "}field"):
                    innerField = Field.loadFromXML(xmlInnerField, namespace, version, symbol)
                    if innerField != None:
                        field.addField(innerField)

            return field

        return None
