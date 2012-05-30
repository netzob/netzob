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
import logging
import uuid
import re
import glib

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.Type.TypeConvertor import TypeConvertor
from netzob.Common.NetzobException import NetzobException
from netzob.Common.MMSTD.Dictionary.Variable import Variable
from netzob.Common.MMSTD.Dictionary.Memory import Memory
from netzob.Common.Type.UnitSize import UnitSize
from netzob.Common.Type.Format import Format
from netzob.Common.Token import Token
from netzob.Common.Filters.FilterApplicationTable import FilterApplicationTable


#+---------------------------------------------------------------------------+
#| AbstractMessage:
#|     Definition of a message
#+---------------------------------------------------------------------------+
class AbstractMessage():

    def __init__(self, id, timestamp, data, type, pattern=[]):
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Common.Models.AbstractMessage.py')
        if id == None:
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
        self.visualizationFilters = []
        self.encodingFilters = []

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
        self.log.error("The message class doesn't have a method 'getProperties' !")
        raise NotImplementedError("The message class doesn't have a method 'getProperties' !")

    #+-----------------------------------------------------------------------+
    #| addVisualizationFilter
    #|     Add a visualization filter
    #+-----------------------------------------------------------------------+
    def addVisualizationFilter(self, filter, start, end):
        self.visualizationFilters.append((filter, start, end))

    #+-----------------------------------------------------------------------+
    #| removeVisualizationFilter
    #|     Remove a visualization filter
    #+-----------------------------------------------------------------------+
    def removeVisualizationFilter(self, filter):
        savedFilters = []
        for (f, start, end) in self.visualizationFilters:
            if filter.getID() != f.getID():
                savedFilters.append((f, start, end))
        self.visualizationFilters = []
        for a in savedFilters:
            self.visualizationFilters.append(a)

    #+-----------------------------------------------------------------------+
    #| addEncodingFilter
    #|     Add an encoding filter
    #+-----------------------------------------------------------------------+
    def addEncodingFilter(self, filter):
        self.encodingFilters.append(filter)

    #+-----------------------------------------------------------------------+
    #| removeEncodingFilter
    #|     Remove an encoding filter
    #+-----------------------------------------------------------------------+
    def removeEncodingFilter(self, filter):
        if filter in self.encodingFilters:
            self.encodingFilters.remove(filter)

    #+-----------------------------------------------------------------------+
    #| getEncodingFilters
    #|     Computes the encoding filters associated with current message
    #+-----------------------------------------------------------------------+
    def getEncodingFilters(self):
        filters = []

        # First we add all the encoding filters attached to the symbol
        filters.extend(self.symbol.getEncodingFilters())

        # We add the locally defined encoding filters
        filters.extend(self.encodingFilters)

        return filters

    #+----------------------------------------------
    #|`getStringData : compute a string representation
    #| of the data
    #| @return string(data)
    #+----------------------------------------------
    def getStringData(self):
        return str(self.data)

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
        if self.getSymbol().getAlignmentType() == "regex":
            return self.getFields(styled, encoded)
        else:
            return self.applyDelimiter(styled, encoded)

    def getFields(self, encoding=False, visualization=False):
        # Retrieve the data in columns
        splittedData = self.getSplittedData()

        if len(splittedData) != len(self.symbol.getFields()):
            logging.error("Inconsistency problem between number of fields and the regex application")
            return []

        # Add Mathematics filters
        i = 0
        for field in self.symbol.getFields():
            for filter in field.getMathematicFilters():
                splittedData[i] = filter.apply(splittedData[i])
            i = i + 1

        # Create the locationTable
        filterTable = FilterApplicationTable(splittedData)

        if encoding == True or visualization == True:
            i_data = 0
            for i_field in range(0, len(self.symbol.getFields())):
                field = self.symbol.getFields()[i_field]
                dataField = splittedData[i_field]

                # Add encoding filters
                if encoding == True:
                    for filter in field.getEncodingFilters():
                        filterTable.applyFilter(filter, i_data, i_data + len(dataField))
                # Add visualization filters
                if visualization == True:
                    # Add visualization filters obtained from fields
                    for filter in field.getVisualizationFilters():
                        if len(dataField) > 0:
                            filterTable.applyFilter(filter, i_data, i_data + len(dataField))
                i_data = i_data + len(dataField)

            # Add visualization filters of our current message
            if visualization == True:
                for (filter, start, end) in self.getVisualizationFilters():
                    filterTable.applyFilter(filter, start, end)

        return filterTable.getResult()

    #+-----------------------------------------------------------------------+
    #| getSplittedData
    #|     Split the message using its symbol's regex and return an array of it
    #+-----------------------------------------------------------------------+
    def getSplittedData(self):
        regex = []
        dynamicDatas = None
        # First we compute the global regex
        for field in self.symbol.getFields():
            regex.append(field.getRegex())

        # Now we apply the regex over the message
        try:
            compiledRegex = re.compile("".join(regex))
            data = self.getReducedStringData()
            dynamicDatas = compiledRegex.match(data)

        except AssertionError:
            raise NetzobException("This Python version only supports 100 named groups in regex")

        if dynamicDatas == None:
            self.log.warning("The regex of the group doesn't match one of its message")
            self.log.warning("Regex: " + "".join(regex))
            self.log.warning("Message: " + data[:255] + "...")
            raise NetzobException("The regex of the group doesn't match one of its message")

        result = []
        iCol = 1
        for field in self.symbol.getFields():
            if field.isStatic():
#                if encoded:
#                    result.append(glib.markup_escape_text(TypeConvertor.encodeNetzobRawToGivenField(field.getRegex(), field)))
#                else:
#                    result.append(glib.markup_escape_text(field.getRegex()))
                result.append(field.getRegex())
            else:
                start = dynamicDatas.start(iCol)
                end = dynamicDatas.end(iCol)
#                if encoded:
#                    result.append(glib.markup_escape_text(TypeConvertor.encodeNetzobRawToGivenField(data[start:end], field)))
#                else:
#                    result.append(glib.markup_escape_text(data[start:end]))
                result.append(data[start:end])
                iCol += 1
        return result

#    def getStyledData(self, styled=False, encoded=False):
#        result = []
#        splittedData = self.getSplittedData(encoded)
#
#        if styled == False:
#            return splittedData
#
#        iGlobal = 0
#        iCol = 0
#
#        for data in splittedData:
#            localResult = ""
#            # Retrieve the field associated with this value
#            field = self.symbol.getFieldByIndex(iCol)
#            # Retrieve the unit size
#            unitSize = Format.getUnitSize(field.getFormat())
#            # First we apply filters on all the message
#            for filter in self.getVisualizationFilters():
#                if filter.isValid(0, -1, data, unitSize):
#                    localResult += filter.apply(data)
#
#            for iLocal in range(0, len(data)):
#                tmp_result = data[iLocal]
#                if sizeFormat != None:
#                    for filter in self.getVisualizationFilters():
#                        if filter.isValid(iGlobal + iLocal, tmp_result, sizeFormat):
#                            tmp_result = filter.apply(tmp_result)
#
#                localResult += tmp_result
#
#            # Now we apply the color to the fields
#            for filter in field.getVisualizationFilters():
#                localResult = filter.apply(localResult)
#
#            iGlobal = iGlobal + len(data)
#            result.append(localResult)
#            iCol += 1
#        return result
#
#    def getVisualizationData(self, styled=False, encoded=False):
#        result = self.getStyledData(styled, encoded)
#        return result

    #+----------------------------------------------
    #| applyDelimiter: apply the current delimiter on the message
    #|  and return a table
    #+----------------------------------------------
    def applyDelimiter(self, styled=False, encoded=False):
        delimiter = self.getSymbol().getRawDelimiter()
        res = []
        iField = -1
        for field in self.symbol.getFields():
            if field.getName() == "__sep__":
                tmp = delimiter
            else:
                iField += 1
                try:
                    tmp = self.getStringData().split(delimiter)[iField]
                except IndexError:
                    tmp = ""

            if field.getColor() == "" or field.getColor() == None:
                color = 'blue'
            else:
                color = field.getColor()

            # Define the background color
            if field.getBackgroundColor() != None:
                backgroundColor = 'background="' + field.getBackgroundColor() + '"'
            else:
                backgroundColor = ""

            if styled:
                if encoded:
                    res.append('<span foreground="' + color + '" ' + backgroundColor + ' font_family="monospace">' + glib.markup_escape_text(TypeConvertor.encodeNetzobRawToGivenField(tmp, field)) + '</span>')
                else:
                    res.append('<span foreground="' + color + '" ' + backgroundColor + ' font_family="monospace">' + tmp + '</span>')
            else:
                if encoded:
                    res.append(glib.markup_escape_text(TypeConvertor.encodeNetzobRawToGivenField(tmp, field)))
                else:
                    res.append(tmp)
        return res

    #+-----------------------------------------------------------------------+
    #| GETTERS AND SETTERS
    #+-----------------------------------------------------------------------+
    def getID(self):
        return self.id

    def getType(self):
        return self.type

    def getData(self):
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

    def getVisualizationFilters(self):
        return self.visualizationFilters

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
