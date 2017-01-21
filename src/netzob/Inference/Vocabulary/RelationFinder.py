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

#+----------------------------------------------
#| Global Imports
#+----------------------------------------------
import uuid
import math

#+----------------------------------------------
#| Local Imports
#+----------------------------------------------
from netzob import _libRelation
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger
from netzob.Model.Types.TypeConverter import TypeConverter
from netzob.Model.Types.AbstractType import AbstractType
from netzob.Model.Types.Raw import Raw
from netzob.Model.Types.Integer import Integer
from netzob.Model.Vocabulary.AbstractField import AbstractField


@NetzobLogger
class RelationFinder(object):
    """Provides multiple algorithms to find relations between messages.

    >>> import binascii
    >>> from netzob.all import *
    >>> samples = [b"0007ff2f000000000000", b"0011ffaaaaaaaaaaaaaabbcc0010000000000000", b"0012ffddddddddddddddddddddfe1f000000000000"]
    >>> messages = [RawMessage(data=binascii.unhexlify(sample)) for sample in samples]
    >>> symbol = Symbol(messages=messages)
    >>> Format.splitStatic(symbol)
    >>> rels = RelationFinder.findOnFields(symbol.fields[1], symbol.fields[3])
    >>> print(len(rels))
    1
    >>> for rel in rels:
    ...     print(rel["relation_type"] + " between " + rel["x_field"].name + ":" + rel["x_attribute"] + \
            " and " + rel["y_field"].name + ":" + rel["y_attribute"])
    SizeRelation between Field-1:value and Field-3:size

    >>> rels = RelationFinder.findOnSymbol(symbol)
    >>> print(len(rels))
    1
    >>> for rel in rels:
    ...     print(rel["relation_type"] + " between fields " + str([x.name for x in rel["x_fields"]]) + ":" + rel["x_attribute"] + \
            " and fields " + str([y.name for y in rel["y_fields"]]) + ":" + rel["y_attribute"])
    SizeRelation between fields ['Field-1']:value and fields ['Field-3']:size

    """

    # Field's attributes
    ATTR_VALUE = "value"
    ATTR_SIZE = "size"
    AVAILABLE_ATTRIBUTES = [ATTR_VALUE, ATTR_SIZE]

    # Relation types
    REL_SIZE = "SizeRelation"
    REL_DATA = "DataRelation"
    REL_EQUALITY = "EqualityRelation"
    REL_UNKNOWN = "Unknown"

    def __init__(self):
        pass

    @staticmethod
    @typeCheck(AbstractField)
    def findOnSymbol(symbol):
        """Find exact relations between fields in the provided
        symbol/field.

        :param symbol: the symbol in which we are looking for relations
        :type symbol: :class:`netzob.Model.Vocabulary.AbstractField.AbstractField`
        """

        rf = RelationFinder()
        return rf.executeOnSymbol(symbol)

    @staticmethod
    @typeCheck(AbstractField, AbstractField, str, str)
    def findOnFields(x_field, y_field, x_attribute=None, y_attribute=None):
        """Find exact relations between the provided fields, according
        to their optional specified attributes.

        """

        rf = RelationFinder()
        return rf.executeOnFields(x_field, y_field, x_attribute, y_attribute)

    # @typeCheck(AbstractField)
    # def executeOnSymbol(self, symbol):
    #     """
    #     :param symbol: the symbol in which we are looking for relations
    #     :type symbol: :class:`netzob.Model.Vocabulary.AbstractField.AbstractField`
    #     """

    #     cells = [field.getValues(encoded=False, styled=False)
    #              for field in symbol.getExtendedFields()
    #              #if not field.isStatic()
    #              ]
    #     if cells:
    #         # Invert array dimensions liks this:
    #         # < [[m0f0, m1f0, ...], [m0f1, m1f1, ...]]
    #         # > [(m0f0, m0f1, ...), (m1f0, m1f1, ...)]
    #         for algo, refs in _libRelation.find(zip(*cells)).items():
    #             for ref_idx, ref_off, ref_size, rels in refs:
    #                 print "Relations(%s) with F%d:" % (algo, ref_idx)
    #                 for rel_id, rel_conf in enumerate(rels):
    #                     print "  %d. F[%d][%d:%d]" % ((rel_id,) + rel_conf)


    # def executeOnCells(self, cellsTable):
    #     if cellsTable:
    #         # Invert array dimensions liks this:
    #         # < [[m0f0, m1f0, ...], [m0f1, m1f1, ...]]
    #         # > [(m0f0, m0f1, ...), (m1f0, m1f1, ...)]
    #         for algo, refs in _libRelation.find(zip(*cellsTable)).items():
    #             for ref_idx, ref_off, ref_size, rels in refs:
    #                 print "Relations(%s) with F%d:" % (algo, ref_idx)
    #                 for rel_id, rel_conf in enumerate(rels):
    #                     print "  %d. F[%d][%d:%d]" % ((rel_id,) + rel_conf)

    @typeCheck(AbstractField)
    def executeOnSymbol(self, symbol):
        """Find exact relations between fields of the provided symbol.
        """

        (attributeValues_headers, attributeValues) = self._generateAttributeValuesForSymbol(symbol)
        results = []

        for i, x_values in enumerate(attributeValues[:-1]):
            for j, y_values in enumerate(attributeValues[:]):
                if j <= i:
                    continue
                isRelation = True
                for k in range(len(x_values)):
                    if not (x_values[k] == y_values[k]):
                        isRelation = False
                        break
                if isRelation:
                    # Do no keep relations where a field's values does not change
                    if len(set(x_values)) == 1 or len(set(y_values)) == 1:
                        continue
                    (x_fields, x_attribute) = attributeValues_headers[i]
                    (y_fields, y_attribute) = attributeValues_headers[j]
                    # The relation should not apply on the same field
                    if len(x_fields) == 1 and len(y_fields) == 1 and x_fields[0].id == y_fields[0].id:
                        continue
                    relation_type = self._findRelationType(x_attribute, y_attribute)
                    # We do not consider unqualified relation (for example, the size of a field is linked to the size of another field)
                    if relation_type == self.REL_UNKNOWN:
                        continue
                    # DataRelation should produce an empty intersection between related fields
                    if relation_type == self.REL_DATA and len(set(x_fields).intersection(set(y_fields))) > 0:
                        continue
                    # SizeRelation should a size field composed of multiple fields
                    if relation_type == self.REL_SIZE:
                        if x_attribute == self.ATTR_VALUE:
                            if len(x_fields) > 1:
                                continue
                        elif y_attribute == self.ATTR_VALUE:
                            if len(y_fields) > 1:
                                continue
                    self._logger.debug("Relation found between '" + str(x_fields) + ":" + x_attribute + "' and '" + str(y_fields) + ":" + y_attribute + "'")
                    id_relation = str(uuid.uuid4())
                    results.append({'id': id_relation,
                                    "relation_type": relation_type,
                                    'x_fields': x_fields,
                                    'x_attribute': x_attribute,
                                    'y_fields': y_fields,
                                    'y_attribute': y_attribute})
        return results

    @typeCheck(AbstractField, AbstractField, str, str)
    def executeOnFields(self, x_field, y_field, x_attribute=None, y_attribute=None):
        """Find exact relations between fields according to their
        optional selected attributes.
        """

        results = []
        # Convert cells according to their interesting attribute (data, size or offset)
        if x_attribute == self.ATTR_SIZE and y_attribute == self.ATTR_SIZE:  # A relation between two size field is uncertain...
            return results
        x_values = x_field.getValues(encoded=False, styled=False)
        y_values = y_field.getValues(encoded=False, styled=False)

        # Select attributes for fields comparison
        if x_attribute is None:
            x_attributes = self.AVAILABLE_ATTRIBUTES
        else:
            x_attributes = [x_attribute]

        if y_attribute is None:
            y_attributes = self.AVAILABLE_ATTRIBUTES
        else:
            y_attributes = [y_attribute]

        # Try to find a relation that matches each cell
        relation_fcts = {}
        relation_fcts[self.REL_SIZE] = self._sizeRelation
        relation_fcts[self.REL_EQUALITY] = self._equalRelation

        for x_attribute in x_attributes:
            for y_attribute in y_attributes:
                for (relation_name, relation_fct) in list(relation_fcts.items()):
                    isRelation = True
                    for i in range(len(x_values)):
                        if not relation_fct(x_values[i], x_attribute, y_values[i], y_attribute):
                            isRelation = False
                            break
                    if isRelation:
                        self._logger.debug("Relation found between '" + x_attribute + ":" + str(x_field.name) + "' and '" + y_attribute + ":" + str(y_field.name) + "'")
                        self._logger.debug("  Relation: " + relation_name)
                        id_relation = str(uuid.uuid4())
                        results.append({'id': id_relation,
                                        "relation_type": relation_name,
                                        'x_field': x_field,
                                        'x_attribute': x_attribute,
                                        'y_field': y_field,
                                        'y_attribute': y_attribute})
        return results

    def _findRelationType(self, x_attribute, y_attribute):
        typeRelation = self.REL_UNKNOWN
        if (x_attribute == self.ATTR_VALUE and y_attribute == self.ATTR_SIZE) or (x_attribute == self.ATTR_SIZE and y_attribute == self.ATTR_VALUE):
            typeRelation = self.REL_SIZE
        elif x_attribute == x_attribute == self.ATTR_VALUE:
            typeRelation = self.REL_DATA
        return typeRelation

    def _equalRelation(self, x, x_attribute, y, y_attribute):
        if x == y:
            return True
        else:
            return False

    def _sizeRelation(self, x, x_attribute, y, y_attribute):
        if x_attribute == self.ATTR_SIZE:
            if len(x) > 0:
                x = len(x)
        else:
            if len(x) > 0:
                x = TypeConverter.convert(x[:8], Raw, Integer)
            else:
                x = 0
        if y_attribute == self.ATTR_SIZE:
            if len(y) > 0:
                y = len(y)
        else:
            if len(y) > 0:
                y = TypeConverter.convert(y[:8], Raw, Integer)
            else:
                y = 0

        if x == y:
            return True
        else:
            return False

    def _generateAttributeValuesForSymbol(self, symbol):
        # First we compute the possible list of payloads
        lines_data = []
        line_header = []

        # Compute the list of values for each field
        (fields, fieldsValues) = self._getAllFieldsValues(symbol)

        # Compute the table of concatenation of values
        for i in range(len(fieldsValues[:])):
            for j in range(i+1, len(fieldsValues)+1):
                # We generate the data
                concatCellsData = self._generateConcatData(fieldsValues[i:j])

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

    def _getAllFieldsValues(self, field):
        # This recursive function returns a tuple containing
        # (array of all fields, array of values of each field)
        if len(field.fields) > 0:
            fields = []
            values = []
            for f in field.fields:
                (retFields, retValues) = self._getAllFieldsValues(f)
                fields.extend(retFields)
                values.extend(retValues)
            return (fields, values)
        else:
            return ([field], [field.getValues(encoded=False, styled=False)])

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
                data = data[:8]  # We take at most 8 bytes
                unitSize = int(AbstractType.UNITSIZE_8) * len(data)
                unitSize = int(pow(2, math.ceil(math.log(unitSize, 2))))  # Round to the nearest upper power of 2
                result.append(Integer.encode(data, endianness=AbstractType.ENDIAN_BIG, unitSize=str(unitSize)))
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

