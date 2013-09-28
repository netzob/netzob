#-*- coding: utf-8 -*-

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

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger
from netzob.Common.Models.Vocabulary.AbstractField import AbstractField
from netzob.Common.Models.Vocabulary.Field import Field
from netzob.Common.Models.Vocabulary.Symbol import Symbol
from netzob.Common.Models.Types.TypeConverter import TypeConverter
from netzob.Common.Models.Types.HexaString import HexaString
from netzob.Common.Models.Types.Raw import Raw
from netzob.Common.Models.Vocabulary.Messages.RawMessage import RawMessage
from netzob.Common.Models.Vocabulary.Domain.DomainFactory import DomainFactory


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
        >>> newSymbols = FormatIdentifier.clusterByKeyField(symbol, f2)
        >>> for sym in newSymbols:
        ...     sym.addEncodingFunction(TypeEncodingFunction(HexaString))
        ...     print sym.name + ":"
        ...     print sym
        symbol_ff2f:
        00 | ff2f | 000000
        00 | ff2f | 000000
        symbol_0020:
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
        if not keyField in field.children:
            raise TypeError("'keyField' is not a child of 'field'")

        newSymbols = []

        # Retrieve cells the main field
        fieldsCells = field.getCells()

        # Retrieve uniq values of the key field
        keyFieldValues = keyField.getValues()
        keyFieldValues = list(set(keyFieldValues))
        if len(keyFieldValues) == 0:
            return newSymbols

        # Construct a dict with splitted messages (data) according to the key field
        newDatas = {}
        for idx_field, fieldChild in enumerate(field.children):  # Loop over children of the main field
            if fieldChild == keyField:  # If the child corresponds to the key field
                for keyFieldValue in keyFieldValues:
                    newDatas[keyFieldValue] = []
                    for idx_msg in range(len(fieldsCells)):
                        if fieldsCells[idx_msg][idx_field] == keyFieldValue:
                            newData = "".join(fieldsCells[idx_msg])
                            newData = RawMessage(TypeConverter.convert(newData, HexaString, Raw))
                            newDatas[keyFieldValue].append(newData)
                break

        # Create new symbols for each splitted group, and propagate the same fields domain for each symbol
        for (keyFieldValue, datas) in newDatas.items():
            newFields = []
            for f in field.children:
                domain = DomainFactory.normalizeDomain(f.domain)
                newField = Field(domain=domain)
                newFields.append(newField)

            s = Symbol(newFields, messages=datas, name="symbol_{0}".format(str(keyFieldValue)))
            newSymbols.append(s)

        return newSymbols
