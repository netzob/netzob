#-*- coding: utf-8 -*-

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
#| File contributors :                                                       |
#|       - Georges Bossert <georges.bossert (a) supelec.fr>                  |
#|       - Frédéric Guihéry <frederic.guihery (a) amossys.fr>                |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Standard library imports
#+---------------------------------------------------------------------------+
from bitarray import bitarray

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger
from netzob.Common.Models.Vocabulary.AbstractField import AbstractField
from netzob.Common.Models.Types.AbstractType import AbstractType
from netzob.Common.Models.Vocabulary.Domain.DomainFactory import DomainFactory
from netzob.Common.Models.Vocabulary.Field import Field
from netzob.Common.Models.Vocabulary.Domain.Variables.Nodes.Alt import Alt
from netzob.Common.Models.Vocabulary.Domain.Variables.Nodes.Agg import Agg
from netzob.Common.Models.Types.TypeConverter import TypeConverter
from netzob.Common.Models.Types.BitArray import BitArray
from netzob.Common.Models.Types.Raw import Raw
from netzob.Common.Models.Types.HexaString import HexaString


@NetzobLogger
class FieldSplitDelimiter(object):

    # Static method
    @staticmethod
    @typeCheck(AbstractField, AbstractType)
    def split(field, delimiter):
        """Split a field (or symbol) with a specific delimiter. The
        delimiter can be passed either as an ASCII, a Raw, an
        HexaString, or any objects that inherit from AbstractType.

        >>> from netzob.all import *
        >>> samples = ["aaaaff000000ff10",	"bbff110010ff00000011",	"ccccccccfffe1f000000ff12"]
        >>> messages = [RawMessage(data=sample) for sample in samples]
        >>> symbol = Symbol(messages=messages[:3])
        >>> Format.splitDelimiter(symbol, ASCII("ff"))
        >>> print symbol
        aaaa     | ff | 000000     | ff | 10      
        bb       | ff | 110010     | ff | 00000011
        cccccccc | ff | fe1f000000 | ff | 12      

        :param field : the field to consider when spliting
        :type: :class:`netzob.Common.Models.Vocabulary.AbstractField.AbstractField`
        :param delimiter : the delimiter used to split messages of the field
        :type: :class:`netzob.Common.Models.Types.AbstractType.AbstractType`
        """

        import logging
        _logger = logging.getLogger("paf")

        
        if delimiter is None:
            raise TypeError("Delimiter cannot be None.")

        if field is None:
            raise TypeError("Field cannot be None.")

        if len(field.messages) < 1:
            raise ValueError("The associated symbol does not contain any message.")

        # Find message substrings after applying delimiter
        splittedMessages = []

        for cell in field.getValues(encoded=False, styled=False):
            splittedMessage = cell.split(delimiter.value.tobytes())
            splittedMessages.append(splittedMessage)

        import itertools
        # Inverse the array, so that columns contains observed values for each field
        splittedMessages = list(itertools.izip_longest(*splittedMessages))
        
        # If the delimiter does not create splitted fields
        if len(splittedMessages) <= 1:
            return

        # Else, we add (2*len(splittedMessages)-1) fields
        newFields = []
        iField = -1
        for i in range(len(splittedMessages)):
            iField += 1
            fieldDomain = []
            isEmptyField = True  # To avoid adding an empty field
            emptyValueFound = False
            for v in splittedMessages[i]:
                _logger.debug(v)
                if v != "" and v is not None:
                    isEmptyField = False
                    fieldDomain.append(Raw(v))
                else:
                    fieldDomain.append(Raw(nbBytes=0))

            if not isEmptyField:
                newField = Field(domain=DomainFactory.normalizeDomain(fieldDomain), name="Field-"+str(iField))
                newField.encodingFunctions = field.encodingFunctions.values()
                newFields.append(newField)
                iField += 1

            fieldName = "Field-sep-" + TypeConverter.convert(delimiter.value, BitArray, HexaString)
            
            newFields.append(Field(domain=delimiter, name=fieldName))
            #newFields[-2].domain=Alt([delimiter, Raw(nbBytes=0)])

        newFields.pop()

        # Reset the field
        from netzob.Inference.Vocabulary.Format import Format
        Format.resetFormat(field)

        # Create a field for each entry
        field.children = newFields
