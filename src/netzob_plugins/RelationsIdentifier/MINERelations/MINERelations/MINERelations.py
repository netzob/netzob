# -*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|          01001110 01100101 01110100 01111010 01101111 01100010            |
#|                                                                           |
#|               Netzob : Inferring communication protocols                  |
#+---------------------------------------------------------------------------+
#| Copyright (C) 2011-2014 Georges Bossert and Frédéric Guihéry              |
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
import errno
import time
import uuid
from gettext import gettext as _

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+
from minepy import MINE
import numpy

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.Plugins.RelationsIdentifier.AbstractRelationsIdentifier import AbstractRelationsIdentifier


class MINERelations(AbstractRelationsIdentifier):
    """Model of MINE Relations Identifier plugin"""

    def __init__(self, netzob):
        super(MINERelations, self).__init__("MINE Relations Identifier", netzob)
        # Create logger with the given configuration
        self.log = logging.getLogger('netzob.Import.PcapImport.py')

    def debug_mine_stats(self, mine):
        logging.debug("MIC: " + str(mine.mic()))
        logging.debug("MAS: " + str(mine.mas()))
        logging.debug("MEV: " + str(mine.mev()))
        logging.debug("MCN (eps=0): " + str(mine.mcn(0)))
        logging.debug("MCN (eps=1-MIC): " + str(mine.mcn_general()))

    def findCorrelationsInSymbols(self, symbols, minMic=0.7):
        """exportButton_clicked_cb:
            Callback executed when the user clicks on the export button"""

        attributeValuesPerSymbols = self.generateAttributeValues(symbols)

        # For each symbol, we write in a temp file the CSV
        # execute the MINE relation finder and parse its results
        results = dict()
        for symbolName in attributeValuesPerSymbols.keys():
            (symbol, attributeValues_headers, attributeValues) = attributeValuesPerSymbols[symbolName]
            symbolResults = []

            # MINE computation of each field combinations
            i = -1
            for values_x in attributeValues[:-1]:
                i += 1
                j = i+1
                for values_y in attributeValues[i+1:]:
                    mine = MINE(alpha=0.6, c=15)
                    mine.compute_score(numpy.array(values_x), numpy.array(values_y))
                    mic = round(mine.mic(), 2)
                    if mic > float(minMic):
                        # We add the relation to the results
                        x_attribute = attributeValues_headers[i][:1]
                        y_attribute = attributeValues_headers[j][:1]
                        x_field = symbol.getFieldByID(attributeValues_headers[i][2:])
                        y_field = symbol.getFieldByID(attributeValues_headers[j][2:])
                        # The relation should not apply on the same field
                        if x_field.getID() != y_field.getID():
                            pearson = numpy.corrcoef(values_x, values_y)[0, 1]
                            if not numpy.isnan(pearson):
                                pearson = round(pearson, 2)
                            relation_type = self.findRelationType(x_attribute, y_attribute)
                            self.debug_mine_stats(mine)
                            logging.info("Correlation found between '" + x_attribute + ":" + x_field.getName() + "' and '" + y_attribute + ":" + y_field.getName() + "'")
                            logging.info("  MIC score: " + str(mic))
                            logging.info("  Pearson score: " + str(pearson))
                            id_relation = str(uuid.uuid4())
                            symbolResults.append({'id': id_relation,
                                                  "relation_type": relation_type,
                                                  'x_field': x_field,
                                                  'x_attribute': x_attribute,
                                                  'y_field': y_field,
                                                  'y_attribute': y_attribute,
                                                  'mic': mic,
                                                  'pearson': pearson})
                    j += 1
            # Concatenate results
            if len(symbolResults) > 0:
                results[symbol.getName()] = symbolResults
        return results

    def findRelationType(self, x_attribute, y_attribute):
        typeRelation = "Unknown"
        if (x_attribute == "v" and y_attribute == "s") or (x_attribute == "s" and y_attribute == "v"):
            typeRelation = "SizeRelation"
        elif (x_attribute == x_attribute) and x_attribute == "v":
            typeRelation = "DataRelation"
        return typeRelation

    def generateAttributeValues(self, symbols):
        attributeValuesPerSymbols = dict()
        for symbol in symbols:
            (attributeValues_headers, attributeValues) = self.generateAttributeValuesForSymbol(symbol)
            attributeValuesPerSymbols[symbol.getName()] = (symbol, attributeValues_headers, attributeValues)
        return attributeValuesPerSymbols

    def generateAttributeValuesForSymbol(self, symbol):
        # First we compute the possible list of payloads
        lines = []
        line_header = []

        # Compute the table of values
        valuesTable = []
        fields = symbol.getExtendedFields()
        for field in fields:
            valuesTable.append(field.getCells())

        i = -1
        for field in fields:
            i += 1
            # We generate lines and header for fields values
            line_header.append("v:{0}".format(field.getID()))
            dataValues = self.generateDataValues(valuesTable[i])
            lines.append(dataValues)

            # We generate lines and header for fields size
            line_header.append("s:{0}".format(field.getID()))
            sizeValues = self.generateSizeValues(valuesTable[i])
            lines.append(sizeValues)

        # # Now we generate values for fields sizes
        # (multipleSize_Header, multipleSize_lines) = self.generateSizeFieldFromBeginingOfField(symbol)
        # line_header.extend(multipleSize_Header)
        # for i_line in range(0, len(lines)):
        #     lines[i_line] = lines[i_line] + "," + multipleSize_lines[i_line]

        # # Now we generate values for CRC32
        # (crc32Header, crc32Lines) = self.generateCRC32(symbol)
        # line_header.extend(crc32Header)
        # for i_line in range(0, len(lines)):
        #     line = lines[i_line]
        #     lines[i_line] = line + "," + crc32Lines[i_line]

        return (line_header, lines)

    def generateDataValues(self, cellsData):
        result = []
        for data in cellsData:
            if len(data) > 0:
                result.append(int(data[:16], 16))  # We take only the first 8 octets
            else:
                result.append(0)
        return result

    def generateSizeValues(self, cellsData):
        result = []
        for data in cellsData:
            if len(data) > 0:
                result.append(len(data) / 2)  # Size in octets
            else:
                result.append(0)
        return result

    def generateCRC32(self, symbol):
        header = []
        lines = []
        header.append("crc32:")
        messages = symbol.getMessages()
        for message in messages:
            line = []
            data = message.getStringData()
            rawContent = TypeConvertor.netzobRawToPythonRaw(data)
            valCrc32 = zlib.crc32(rawContent) & 0xFFFFFFFFL
            line.append(str(valCrc32))
            lines.append(",".join(line))
        return (header, lines)

    def generateSizeFieldFromBeginingOfField(self, symbol):
        header = []
        lines = []
        cells = dict()
        fields = symbol.getExtendedFields()
        for field in fields:
            if not field.isStatic():
                header.append("v:{0}[2]".format(field.getID()))
                cells[field] = field.getCells()

        for i_msg in range(0, len(symbol.getMessages())):
            line = []
            for field in cells.keys():
                entry = cells[field][i_msg]
                for k in range(2, 3, 2):
                    if len(entry) > k:
                        line.append(TypeConvertor.netzobRawToDecimal(entry[:k]))
                    else:
                        line.append(TypeConvertor.netzobRawToDecimal(entry))

            lines.append(",".join(line))

        return (header, lines)
