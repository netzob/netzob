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
import glib
from netzob.Common.Type.Format import Format
from netzob.Common.Filters.EncodingFilter import EncodingFilter
from netzob.Common.Filters.VisualizationFilter import VisualizationFilter

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+


#+---------------------------------------------------------------------------+
#| FilterApplicationTable:
#|     Definition of a filter application table
#+---------------------------------------------------------------------------+
class FilterApplicationTable:

    def __init__(self, splittedData):
        self.splittedData = splittedData
        self.appliedFilters = []  # [(i_col, i_local_start, i_local_end, i_start, i_end, originalData, newData, filter), ...]
        # We create a conversion addressing table
        # {(i_data => i_data_filtered), ...}
        self.conversionAddressingTable = self.getInitialConversionAddressingTable()
        self.tags = []

    def applyFilter(self, filter, i_start, i_end):
        for (i_col, i_local_start, i_local_end, i_start, i_end, data) in self.getSegments(i_start, i_end):
            self.appliedFilters.append((i_col, i_local_start, i_local_end, i_start, i_end, data, filter))

    def getResult(self):
        result = []
        styledResult = []
        encodedResult = []

        # First we apply encoding filters
        # then we apply visualization filters
        encodingFilters = []
        visualizationFilters = []

        # We split applied filters between encoding and visualization ones
        for appliedFilter in self.appliedFilters:
            (i_col, i_local_start, i_end_local, i_start, i_end, data, filter) = appliedFilter
            if filter.getSuperType() == EncodingFilter.TYPE:
                encodingFilters.append(appliedFilter)
            elif filter.getSuperType() == VisualizationFilter.TYPE:
                visualizationFilters.append(appliedFilter)
            else:
                logging.warn("Unknown filter found in the list of applied filters.")

        # We apply encoding filters per column
        for col in range(0, len(self.splittedData)):
            newData = self.splittedData[col]
            # Search for filters which applies on current column
            toApplyFilter = []
            for (i_col, i_local_start, i_local_end, i_start, i_end, data, filter) in encodingFilters:
                if i_col == col:
                    toApplyFilter.append((i_col, i_local_start, i_local_end, i_start, i_end, data, filter))

            # Apply filters
            for (i_col, i_local_start, i_local_end, i_start, i_end, data, filter) in toApplyFilter:
                #logging.debug("Apply filter {0} on {1}".format(filter.getName(), self.splittedData[col][i_local_start:i_local_end]))
                #logging.debug("Conversion table (before):")
                #logging.debug(self.conversionAddressingTable)

                tmpData = filter.apply(self.splittedData[col][i_local_start:i_local_end])
                newData = newData[0:i_local_start] + tmpData + newData[i_local_end:]

                # update in the conversion addressing table
                filterConversionAddressingTable = filter.getConversionAddressingTable(self.splittedData[col][i_local_start:i_local_end])
                if filterConversionAddressingTable == None:
                     #logging.debug("Automatic deduction of the filter conversion addressing table")
                    self.updateConversionAddressingTable(i_start, i_end, i_start, i_start + len(tmpData))
                else:
                    #logging.debug("Apply the filter conversion addressing table")
                    self.updateConversionAddressingTableWithTable(filterConversionAddressingTable)

                #logging.debug("Conversion table (after):")
                #logging.debug(self.conversionAddressingTable)
            encodedResult.append(glib.markup_escape_text(newData))

        i_global = 0

        # We apply visualization filters per column
        for col in range(0, len(self.splittedData)):
            encodedCol = encodedResult[col]

            if len(encodedCol) > 0:
                toApplyFilter = []
                # Retrieve all the visualization filters we should apply on current column
                for (i_col, i_local_start, i_local_end, i_start, i_end, data, filter) in visualizationFilters:
                    if i_col == col:
                        toApplyFilter.append((i_col, i_local_start, i_local_end, i_start, i_end, data, filter))

                # Prepare filters for current column
                for (i_col, i_local_start, i_local_end, i_start, i_end, data, filter) in toApplyFilter:
                    (openTag, endTag) = filter.getTags()
                    if openTag != None:
                        self.registerTag(i_col, filter.getID(), i_local_start, openTag)
                    if endTag != None:
                        self.registerTag(i_col, filter.getID(), i_local_end, endTag)

                i_letter = 0
                # Retrieve the new content of current column (with opening and ending tags)
                for i_letter in range(0, len(self.splittedData[col])):
                    tags = self.getTags(col, i_letter)
                    # convert i_letter in i_encoded_letter
                    i_encoded_letter = self.conversionAddressingTable[i_global][0] - self.conversionAddressingTable[i_global - i_letter][0]

                    for tag in tags:
                        i_encoded_global_tag = self.conversionAddressingTable[i_global][0]
                        i_encoded_local_tag = len(encodedCol) - len(encodedResult[col]) + i_encoded_letter

                        encodedCol = self.insertTagInEncoded(col, i_encoded_local_tag, i_encoded_global_tag, tag, encodedCol)
                    i_global = i_global + 1

                tags = self.getTags(col, i_letter + 1)
                for tag in tags:
                    # Adding a tag at the the end of the field
                    encodedCol = encodedCol + tag

            styledResult.append(encodedCol)
        return styledResult

    def insertTagInEncoded(self, col, i_local, i_global, tag, currentValue):
        offset = len(tag)
        newValue = currentValue[:i_local] + tag + currentValue[i_local:]
        new_i = 0
        previousOld = []
        currentOld = []

        for i in self.conversionAddressingTable.keys():
            currentOld = self.conversionAddressingTable[i]
            if i == i_global:
                result = []
                for a in currentOld:
                    result.append(a + offset)
                self.conversionAddressingTable[i] = result
            elif i > i_global:
                o = currentOld[0] - previousOld[0]

                r = self.conversionAddressingTable[i - 1]
                t = []
                for a in r:
                    t.append(a + o)
                self.conversionAddressingTable[i] = t

            previousOld = currentOld
        return newValue

    def registerTag(self, i_col, idTag, i, tag):
        self.tags.append((i_col, idTag, i, tag))

    def getTags(self, col, i_local):
        tags = []
        for (i_col, idTag, i, tag) in self.tags:
            if i_col == col  and i == i_local:
                tags.append(tag)
        return tags

    def updateConversionAddressingTableWithTable(self, table):
        for original_indice in table.keys():
            self.conversionAddressingTable[original_indice] = table.get(original_indice)

    def updateConversionAddressingTable(self, old_start, old_end, new_start, new_end):
        sizeSegmentOld = old_end - old_start
        sizeSegment = new_end - new_start

        if sizeSegment == 0 or sizeSegmentOld == 0:
            return

        type = "equal"
        if sizeSegment < sizeSegmentOld:
            type = "reduction"
            factor = sizeSegmentOld // sizeSegment
        elif sizeSegment > sizeSegmentOld:
            type = "increase"
            factor = sizeSegment // sizeSegmentOld

        for i in self.conversionAddressingTable.keys():
            if i >= old_start and i < old_end:
                if type == "reduction":
                    tmp_i = (i - old_start)
                    new_i = old_start + tmp_i // factor
                    result = [new_i]
                elif type == "increase":
                    new_i = i
                    result = [new_i]
                    for a in range(0, factor):
                        new_i = new_i + 1
                        result.append(new_i)
                else:
                    result = self.conversionAddressingTable[i]
                self.conversionAddressingTable[i] = result
            elif i >= old_end:
                r = []
                for k in self.conversionAddressingTable[i]:
                    if type == "reduction":
                        r.append(k - factor)
                    elif type == "increase":
                        r.append(k + factor)
                    else:
                        r = self.conversionAddressingTable[i]
                self.conversionAddressingTable[i] = r

    def getInitialConversionAddressingTable(self):
        addressingTable = dict()
        i = 0
        for col in self.splittedData:
            for i_col in range(0, len(col)):
                addressingTable[i] = [i]
                i = i + 1
        return addressingTable

    def getSegments(self, i_start, i_end):
        i = 0
        i_local_start = 0
        i_local_end = 0
        segments = []
        in_segment = False
        for i_col in range(0, len(self.splittedData)):
            segment = ""
            col_data = self.splittedData[i_col]
            i_local_start = 0
            for i_col_data in range(0, len(col_data)):
                if i >= i_start and i < i_end and in_segment:
                    segment = segment + col_data[i_col_data]
                if i == i_start:
                    in_segment = True
                    i_local_start = i_col_data
                elif i == i_end and in_segment:
                    in_segment = False
                    i_local_end = i_col_data
                    segments.append((i_col, i_local_start, i_local_end, i_start, i_end, segment))
                    return segments
                i = i + 1

            if len(col_data) > 0:
                if in_segment == True and i == i_end:
                    i_local_end = len(col_data)
                    segments.append((i_col, i_local_start, i_local_end, i_start, i_end, segment))
                    segment = ""
                    in_segment = False
                elif in_segment == True:
                    # The segment closes in the next col
                    # first we close this one
                    i_local_end = i_col_data + 1
                    segments.append((i_col, i_local_start, i_local_end, i_start, i_end, segment))
                    segment = ""
                    in_segment == True
                    i_local_start = 0
        if i == i_end and in_segment == True:
            in_segment = False
            i_local_end = len(col_data) + 1
            segments.append((i_col, i_local_start, i_local_end, i_start, i_end, segment))
            return segments

        #logging.warn("i_end never reached in the message (i_end=%d, i=%d)" % (i_end, i))
        return segments
