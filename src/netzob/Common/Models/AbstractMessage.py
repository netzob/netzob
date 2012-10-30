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
import uuid
import re

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.Type.TypeConvertor import TypeConvertor
from netzob.Common.NetzobException import NetzobException
from netzob.Common.MMSTD.Dictionary.Memory import Memory
from netzob.Common.Type.UnitSize import UnitSize
from netzob.Common.Type.Format import Format
from netzob.Common.Token import Token
from netzob.Common.Functions.FunctionApplicationTable import FunctionApplicationTable

#from netzob import _libRegex


#+---------------------------------------------------------------------------+
#| AbstractMessage:
#|     Definition of a message
#+---------------------------------------------------------------------------+
class AbstractMessage(object):

    def __init__(self, id, timestamp, data, type, pattern=[]):
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Common.Models.AbstractMessage.py')
        if id is None:
            self.id = uuid.uuid4()
        else:
            self.id = id

        self.timestamp = timestamp
        self.data = data
        self.type = type
        self.symbol = None
        self.session = None
        self.rightReductionFactor = 0
        self.leftReductionFactor = 0
        self.extraProperties = []
        self.visualizationFunctions = []
        self.transformationFunctions = []

        self.pattern = []
        if not pattern:
            self.compilePattern()
            # self.log.debug("empty {0}".format(str(self.getPattern()[0][0])))
        else:
            self.pattern = pattern
            # self.log.debug("not empty {0}".format(self.getPatternString()))

    #+-----------------------------------------------------------------------+
    #| getFactory
    #|     Abstract method to retrieve the associated factory
    #|     MUST BE IMPLEMENTED IN SUB CLASSES
    #+-----------------------------------------------------------------------+
    def getFactory(self):
        self.log.error("The message class doesn't have an associated factory !")
        raise NotImplementedError("The message class doesn't have an associated factory !")

    #+-----------------------------------------------------------------------+
    #| getProperties
    #|     Abstract method to retrieve the properties of the message
    #|     MUST BE IMPLEMENTED IN SUB CLASSES
    #+-----------------------------------------------------------------------+
    def getProperties(self):
        return self.extraProperties
#        self.log.error("The message class doesn't have a method 'getProperties' !")
#        raise NotImplementedError("The message class doesn't have a method 'getProperties' !")

    def addExtraProperty(self, property):
        self.extraProperties.append(property)

    #+----------------------------------------------
    #|`getStringData : compute a string representation
    #| of the data
    #| @return string(data)
    #+----------------------------------------------
    def getStringData(self):
        message = str(self.data)

        # Function with math functions
        for function in self.getTransformationFunctions():
            message = function.apply(message)

        return message

    def getReducedSize(self):
        start = 0
        end = len(self.getStringData())

        if self.getLeftReductionFactor() > 0:
            start = self.getLeftReductionFactor() * len(self.getStringData()) / 100
            if (end - start) % 2 == 1:
                start = start - 1
        if self.getRightReductionFactor() > 0:
            end = self.getRightReductionFactor() * len(self.getStringData()) / 100
            if (end - start) % 2 == 1:
                end = end + 1

        if (end - start) % 2 == 1:
            end = end + 1

        return len(self.getStringData()) - (end - start)

    def getReducedStringData(self):
        start = 0
        end = len(self.getStringData())

        if self.getLeftReductionFactor() > 0:
            start = self.getLeftReductionFactor() * len(self.getStringData()) / 100
            if (end - start) % 2 == 1:
                start = start - 1
        if self.getRightReductionFactor() > 0:
            end = self.getRightReductionFactor() * len(self.getStringData()) / 100
            if (end - start) % 2 == 1:
                end = end + 1

        return "".join(self.getStringData()[start:end])

    #+----------------------------------------------
    #| compilePattern:
    #|    compile the pattern of the data part in the Discover way (direction, [Token1, Token2...])
    #+----------------------------------------------
    def compilePattern(self):
        # self.log.debug("CALL COMPILE")
        tokens = []
        maxA = 126                # Max of ascii char not extended
        minA = 32                 # Min of ascii printable
        spe = [9, 10, 13]           # tab, \n, \r
        tempstr = ""
        tempbstr = ""
        ASCIITHRESHOLD = 5  # TODO put as option in UI
        isAsciiPrintable = lambda t: (ord(t) >= minA and ord(t) <= maxA)  # or ord(t) in spe
        current = ""
        tempLength = 0            # Temporary length of byte token

        canRemove = False
        if len(str(self.getData())) > 0:
            # self.log.debug(str(self.getData()))
            for i in TypeConvertor.netzobRawToPythonRaw(str(self.getData())):
                if isAsciiPrintable(i):
                    if tempLength:
                        if not canRemove:                                                  # Means that there where bytes before
                            tokens.append(Token(Format.HEX, tempLength, "constant", tempbstr))
                            canRemove = True
                        tempLength += 1
                    tempstr += i
                else:                                                               # We have a byte
                    if len(tempstr) > ASCIITHRESHOLD:
                        tempbstr = ""
                        tempLength = 0
                        tokens.append(Token(Format.STRING, len(tempstr), "constant", tempstr))
                        canRemove = False
                    elif canRemove:                                                 # It is not considered as a text string or we have a byte
                        tokens.pop()
                        tempbstr += tempstr
                        canRemove = False
                    elif tempstr:
                        tempLength += len(tempstr)
                        tempbstr += tempstr
                    tempstr = ""
                    tempbstr += i
                    tempLength += 1

            if len(tempstr) > ASCIITHRESHOLD or (not tokens and tempstr):
                tokens.append(Token(Format.STRING, len(tempstr), "constant", tempstr))
            else:
                if canRemove:
                    tokens.pop()
                tokens.append(Token(Format.HEX, tempLength, "constant", tempbstr))

        self.pattern.append(tokens)

    #+----------------------------------------------
    #| applyRegex: apply the current regex on the message
    #|  and return a table
    #+----------------------------------------------
    def applyAlignment(self, styled=False, encoded=False):
        fields = [self.symbol.getField()]
        dataToSplit = self.getReducedStringData()
        splittedData = self.applyAlignmentByFields(fields, dataToSplit)

        # Create the locationTable
        functionTable = FunctionApplicationTable(splittedData)

        if encoded is True or styled is True:
            i_data = 0
            for i_field in range(0, len(self.symbol.getExtendedFields())):
                field = self.symbol.getExtendedFields()[i_field]
                dataField = splittedData[i_field]

                # Add encoding functions
                if encoded is True:
                    for function in field.getEncodingFunctions():
                        functionTable.applyFunction(function, i_data, i_data + len(dataField))
                # Add visualization functions
                if styled is True and len(dataField) > 0:
                    # Add visualization functions obtained from fields
                    for function in field.getVisualizationFunctions():
                        functionTable.applyFunction(function, i_data, i_data + len(dataField))

                i_data = i_data + len(dataField)

            if styled is True:
                for (function, start, end) in self.getVisualizationFunctions():
                    functionTable.applyFunction(function, start, end)

        return functionTable.getResult()

    def applyAlignmentByFields(self, fields, dataToSplit):
        resSplittedData = []
        # Retrieve the data in columns
        splittedData = self.getSplittedData(fields, dataToSplit)

        if len(splittedData) != len(fields):
            logging.error("Nb of expected fields : {0}".format(self.symbol.getExtendedFields()))
            logging.error("fields : {0}".format(splittedData))
            logging.error("Inconsistency problem between number of fields and the regex application")
            return []

        # Apply transformation functions on each field
        transformedData = self.getTransformedData(fields, splittedData)

        # Recursive alignment on each fieldLayer
        i = 0
        for field in fields:
            if field.isLayer():
                resSplittedData.extend(self.applyAlignmentByFields(field.getLocalFields(), transformedData[i]))
            else:
                resSplittedData.append(transformedData[i])
            i += 1
        return resSplittedData

    def getTransformedData(self, fields, splittedData):
        # Add transformation functions
        i = 0
        for field in fields:

            functions = field.getTransformationFunctions()
            for function in functions:
                try:
                    splittedData[i] = function.apply(splittedData[i])
                except:
                    self.log.warning("Impossible to apply function {0} on data {1}.".format(function.getName(), splittedData[i]))
            i = i + 1
        return splittedData

    #+-----------------------------------------------------------------------+
    #| getSplittedData
    #|     Split the message using its symbol's regex and return an array of it
    #+-----------------------------------------------------------------------+
    def getSplittedData(self, fields, dataToSplit):
        if len(fields) == 1:
            return [dataToSplit]

        regex = []
        aligned = None

        dynamicDatas = None
        # First we compute the global regex
        for field in fields:
            # C Version :
            #regex.append("(" + field.getRegex() + ")")
            regex.append(field.getRegex())

        # Now we apply the regex over the message
        try:
            compiledRegex = re.compile("".join(regex))
            dynamicDatas = compiledRegex.match(dataToSplit)

        except AssertionError:
            raise NetzobException("This Python version only supports 100 named groups in regex")

        if dynamicDatas is None:
            self.log.warning("The regex of the group doesn't match one of its message")
            self.log.warning("Regex: " + "".join(regex))
            self.log.warning("Message: " + dataToSplit[:255] + "...")
            raise NetzobException("The regex of the group doesn't match one of its message")
        result = []
        iCol = 1

        for field in fields:
            try:
                start = dynamicDatas.start(iCol)
                end = dynamicDatas.end(iCol)
            except:
                self.log.warning("Possible error.")
            result.append(dataToSplit[start:end])

            iCol += 1
        return result

    #+-----------------------------------------------------------------------+
    #| GETTERS AND SETTERS
    #+-----------------------------------------------------------------------+
    def getID(self):
        return self.id

    def getType(self):
        return self.type

    def getData(self):
        """@deprecated: use getStringData instead"""
        return self.data.strip()

    def getSymbol(self):
        return self.symbol

    def getSession(self):
        return self.session

    def getRightReductionFactor(self):
        return self.rightReductionFactor

    def getLeftReductionFactor(self):
        return self.leftReductionFactor

    def getTimestamp(self):
        return self.timestamp

    def getPattern(self):
        return self.pattern

    def getPatternString(self):
        return str(self.pattern[0]) + ";" + str([str(i) for i in self.pattern[1]])

    def setID(self, id):
        self.id = id

    def setType(self, type):
        self.type = type

    def setData(self, data):
        self.data = data

    def setSymbol(self, symbol):
        self.symbol = symbol

    def setSession(self, session):
        self.session = session

    def setRightReductionFactor(self, factor):
        self.rightReductionFactor = factor
        self.leftReductionFactor = 0

    def setLeftReductionFactor(self, factor):
        self.leftReductionFactor = factor
        self.rightReductionFactor = 0

    def getVisualizationFunctions(self):
        """getVisualizationFunctions:
                Returns a list which contains all the visualization functions
                attach to the current message"""
        return self.visualizationFunctions

    def addVisualizationFunction(self, function, start, end):
        """addVisualizationFunction:
                Register a new visu function"""
        self.visualizationFunctions.append((function, start, end))

    def removeVisualizationFunction(self, function):
        """removeVisualizationFunction:
                Remove the provided function."""
        savedFunctions = []
        for (f, start, end) in self.visualizationFunctions:
            if function.getID() != f.getID():
                savedFunctions.append((f, start, end))
        self.visualizationFunctions = []
        for a in savedFunctions:
            self.visualizationFunctions.append(a)

    def removeTransformationFunction(self, function):
        """removeTransformationFunction:
                Remove a precised transformation function.

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
                Add a precised transformation function.

                @type function: netzob.Common.Functions
                @param function: the function that is added.
        """
        self.transformationFunctions.append(function)

    def getTransformationFunctions(self):
        return self.transformationFunctions
