# -*- coding: utf-8 -*-

# +---------------------------------------------------------------------------+
# |          01001110 01100101 01110100 01111010 01101111 01100010            |
# |                                                                           |
# |               Netzob : Inferring communication protocols                  |
# +---------------------------------------------------------------------------+
# | Copyright (C) 2011-2016 Georges Bossert and Frédéric Guihéry              |
# | This program is free software: you can redistribute it and/or modify      |
# | it under the terms of the GNU General Public License as published by      |
# | the Free Software Foundation, either version 3 of the License, or         |
# | (at your option) any later version.                                       |
# |                                                                           |
# | This program is distributed in the hope that it will be useful,           |
# | but WITHOUT ANY WARRANTY; without even the implied warranty of            |
# | MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the              |
# | GNU General Public License for more details.                              |
# |                                                                           |
# | You should have received a copy of the GNU General Public License         |
# | along with this program. If not, see <http://www.gnu.org/licenses/>.      |
# +---------------------------------------------------------------------------+
# | @url      : http://www.netzob.org                                         |
# | @contact  : contact@netzob.org                                            |
# | @sponsors : Amossys, http://www.amossys.fr                                |
# |             Supélec, http://www.rennes.supelec.fr/ren/rd/cidre/           |
# +---------------------------------------------------------------------------+

# +---------------------------------------------------------------------------+
# | File contributors :                                                       |
# |       - Georges Bossert <georges.bossert (a) supelec.fr>                  |
# |       - Frédéric Guihéry <frederic.guihery (a) amossys.fr>                |
# +---------------------------------------------------------------------------+

# +---------------------------------------------------------------------------+
# | Standard library imports                                                  |
# +---------------------------------------------------------------------------+
import collections

# +---------------------------------------------------------------------------+
# | Related third party imports                                               |
# +---------------------------------------------------------------------------+

# +---------------------------------------------------------------------------+
# | Local application imports                                                 |
# +---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger
from netzob.Model.Vocabulary.AbstractField import AbstractField
from netzob.Model.Vocabulary.Field import Field
from netzob.Model.Vocabulary.Symbol import Symbol
from netzob.Model.Types.TypeConverter import TypeConverter
from netzob.Model.Types.HexaString import HexaString
from netzob.Model.Types.ASCII import ASCII
from netzob.Model.Types.BitArray import BitArray
from netzob.Model.Types.Raw import Raw
from netzob.Common.Utils.DataAlignment.DataAlignment import DataAlignment


@NetzobLogger
class ClusterByKeyField(object):
    """This operation clusters the messages belonging to the
    specified field following their value in the specified key field.
    """

    @typeCheck(AbstractField, AbstractField)
    def cluster(self, field, keyField):
        """Create and return new symbols according to a specific key
        field.

        >>> import binascii
        >>> from netzob.all import *
        >>> samples = [b"00ff2f000000", b"000020000000", b"00ff2f000000"]
        >>> messages = [RawMessage(data=binascii.unhexlify(sample)) for sample in samples]
        >>> f1 = Field(Raw(nbBytes=1))
        >>> f2 = Field(Raw(nbBytes=2))
        >>> f3 = Field(Raw(nbBytes=3))
        >>> symbol = Symbol([f1, f2, f3], messages=messages)
        >>> symbol.addEncodingFunction(TypeEncodingFunction(HexaString))
        >>> newSymbols = Format.clusterByKeyField(symbol, f2)
        >>> for sym in list(newSymbols.values()):
        ...     sym.addEncodingFunction(TypeEncodingFunction(HexaString))
        ...     print(sym.name + ":")
        ...     print(sym)
        Symbol_ff2f:
        Field | Field  | Field   
        ----- | ------ | --------
        '00'  | 'ff2f' | '000000'
        '00'  | 'ff2f' | '000000'
        ----- | ------ | --------
        Symbol_0020:
        Field | Field  | Field   
        ----- | ------ | --------
        '00'  | '0020' | '000000'
        ----- | ------ | --------


        :param field: the field we want to split in new symbols
        :type field: :class:`netzob.Model.Vocabulary.AbstractField.AbstractField`
        :param keyField: the field used as a key during the splitting operation
        :type field: :class:`netzob.Model.Vocabulary.AbstractField.AbstractField`
        :raise Exception if something bad happens
        """

        # Safe checks
        if field is None:
            raise TypeError("'field' should not be None")
        if keyField is None:
            raise TypeError("'keyField' should not be None")
        if keyField not in field.fields:
            raise TypeError("'keyField' is not a child of 'field'")

        newSymbols = collections.OrderedDict()

        keyFieldMessageValues = keyField.getMessageValues(encoded=False, styled=False)
        newSymbolsSplittedMessages = {}

        # we identify what would be the best type of the key field
        keyFieldType = ASCII
        for message, keyFieldValue in list(keyFieldMessageValues.items()):
            # If the value cannot be parsed as ASCII, we convert it to HexaString
            if not ASCII().canParse(TypeConverter.convert(keyFieldValue, Raw, BitArray)):
                keyFieldType = HexaString
                break

            # Even if the value is theoritically parsable as ASCII, some caracters cannot be encoded, so we double check
            tmp_value = TypeConverter.convert(keyFieldValue, Raw, ASCII)
            tmp2_value = TypeConverter.convert(tmp_value, ASCII, Raw)
            if keyFieldValue != tmp2_value:
                # This means we cannot retrieve the original value by encoding and then decoding in ASCII
                keyFieldType = HexaString
                break

        # we create a symbol for each of these uniq values
        for message, keyFieldValue in list(keyFieldMessageValues.items()):
            keyFieldValue = TypeConverter.convert(keyFieldValue, Raw, keyFieldType)
            if keyFieldValue not in list(newSymbols.keys()):
                if type(keyFieldValue) is str:
                    symbolName = "Symbol_{0}".format(keyFieldValue)
                else:
                    symbolName = "Symbol_{0}".format(keyFieldValue.decode("utf-8"))
                newSymbols[keyFieldValue] = Symbol(name=symbolName, messages=[message])
                splittedMessages = DataAlignment.align([message.data], field, encoded=False)
                newSymbolsSplittedMessages[keyFieldValue] = [splittedMessages[0]]
            else:
                newSymbols[keyFieldValue].messages.append(message)
                splittedMessages = DataAlignment.align([message.data], field, encoded=False)
                newSymbolsSplittedMessages[keyFieldValue].append(splittedMessages[0])

        for newSymbolKeyValue, newSymbol in list(newSymbols.items()):
            # we recreate the same fields in this new symbol as the fields that exist in the original symbol
            newSymbol.clearFields()
            for i, f in enumerate(field.fields):
                if f == keyField:
                    newFieldDomain = TypeConverter.convert(newSymbolKeyValue, keyFieldType, Raw)
                else:
                    newFieldDomain = set()
                    for j in range(len(newSymbolsSplittedMessages[newSymbolKeyValue])):
                        newFieldDomain.add(newSymbolsSplittedMessages[newSymbolKeyValue][j][i])
                    newFieldDomain = list(newFieldDomain)
                newF = Field(name=f.name, domain=newFieldDomain)
                newF.parent = newSymbol
                newSymbol.fields.append(newF)

            # we remove endless fields that accepts no values
            cells = newSymbol.getCells(encoded=False, styled=False, transposed=False)
            max_i_cell_with_value = 0
            for line in cells:
                for i_cell, cell in enumerate(line):
                    if cell != '' and max_i_cell_with_value < i_cell:
                        max_i_cell_with_value = i_cell
            newSymbol.clearFields()
            for i, f in enumerate(field.fields[:max_i_cell_with_value + 1]):
                if f == keyField:
                    newFieldDomain = TypeConverter.convert(newSymbolKeyValue, keyFieldType, Raw)
                else:
                    newFieldDomain = set()
                    for j in range(len(newSymbolsSplittedMessages[newSymbolKeyValue])):
                        newFieldDomain.add(newSymbolsSplittedMessages[newSymbolKeyValue][j][i])
                    newFieldDomain = list(newFieldDomain)
                newF = Field(name=f.name, domain=newFieldDomain)
                newF.parent = newSymbol
                newSymbol.fields.append(newF)

        return newSymbols

