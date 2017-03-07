# -*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|          01001110 01100101 01110100 01111010 01101111 01100010            |
#|                                                                           |
#|               Netzob : Inferring communication protocols                  |
#+---------------------------------------------------------------------------+
#| Copyright (C) 2011-2016 Georges Bossert and Frédéric Guihéry              |
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
import errno
import time
import uuid
import zlib
from gettext import gettext as _

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+
try:
    import numpy
    from minepy import MINE
except:
    pass

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger
from netzob.Model.Vocabulary.AbstractField import AbstractField
from netzob.Model.Types.TypeConverter import TypeConverter
from netzob.Model.Types.Raw import Raw
from netzob.Model.Types.Integer import Integer
from netzob.Inference.Vocabulary.RelationFinder import RelationFinder


@NetzobLogger
class CorrelationFinder(object):
    """Correlation identification based on MINE (Maximal
    Information-based Nonparametric Exploration) statistics.

    >>> import binascii
    >>> from netzob.all import *
    >>> samples = [b"0007ff2f000000000000", b"0011ffaaaaaaaaaaaaaabbcc0010000000000000", b"0012ffddddddddddddddddddddfe1f000000000000"]
    >>> messages = [RawMessage(data=binascii.unhexlify(sample)) for sample in samples]
    >>> symbol = Symbol(messages=messages)
    >>> Format.splitStatic(symbol)
    >>> rels = CorrelationFinder.find(symbol)
    >>> print(len(rels))
    64
    """

    # Field's attributes
    ATTR_VALUE = "value"
    ATTR_SIZE = "size"
    ATTR_CRC32 = "crc32"

    # Relation types
    REL_SIZE = "SizeRelation"
    REL_DATA = "DataRelation"

    @staticmethod
    @typeCheck(AbstractField, float)
    def find(symbol, minMic=0.7):
        """Find correlations between fields in the provided symbol,
        according to a minimum threshold. The underlying work is as
        follow: we compute the combination of each field's attribute
        (value, size, etc.), execute MINE correlation finder on it and
        parse the results.

        :param symbol: the symbol in which we are looking for correlations
        :type symbol: :class:`netzob.Model.Vocabulary.AbstractField.AbstractField`
        :param minMic: the minimum correlation score 
        :type minMic: :class:`float`
        """

        try:
            import numpy
        except:
            # Fall back to classical relations
            import logging
            logging.warn("'numpy' and 'minepy' packages needed for CorrelationFinder. Fall back to RelationFinder instead.")
            return RelationFinder.findOnSymbol(symbol)

        cf = CorrelationFinder(minMic)
        return cf.execute(symbol)

    def __init__(self, minMic=0.7):
        self.minMic = minMic

    @typeCheck(AbstractField)
    def execute(self, symbol):
        """
        :param symbol: the symbol in which we are looking for correlations
        :type symbol: :class:`netzob.Model.Vocabulary.AbstractField.AbstractField`
        """

        (attributeValues_headers, attributeValues) = self._generateAttributeValuesForSymbol(symbol)
        symbolResults = []

        # MINE computation of each field's combination
        for i, values_x in enumerate(attributeValues[:-1]):
            for j, values_y in enumerate(attributeValues[i+1:]):
                mine = MINE(alpha=0.6, c=15)
                mine.compute_score(numpy.array(values_x), numpy.array(values_y))
                mic = round(mine.mic(), 2)
                if mic > float(self.minMic):
                    # We add the relation to the results
                    (x_fields, x_attribute) = attributeValues_headers[i]
                    (y_fields, y_attribute) = attributeValues_headers[j]
                    # The relation should not apply on the same field
                    if len(x_fields) == 1 and len(y_fields) == 1 and x_fields[0].id == y_fields[0].id:
                        continue
                    pearson = numpy.corrcoef(values_x, values_y)[0, 1]
                    if not numpy.isnan(pearson):
                        pearson = round(pearson, 2)
                    relation_type = self._findRelationType(x_attribute, y_attribute)
                    self._debug_mine_stats(mine)
                    self._logger.debug("Correlation found between '" + str(x_fields) + ":" + x_attribute + "' and '" + str(y_fields) + ":" + y_attribute + "'")
                    self._logger.debug("  MIC score: " + str(mic))
                    self._logger.debug("  Pearson score: " + str(pearson))
                    id_relation = str(uuid.uuid4())
                    symbolResults.append({'id': id_relation,
                                          "relation_type": relation_type,
                                          'x_fields': x_fields,
                                          'x_attribute': x_attribute,
                                          'y_fields': y_fields,
                                          'y_attribute': y_attribute,
                                          'mic': mic,
                                          'pearson': pearson})
        return symbolResults

    def _debug_mine_stats(self, mine):
        self._logger.debug("MIC: " + str(mine.mic()))
        self._logger.debug("MAS: " + str(mine.mas()))
        self._logger.debug("MEV: " + str(mine.mev()))
        self._logger.debug("MCN (eps=0): " + str(mine.mcn(0)))
        self._logger.debug("MCN (eps=1-MIC): " + str(mine.mcn_general()))

    def _findRelationType(self, x_attribute, y_attribute):
        typeRelation = "Unknown"
        if (x_attribute == self.ATTR_VALUE and y_attribute == self.ATTR_SIZE) or (x_attribute == self.ATTR_SIZE and y_attribute == self.ATTR_VALUE):
            typeRelation = self.REL_SIZE
        elif (x_attribute == x_attribute) and x_attribute == self.ATTR_VALUE:
            typeRelation = self.REL_DATA
        return typeRelation

    def _generateAttributeValuesForSymbol(self, symbol):
        # First we compute the possible list of payloads
        lines_data = []
        line_header = []

        # Compute the table of values
        valuesTable = []
        fields = symbol.fields
        for field in fields:
            valuesTable.append(field.getValues(encoded=False, styled=False))

        # Compute the table of concatenation of values
        for i in range(len(fields[:])):
            for j in range(i+1, len(fields)+1):
                # We generate the data
                concatCellsData = self._generateConcatData(valuesTable[i:j])

                # We generate lines and header for fields values
                line_header.append((fields[i:j], self.ATTR_VALUE))
                lines_data.append(self._generateDataValues(concatCellsData))

                # We generate lines and header for fields values
                line_header.append((fields[i:j], self.ATTR_SIZE))
                lines_data.append(self._generateSizeValues(concatCellsData))

        # # # Now we generate values for fields sizes
        # # (multipleSize_Header, multipleSize_lines) = self._generateSizeFieldFromBeginingOfField(symbol)
        # # line_header.extend(multipleSize_Header)
        # # for i_line in range(0, len(lines)):
        # #     lines[i_line] = lines[i_line] + "," + multipleSize_lines[i_line]

        # # # Now we generate values for CRC32
        # # (crc32Header, crc32Lines) = self._generateCRC32(symbol)
        # # line_header.extend(crc32Header)
        # # for i_line in range(0, len(lines)):
        # #     line = lines[i_line]
        # #     lines[i_line] = line + "," + crc32Lines[i_line]

        return (line_header, lines_data)

    def _generateConcatData(self, cellsDataList):
        """Generates the concatenation of each cell of each field.
        Example:
          cellsData_1 = ["a", "aa", "aaa"]
          cellsData_2 = ["b", "bb", "bbb"]
          res = ["ab", "aabb", "aaabbb"]
        """

        if len(cellsDataList) < 1:
            return []
        result = [b"" for cell in cellsDataList[0]]
        for cellsData in cellsDataList:
            for i, data in enumerate(cellsData):
                result[i] += data
        return result

    def _generateDataValues(self, cellsData):
        result = []
        for data in cellsData:
            if len(data) > 0:
                result.append(TypeConverter.convert(data[:8], Raw, Integer))  # We take only the first 8 octets
            else:
                result.append(0)
        return result

    def _generateSizeValues(self, cellsData):
        result = []
        for data in cellsData:
            if len(data) > 0:
                result.append(len(data))  # Size in octets
            else:
                result.append(0)
        return result

    def _generateCRC32(self, symbol):
        header = []
        lines = []
        header.append(self.ATTR_CRC32)
        messages = symbol.getMessages()
        for message in messages:
            line = []
            data = message.getStringData()
            rawContent = TypeConverter.netzobRawToPythonRaw(data)
            valCrc32 = zlib.crc32(rawContent) & 0xFFFFFFFF
            line.append(str(valCrc32))
            lines.append(b",".join(line))
        return (header, lines)

    def _generateSizeFieldFromBeginingOfField(self, symbol):
        header = []
        lines = []
        cells = dict()
        fields = symbol.fields
        for field in fields:
            if not field.isStatic():
                header.append((self.ATTR_VALUE, field))
                cells[field] = field.getCells(encoded=False, styled=False)

        for i_msg in range(0, len(symbol.getMessages())):
            line = []
            for field in list(cells.keys()):
                entry = cells[field][i_msg]
                for k in range(2, 3, 2):
                    if len(entry) > k:
                        line.append(TypeConverter.netzobRawToInteger(entry[:k]))
                    else:
                        line.append(TypeConverter.netzobRawToInteger(entry))

            lines.append(b",".join(line))

        return (header, lines)

