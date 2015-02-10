# -*- coding: utf-8 -*-

# +---------------------------------------------------------------------------+
# |          01001110 01100101 01110100 01111010 01101111 01100010            |
# |                                                                           |
# |               Netzob : Inferring communication protocols                  |
# +---------------------------------------------------------------------------+
# | Copyright (C) 2011-2014 Georges Bossert and Frédéric Guihéry              |
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

# +---------------------------------------------------------------------------+
# | Related third party imports                                               |
# +---------------------------------------------------------------------------+

# +---------------------------------------------------------------------------+
# | Local application imports                                                 |
# +---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger
from netzob.Common.Models.Vocabulary.AbstractField import AbstractField
from netzob.Common.Models.Vocabulary.Field import Field
from netzob.Common.Models.Vocabulary.Symbol import Symbol
from netzob.Common.Models.Types.TypeConverter import TypeConverter
from netzob.Common.Models.Types.HexaString import HexaString
from netzob.Common.Models.Types.Raw import Raw


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
        >>> samples = ["00ff2f000000",	"000020000000",	"00ff2f000000"]
        >>> messages = [RawMessage(data=binascii.unhexlify(sample)) for sample in samples]
        >>> f1 = Field(Raw(nbBytes=1))
        >>> f2 = Field(Raw(nbBytes=2))
        >>> f3 = Field(Raw(nbBytes=3))
        >>> symbol = Symbol([f1, f2, f3], messages=messages)
        >>> symbol.addEncodingFunction(TypeEncodingFunction(HexaString))
        >>> newSymbols = Format.clusterByKeyField(symbol, f2)
        >>> for sym in newSymbols.values():
        ...     sym.addEncodingFunction(TypeEncodingFunction(HexaString))
        ...     print sym.name + ":"
        ...     print sym
        Symbol_ff2f:
        00 | ff2f | 000000
        00 | ff2f | 000000
        Symbol_0020:
        00 | 0020 | 000000

        :param field: the field we want to split in new symbols
        :type field: :class:`netzob.Common.Models.Vocabulary.AbstractField.AbstractField`
        :param keyField: the field used as a key during the splitting operation
        :type field: :class:`netzob.Common.Models.Vocabulary.AbstractField.AbstractField`
        :raise Exception if something bad happens
        """

        # Safe checks
        if field is None:
            raise TypeError("'field' should not be None")
        if keyField is None:
            raise TypeError("'keyField' should not be None")
        if keyField not in field.children:
            raise TypeError("'keyField' is not a child of 'field'")

        newSymbols = {}

        keyFieldMessageValues = keyField.getMessageValues()

        # we create a symbol for each of these uniq values
        for message, keyFieldValue in keyFieldMessageValues.iteritems():
            # keyFieldValue = TypeConverter.convert(keyFieldValueRaw, Raw, HexaString)
            if keyFieldValue not in newSymbols.keys():
                symbolName = "Symbol_{0}".format(TypeConverter.convert(keyFieldValue, Raw, HexaString))
                newSymbols[keyFieldValue] = Symbol(name=symbolName, messages=[message])
            else:
                newSymbols[keyFieldValue].messages.append(message)

        for newSymbolKeyValue, newSymbol in newSymbols.iteritems():
            # we recreate the same fields in this new symbol as the fields that exist in the original symbol
            newSymbol.clearChildren()
            for f in field.children:
                if f == keyField:
                    newFieldDomain = newSymbolKeyValue
                else:
                    newFieldDomain = f.domain
                newF = Field(name=f.name, domain=newFieldDomain)
                newF.parent = newSymbol
                newSymbol.children.append(newF)
            # we remove endless fields that accepts no values
            cells = newSymbol.getCells()
            max_i_cell_with_value = 0
            for line in cells:
                for i_cell, cell in enumerate(line):
                    if cell != '' and max_i_cell_with_value < i_cell:
                        max_i_cell_with_value = i_cell
            newSymbol.clearChildren()
            for f in field.children[:max_i_cell_with_value + 1]:
                if f == keyField:
                    newFieldDomain = newSymbolKeyValue
                else:
                    newFieldDomain = f.domain
                newF = Field(name=f.name, domain=newFieldDomain)
                newF.parent = newSymbol
                newSymbol.children.append(newF)

        return newSymbols

        # # Construct a dict with splitted messages (data) according to the key field
        # newDatas = {}
        # newDomains = {}
        # for idx_field, fieldChild in enumerate(field.children):  # Loop over children of the main field
        #     if fieldChild == keyField:  # If the child corresponds to the key field
        #         for keyFieldValue in keyFieldValues:
        #             newDatas[keyFieldValue] = []  # In order to keep the association between messages and their new symbols
        #             newDomains[keyFieldValue] = []  # In order to keep the association between domains and their new symbols
        #             for idx_msg in range(len(fieldsCells)):
        #                 if fieldsCells[idx_msg][idx_field] == keyFieldValue:
        #                     newData = "".join(fieldsCells[idx_msg])
        #                     newData = RawMessage(newData)
        #                     newDatas[keyFieldValue].append(newData)
        #                     newDomain = fieldsCells[idx_msg]
        #                     newDomains[keyFieldValue].append(newDomain)
        #             newDomains[keyFieldValue] = zip(*newDomains[keyFieldValue])  # Inverse the array to have fields values for the first dimension
        #         break

        # # Create new symbols for each splitted group, and recreate the fields domain for each symbol
        # for (keyFieldValue, datas) in newDatas.items():
        #     newFields = []
        #     for (idx, f) in enumerate(field.children):
        #         domain = DomainFactory.normalizeDomain(list(newDomains[keyFieldValue][idx]))
        #         newField = Field(domain=domain)
        #         _logger.warn(newField._str_debug())
        #         newFields.append(newField)

        #     if not ASCII().canParse(keyFieldValue):
        #         keyFieldValue = TypeConverter.convert(keyFieldValue, Raw, HexaString)
        #     s = Symbol(newFields, messages=datas, name="symbol_{0}".format(keyFieldValue))
        #     newSymbols["symbol_{0}".format(keyFieldValue)] = s

        # return newSymbols
