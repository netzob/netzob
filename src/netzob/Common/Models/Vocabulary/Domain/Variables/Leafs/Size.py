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
#| Standard library imports                                                  |
#+---------------------------------------------------------------------------+
import math

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
from netzob.Common.Models.Types.Decimal import Decimal
from netzob.Common.Utils.NetzobRegex import NetzobRegex
from netzob.Common.Models.Vocabulary.Domain.Variables.VariableProcessingTokens.VariableReadingToken import VariableReadingToken


@NetzobLogger
class Size(AbstractRelationVariableLeaf):
    """A size relation between one variable and a the value of a field

    In the following example, a size field is declared after its field.

    >>> from netzob.all import *


    # >>> import random
    # >>> f1 = Field(ASCII(nbChars=(5,10)))
    # >>> f2 = Field(";")
    # >>> f3 = Field(Size(f1))
    # >>> s = Symbol(fields=[f1, f2, f3])
    # >>> msgs = [RawMessage(s.specialize()) for i in xrange(10)]
    # >>> s.messages = msgs
    # >>> values = random.choice(s.getCells())
    # >>> len(values[0])*4 == int(TypeConverter.convert(values[2], HexaString, Raw))
    # True

    While next demo, illustrates a size field declared before its target field

    >>> f2 = Field(ASCII(nbChars=(5, 10)), name="payload")
    >>> f1 = Field(Size(f2, dataType=ASCII(nbChars=1), factor=1/8.0, offset=1), name="size")
    >>> s = Symbol([f1, f2])
    >>> m = TypeConverter.convert(s.specialize(), Raw, HexaString)
    >>> computed_size = int(m[0:2], 16)
    >>> print computed_size == len(m) / 2
    True

    """

    def __init__(self, fields, dataType=None, factor=1.0, offset=0, name=None):
        if isinstance(fields, AbstractField):
            fields = [fields]
        super(Size, self).__init__("Size", fieldDependencies=fields, name=name)
        self.fields = fields
        if dataType is None:
            dataType = Raw(nbBytes=1)
        self.dataType = dataType
        self.factor = factor
        self.offset = offset

    def buildRegex(self):
        """This method creates a regex based on the size
        established in the domain."""
        return NetzobRegex.buildRegexForSizedValue(self.dataType.size)

    @typeCheck(VariableReadingToken)
    def compareFormat(self, readingToken):
        if readingToken is None:
            raise TypeError("readingToken cannot be None")
        self._logger.debug("- [ {0}: compareFormat".format(self))

        # Retrieve the value to check
        if not readingToken.isValueForVariableAvailable(self):
            raise Exception("Cannot compareFormat because not value is linked with the current data")

        data = readingToken.getValueForVariable(self)

        if len(data) < self.dataType.size[0]:
            readingToken.Ok = False

        minSize, maxSize = self.dataType.size
        if minSize != maxSize:
            raise Exception("Impossible to abstract messages if a size field has a dynamic size")

        value = data[:maxSize]
        if not self.isDefined(readingToken):
            for field in self.fieldDependencies:
                if not readingToken.isValueForVariableAvailable(field.domain):
                    readingToken.addRelationCallback(field.domain, self, self.compareFormat)
        else:
            if value == self.getValue(readingToken):
                self._logger.debug("Parsed value respects size constraints.")
                readingToken.Ok = True
            else:
                self._logger.debug("Parsed value doesn't respect size constraints")
                readingToken.Ok = False

        if readingToken.Ok:
            readingToken.setValueForVariable(self, data[:maxSize])
        else:
            readingToken.removeValueForVariable(self)

    def getValue(self, processingToken):
        """Return the current value of targeted field.
        """
        # first checks the pointed fields all have a value
        hasValue = True
        for field in self.fields:
            if field.domain != self and not processingToken.isValueForVariableAvailable(field.domain):
                hasValue = False

        if not hasValue:
            raise Exception("Impossible to compute the value (getValue) of the current Size field since some of its dependencies have no value")
        else:
            size = 0
            for field in self.fields:
                if field.domain is self:
                    fieldValue = self.dataType.generate()
                else:
                    fieldValue = processingToken.getValueForVariable(field.domain)
                if fieldValue is None:
                    break
                else:
                    tmpLen = len(fieldValue)
                    tmpLen = int(math.ceil(tmpLen / 8.0) * 8)  # Round to the upper closest multiple of 8 (the size of a byte),
                                                               # because this is what will be considered durring field specialization
                    size += tmpLen
            size = size * self.factor + self.offset

            return TypeConverter.convert(size, Decimal, BitArray)

    def __str__(self):
        """The str method."""
        return "Size({0}) - Type:{1} (L={2}, M={3})".format(str([f.name for f in self.fields]), self.dataType, self.learnable, self.mutable)

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
        (minSize, maxSize) = dataType.size
        if maxSize is None:
            raise ValueError("The datatype of a size field must declare its length")
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

    @property
    def factor(self):
        """Defines the multiplication factor to apply on the targeted length (in bits)"""
        return self.__factor

    @factor.setter
    @typeCheck(float)
    def factor(self, factor):
        if factor is None:
            raise TypeError("Factor cannot be None, use 1.0 for the identity.")
        self.__factor = factor

    @property
    def offset(self):
        """Defines the offset to apply on the computed length
        computed size = (factor*size(targetField)+offset)"""
        return self.__offset

    @offset.setter
    @typeCheck(int)
    def offset(self, offset):
        if offset is None:
            raise TypeError("Offset cannot be None, use 0 if no offset should be applied.")
        self.__offset = offset
