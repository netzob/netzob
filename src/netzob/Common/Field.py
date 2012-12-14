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
from netzob.Common.Functions.Encoding.FormatFunction import FormatFunction
from netzob.Common.Type.TypeIdentifier import TypeIdentifier
from netzob.Common.Functions.Visualization.TextColorFunction import TextColorFunction
from netzob.Common.MMSTD.Dictionary.DataTypes.BinaryType import BinaryType
from netzob.Common.MMSTD.Dictionary.Variables.AbstractVariable import \
    AbstractVariable
from netzob.Common.MMSTD.Dictionary.Variables.AggregateVariable import \
    AggregateVariable
from netzob.Common.MMSTD.Dictionary.Variables.AlternateVariable import \
    AlternateVariable
from netzob.Common.MMSTD.Dictionary.Variables.DataVariable import DataVariable
from netzob.Common.ProjectConfiguration import ProjectConfiguration
from netzob.Common.Property import Property
from netzob.Common.Type.Endianess import Endianess
from netzob.Common.Type.Format import Format
from netzob.Common.Type.Sign import Sign
from netzob.Common.Type.TypeConvertor import TypeConvertor
from netzob.Common.Type.UnitSize import UnitSize


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
        self.id = str(uuid.uuid4())
        self.name = name
        self.symbol = symbol
        self.description = ""
        self.color = "black"

        # Partitionment
        self.score = 0.0
        self.alignment = ""
        self.regex = regex

        # Functions
        self.encodingFunctions = []
        self.visualizationFunctions = []
        self.transformationFunctions = []

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

    ## Functions
    def addVisualizationFunction(self, function):
        self.visualizationFunctions.append(function)

    def cleanVisualizationFunctions(self):
        self.visualizationFunctions = []

#    def getVisualizationFunctions(self):
#        return self.visualizationFunctions

    def removeVisualizationFunction(self, function):
        self.visualizationFunctions.remove(function)

    def addEncodingFunction(self, function):
        self.encodingFunctions.append(function)

    def removeEncodingFunction(self, function):
        if function in self.encodingFunctions:
            self.encodingFunctions.remove(function)

#    def getEncodingFunctions(self):
#        functions = []
#        for field in self.getExtendedFields():
#            functions.extend(field.getEncodingFunctions())
#        functions.extend(self.encodingFunctions)

    def getVisualizationFunctions(self):
        """getVisualizationFunctions:
                Get the visualization functions applied on this field.

                @rtype: netzob.Common.Functions List
                @return: a list of all needed functions.
        """
        functions = []

        # dynamic fields are in Blue
        if not self.isStatic():
            functions.append(TextColorFunction("Dynamic Field", "blue"))
#            # fields with no variable define are in yellow
#            if self.variable is None:
#                functions.append(BackgroundColorFunction("Default variable", "yellow"))

        return functions

    def getEncodingFunctions(self):
        """getEncodingFunctions:
                Calls computeFormatEncodingFunction.
        """
        functions = []
        # Following functions must be considered :
        functions.append(self.computeFormatEncodingFunction())
        return functions

    def removeTransformationFunction(self, function):
        """removeTransformationFunction:
                Remove a precised function.

                @type function: netzob.Common.Functions
                @param function: the function that is removed.
        """
        fToRemove = None
        for mFunction in self.transformationFunctions:
            if mFunction.getName() == function.getName():
                fToRemove = mFunction
                break
        if fToRemove is not None:
            self.transformationFunctions.remove(fToRemove)

    def addTransformationFunction(self, function):
        """addTransformationFunction:
                Add a precised function.

                @type function: netzob.Common.Functions
                @param function: the function that is added.
        """
        self.transformationFunctions.append(function)

    def computeFormatEncodingFunction(self):
        """computeFormatEncodingFunction:
                Get the format function applied on this field. It tells how the data are displayed.

                @rtype: netzob.Common.Functions.FormatFunction
                @return: the computed format function.
        """
        return FormatFunction("Field Format Encoding", self.format, self.unitSize, self.endianess, self.sign)

    def computeSignEncodingFunction(self):
        """computeSignEncodingFunction:
                Does nothing.

                @return: None
        """
        return None

    def computeEndianessEncodingFunction(self):
        """computeEndianessEncodingFunction:
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
        if self.regex == "" or self.regex is None:
            return ""
        elif self.isStatic():
            return self.getRegex().replace(self.getRegexData(), TypeConvertor.encodeNetzobRawToGivenType(self.getRegexData(), self.format))
        else:  # Dynamic or complex regex
            return self.regex

    def isStatic(self):
        """isStatic:
                Tells if a regex is static (is of the form '(data)').

                @rtype: boolean
                @return: True if the regex is static.
        """
        if (re.match("\([0-9a-f]*\)\??", self.regex) is not None) and self.getName() != "__sep__":
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

    def isRegexOptional(self):
        """isRegexOptional:
                Tells if a regex is optional (i.e. has a '?' at the end).

                @rtype: boolean
                @return: True if the regex is optional.
        """
        if self.getRegex()[-1] == '?':
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

    def fixRegex(self):
        """fixRegex: for regex that only renders fixed-size cells,
        directly fix the regex."""
        if not self.isRegexOnlyDynamic():
            return
        cells = self.getCells()
        refSize = len(cells[0])
        for cell in cells[1:]:
            if len(cell) != refSize:
                return
        self.setRegex("(.{" + str(refSize) + "})")

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

        # Loop to detect fixed-sized dynamic fields
        for innerField in self.getLocalFields():
            innerField.fixRegex()

        # Clean created fields (remove fields that produce only empty cells)
        self.removeEmptyFields()

    #+----------------------------------------------
    #| simplePartitioning:
    #|  Do message partitioning according to column variation
    #+----------------------------------------------
    def simplePartitioning(self, unitSize, status_cb=None, idStop_cb=None):
        logging.debug("Compute the simple partitioning on current symbol")
        # Restore fields to the default situation
        self.resetPartitioning()
        # Retrieve the biggest message
        maxLen = 0
        cells = self.getCells()
        for cell in cells:
            curLen = len(cell)
            if curLen > maxLen:
                maxLen = curLen
        logging.debug("Size of the longest message: {0}".format(maxLen))

        # Try to see if the column is static or variable
        resultString = []
        resultMask = []

        # Stop and clean if requested
        if idStop_cb is not None:
            if idStop_cb():
                self.removeLocalFields()
                return

        step = float(100) / float(maxLen)
        totalPercent = 0
        # Loop until maxLen to build a mask such as:
        #        'totoploptoto'
        #        'tototatatotototo'
        #        'totoabcdtotototo'
        #  ref = 'toto----totototo'
        # mask = '............????'
        # Where '-' means a different character
        #   and '.' means a mandatory character
        #   and '?' means an optional similar character
        SIMILAR = "0"
        DIFFERENT = "1"
        SIMILAR_OPTIONAL = "2"
        DIFFERENT_OPTIONAL = "3"

        for it in range(maxLen):
            ref = ""
            isDifferent = False
            oneCellIsTooShort = False

            # Stop and clean if requested
            if it % 10 == 0 and idStop_cb is not None:
                if idStop_cb():
                    self.removeLocalFields()
                    return

            # Loop through each cells of the column
            for cell in cells:
                if it < len(cell):
                    tmp = cell[it]
                    if ref == "":
                        ref = tmp
                    if ref != tmp:
                        isDifferent = True
                        break
                else:
                    oneCellIsTooShort = True

            if isDifferent:
                resultString.append("-")
                if oneCellIsTooShort:
                    resultMask.append(DIFFERENT_OPTIONAL)
                else:
                    resultMask.append(DIFFERENT)
            else:
                resultString.append(ref)
                if oneCellIsTooShort:
                    resultMask.append(SIMILAR_OPTIONAL)
                else:
                    resultMask.append(SIMILAR)

            totalPercent += step
            if it % 20 == 0 and status_cb is not None:
                status_cb(totalPercent, None)

        # Apply unitSize
        if unitSize != UnitSize.NONE:
            unitSize = UnitSize.getSizeInBits(unitSize)
            nbLetters = unitSize / 4
            tmpResultString = []
            tmpResultMask = []
            for i in range(0, len(resultString), nbLetters):
                # Stop and clean if requested
                if idStop_cb is not None:
                    if idStop_cb():
                        self.removeLocalFields()
                        return

                tmpText = resultString[i:i + nbLetters]
                tmpMask = resultMask[i:i + nbLetters]
                if "-" in tmpText:
                    for j in range(len(tmpText)):
                        tmpResultString.append("-")
                        tmpResultMask.append(DIFFERENT)
                else:
                    tmpResultString.extend(tmpText)
                    tmpResultMask.extend(tmpMask)
            resultString = tmpResultString
            resultMask = tmpResultMask

        ## Build of the fields
        self.removeLocalFields()
        nbElements = 0
        iField = 0
        typeOfLastElement = None
        fields = []
        currentField = Field("tmp", "", self.getSymbol())
        for it in range(0, len(resultMask)):
            nbElements += 1

            if resultMask[it] == DIFFERENT:  # The current column is dynamic
                if typeOfLastElement is None or typeOfLastElement == DIFFERENT:
                    typeOfLastElement = DIFFERENT
                    if currentField is None:
                        currentField = Field("tmp", "(.{,1})", self.getSymbol())
                        nbElements = 1
                    else:
                        currentField.setRegex("(.{," + str(nbElements) + "})")
                else:  # Last element was SIMILAR, wo we've reached a field boundary
                    typeOfLastElement = DIFFERENT
                    fields.append(currentField)
                    iField += 1
                    currentField = Field("tmp", "(.{,1})", self.getSymbol())
                    nbElements = 1
            elif resultMask[it] == SIMILAR:
                # In a static field
                if typeOfLastElement is None or typeOfLastElement == SIMILAR:
                    typeOfLastElement = SIMILAR
                    if currentField is None:
                        currentField = Field("tmp", resultString[it], self.getSymbol())
                    else:
                        currentField.setRegex(currentField.getRegex() + resultString[it])
                else:  # Last element was DIFFERENT, wo we've reached a field boundary
                    typeOfLastElement = SIMILAR
                    fields.append(currentField)
                    currentField = Field("tmp", resultString[it], self.getSymbol())
                    iField += 1

            elif resultMask[it] == SIMILAR_OPTIONAL:
                # In a static optional field
                if typeOfLastElement is None or typeOfLastElement == resultMask[it]:
                    typeOfLastElement = resultMask[it]

                    if currentField is None:
                        currentField = Field("tmp", "(" + resultString[it] + ")?", self.getSymbol())
                        nbElements = 1
                    else:
                        currentField.setRegex("(" + currentField.getRegex()[1:len(currentField.getRegex()) - 2] + resultString[it] + ")?")
                else:
                    typeOfLastElement = resultMask[it]
                    fields.append(currentField)
                    currentField = Field("tmp", "(" + resultString[it] + ")?", self.getSymbol())
                    iField += 1
        if currentField is not None:
            fields.append(currentField)

        for field in fields:
            # Add parentheses where needed
            if field.getRegex()[0] != "(":
                field.setRegex("(" + field.getRegex())
            if field.getRegex()[-1] != ")" and field.getRegex()[-1] != "?":
                field.setRegex(field.getRegex() + ")")
            # Add field to local fields of the current object
            self.addField(field)

        # Loop to detect fixed-sized dynamic fields
        for innerField in self.getLocalFields():
            innerField.fixRegex()

        # Stop and clean if requested
        if idStop_cb is not None:
            if idStop_cb():
                self.removeLocalFields()
                return

    #+----------------------------------------------
    #| slickRegex:
    #|  try to make smooth the regex, by deleting tiny static
    #|  sequences that are between big dynamic sequences
    #+----------------------------------------------
    def slickRegex(self, project):
        # Verify that targeted fields are in the same layer
        extendedFields = self.getExtendedFields()
        parent = extendedFields[0].getParentField()
        for field in extendedFields[1:]:
            if field.getParentField() != parent:
                logging.warn("Can't smooth regex from fields that are part of different layers.")
                return

        # Main smooth routine
        mergeDone = False
        i = extendedFields[0].getIndex()  # Retrieve the index of the first field to consider
        i = i + 1  # We start at the second field
        nbFields = len(extendedFields)
        while i < nbFields - 1:
            aField = self.getFieldByIndex(i)
            if aField is None:
                return
            if aField.isStatic():
                if len(aField.getRegexData()) <= 2:  # Means a potential negligeable element that can be merged with its neighbours
                    precField = self.getFieldByIndex(i - 1)
                    if precField.isRegexOnlyDynamic():
                        nextField = self.getFieldByIndex(i + 1)
                        if nextField.isRegexOnlyDynamic():
                            mergeDone = True
                            minSize = len(aField.getRegexData())
                            maxSize = len(aField.getRegexData())

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

                            # Update current field regex
                            aField.setRegex("(.{" + minSize + "," + maxSize + "})")

                            # Delete the now usless precedent and next fields
                            parent = nextField.getParentField()
                            parent.removeLocalField(nextField)
                            parent = precField.getParentField()
                            parent.removeLocalField(precField)
            i += 1

        if mergeDone:
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

    def concatFields(self, lastField):
        """concatFields: concat all the next fields with the current one
        until the lastField is reached.
        @return: a tupple that indicates if the function has correctly been processed, and if not, the error message."""
        logging.debug("Concat field from {0} to {1}".format(self.getName(), lastField.getName()))

        # If no last field is provided we stop here
        if lastField == None:
            msg = "Last field is not provided."
            return (False, msg)

        # Retrieve all the fields at the same level
        parentField = self.getParentField()
        localFields = parentField.getLocalFields()

        if lastField not in localFields:
            msg = "Impossible to merge with field {0} since it's not part of the same layer.".format(lastField.getName())
            logging.warn(msg)
            return (False, msg)

        lastMerge = False
        while not lastMerge:
            # retrieve next field
            nextField = self.getNextFieldInCurrentLayer()

            if nextField is None:
                return (True, "")

            if nextField.getID() == lastField.getID():
                lastMerge = True

            self.concatWithNextField()
        return (True, "")

    def getNextFieldInCurrentLayer(self):
        """getNextFieldInCurrentLayer:
            Computes the next field from the same layer.
            Returns None if it doesn't exist"""
        parentField = self.getParentField()
        localFields = parentField.getLocalFields()
        indexField1 = localFields.index(self)
        indexField2 = indexField1 + 1
        try:
            return localFields[indexField2]
        except IndexError:
            return None

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
        regex = ""
        optional = False
        if field1.isRegexOptional():
            regex += field1.getRegex()[1:-2]
            optional = True
        else:
            regex += field1.getRegex()[1:-1]

        if field2.isRegexOptional():
            regex += field2.getRegex()[1:-2]
            optional = True
        else:
            regex += field2.getRegex()[1:-1]

        if optional:
            field1.setRegex("(" + regex + ")?")
        else:
            field1.setRegex("(" + regex + ")")
        localFields.remove(field2)
        return 1

    #+----------------------------------------------
    #| splitField:
    #|  Split a field in two fields
    #|  return False if the split does not occure, else True
    #+----------------------------------------------
    def splitField(self, split_position, split_align):
        if split_position == 0:
            return False

        # Find the static/dynamic cols
        cells = self.getCells()
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
            regex1 = "(" + ref1 + ")"
        else:
            if split_align == "left":
                # The size is fixed
                regex1 = "(.{" + str(lenDyn1) + "})"
            else:
                regex1 = "(.{," + str(lenDyn1) + "})"
        if isStatic2:
            regex2 = "(" + ref2 + ")"
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

        new_format = self.getFormat()
        indexOldField = self.getIndex()
        parentField = self.getParentField()

        # Create two new fields
        field1 = Field(self.getName() + "-1", regex1, self.getSymbol())
        field1.setFormat(new_format)

        field2 = Field(self.getName() + "-2", regex2, self.getSymbol())
        field2.setFormat(new_format)

        if parentField is None:  # Parent is Symbol
            self.addField(field1)
            self.addField(field2)
            return True
        else:
            index2 = parentField.addField(field2, indexOldField)
            parentField.addField(field1, index2)
            parentField.removeLocalField(self)
            return True

    #+-----------------------------------------------------------------------+
    #| getPossibleTypes:
    #|     Retrieve all the possible types for the current field
    #+-----------------------------------------------------------------------+
    def getPossibleTypes(self):
        # Retrieve all the part of the messages which are in the given field
        cells = self.getUniqValuesByField()
        typeIdentifier = TypeIdentifier()
        return typeIdentifier.getTypes("".join(cells))

    #+-----------------------------------------------------------------------+
    #| getStyledPossibleTypes:
    #|     Retrieve all the possibles types for a field and we colorize
    #|     the selected one we an HTML RED SPAN
    #+-----------------------------------------------------------------------+
    def getStyledPossibleTypes(self):
        tmpTypes = self.getPossibleTypes()
        for i in range(len(tmpTypes)):
            if tmpTypes[i] == self.getFormat():
                tmpTypes[i] = "<span foreground=\"red\">" + self.getFormat() + "</span>"
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
            value = self.getRegex()
            if value.endswith("?"):
                value = value[1:len(value) - 2]
            else:
                value = value[1:len(value) - 1]

            value = TypeConvertor.netzobRawToBitArray(value)
            variable = DataVariable(str(uuid.uuid4()), self.getName(), False, False, BinaryType(True, len(value), len(value)), value.to01())  # A static field is neither mutable nor random.
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

        variable = AggregateVariable(str(uuid.uuid4()), "Aggregate", False, False, None)
        alternateVar = AlternateVariable(str(uuid.uuid4()), "Alternate", True, False, None)
        for d in domain:
            child = DataVariable(str(uuid.uuid4()), "defaultVariable", False, False, BinaryType(True, len(d), len(d)), d.to01())
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

    def removeEmptyFields(self, cb_status):
        """
        removeEmptyFields: we look for useless fields (i.e. fields
        that produces only empty cells) and remove them.
        """
        fieldsToRemove = []
        fields = self.getExtendedFields()
        step = float(100) / float(len(fields))
        totalPercent = 0
        for innerField in fields:
            # We try to see if this field produces only empty values when applied on messages
            cells = innerField.getCells()
            cells = "".join(cells)
            if cb_status is not None:
                totalPercent += step
                cb_status(4, totalPercent, None)
            if cells == "":
                # Concatenate the current useless inner field with the next field
                fieldsToRemove.append(innerField)
        for field in fieldsToRemove:
            field.getParentField().removeLocalField(field)

    def removeLocalField(self, field):
        """removeLocalField:
        Remove from the current field's children, the provided field"""
        if field in self.fields:
            self.fields.remove(field)
        else:
            self.log.warning("Cannot remove field {0} from the children of field {1}.".format(field.getName(), self.getName()))

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
            logging.warn("The computing field is not part of the current symbol")
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

    def getTransformationFunctions(self):
        return self.transformationFunctions

    def getVariable(self):
        if self.variable is None:
            self.variable = self.generateDefaultVariable(self.symbol)
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
            field_id = str(xmlRoot.get("id"))
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
