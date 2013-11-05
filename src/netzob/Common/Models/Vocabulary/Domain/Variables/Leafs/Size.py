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
from netzob.Common.Models.Vocabulary.Domain.Variables.Leafs.AbstractRelationVariableLeaf import AbstractRelationVariableLeaf
from netzob.Common.Models.Vocabulary.AbstractField import AbstractField
from netzob.Common.Models.Types.ASCII import ASCII
from netzob.Common.Models.Types.AbstractType import AbstractType
from netzob.Common.Models.Types.TypeConverter import TypeConverter
from netzob.Common.Models.Types.BitArray import BitArray
from netzob.Common.Models.Types.Raw import Raw
from netzob.Common.Utils.NetzobRegex import NetzobRegex


@NetzobLogger
class Size(AbstractRelationVariableLeaf):
    """A size relation between one variable and

    >>> from netzob.all import *
    >>> f1 = Field(ASCII(nbChars=(5,10)), name="payload")
    >>> f1.domain.learnable = False
    >>> f2 = Field(Size(f1), name="size")
    >>> f2.domain.learnable = False
    >>> s = Symbol(fields=[f2, f1])
    >>> msgs = [RawMessage(s.generate()) for i in xrange(5)]
    >>> for msg in msgs:
    ...     print msg

    >>> s.messages = msgs
    >>> print s

    """

    def __init__(self, fields, dataType=None, name=None):
        super(Size, self).__init__(Size.__class__.__name__, name)

        if isinstance(fields, AbstractField):
            fields = [fields]
        self.fields = fields
        if dataType is None:
            dataType = ASCII()
        self.dataType = dataType

    def isDefined(self, processingToken):
        """Tells if the variable is defined (i.e. has a value for a leaf, enough leaf have values for a node...)

        :type processingToken: :class:`netzob.Common.Models.Vocabulary.Domain.Variables.VariableProcessingTokens.AbstractVariableProcessingToken.AbstractVariableProcessingToken
        :param processingToken: a token which contains all critical information on this access.
        :rtype: boolean
        :return: True if the variable is defined.
        """
        return True

    def buildRegex(self):
        """This method creates a regex based on the size
        established in the domain."""
        return NetzobRegex.buildRegexForSizedValue(self.dataType.size)

    def getValue(self, processingToken):
        """Return the current value of targeted field.

        """

        # first checks the pointed fields all have a value
        hasValue = True
        for field in self.fields:
            if field.domain.getValue(processingToken) is None:
                hasValue = False

        if not hasValue:
            return self.guessValue()
        else:
            size = 0
            for field in self.fields:
                fieldValue = field.domain.getValue(processingToken)

                if fieldValue is None:
                    break
                else:
                    size += len(fieldValue)

            return TypeConverter.convert(size, self.dataType.__class__, BitArray)

    def guessValue(self):
        self._logger.debug("Guessing the value...")
        return TypeConverter.convert("TEMPORARY VALUE", Raw, BitArray)

    @property
    def dataType(self):
        """The datatype used to encode the result of the computed size.

        :type: :class:`netzob.Common.Models.Types.AbstractType.AbstractType`
        """

        return self.__dataType

    @dataType.setter
    @typeCheck(AbstractType)
    def dataType(self, dataType):
        if dataType is None:
            raise TypeError("Datatype cannot be None")
        self.__dataType = dataType

    @property
    def fields(self):
        """A list of fields from which the size will be computed.

        :type: a list of :class:`netzob.Common.Models.Vocabulary.AbstractField.AbstractField`
        """
        return self.__fields

    @fields.setter
    @typeCheck(list)
    def fields(self, fields):
        if fields is None or len(fields) == 0:
            raise TypeError("At least one field must be specified.")
        for field in fields:
            if not isinstance(field, AbstractField):
                raise TypeError("At least one specified field is not a Field.")
        self.__fields = []
        for f in fields:
            self.__fields.append(f)
            f.domain.boundedVariables.append(self)
