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
import random
#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+
from bitarray import bitarray

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger
from netzob.Common.Models.Vocabulary.Domain.Variables.Leafs.AbstractRelationVariableLeaf import AbstractRelationVariableLeaf
from netzob.Common.Models.Vocabulary.AbstractField import AbstractField
from netzob.Common.Models.Types.HexaString import HexaString
from netzob.Common.Models.Types.AbstractType import AbstractType
from netzob.Common.Models.Types.TypeConverter import TypeConverter
from netzob.Common.Models.Types.BitArray import BitArray
from netzob.Common.Models.Types.Raw import Raw
from netzob.Common.Models.Types.Decimal import Decimal


@NetzobLogger
class InternetChecksum(AbstractRelationVariableLeaf):
    """An internet checksum relaton as specified in RFC 1071 (https://www.ietf.org/rfc/rfc1071.txt).
    This checksum is used by ICMP, UDP, IP, TCP protocols.


    The following example, illustrates the creation of an ICMP Echo request packet
    with a valid checksum computed on-the-fly.
    
    >>> from netzob.all import *
    >>> typeField = Field(name="Type", domain=Raw('\\x08'))
    >>> codeField = Field(name="Code", domain=Raw('\\x00'))
    >>> chksumField = Field(name="Checksum")
    >>> identField = Field(name="Identifier", domain=Raw('\\x1d\\x22'))
    >>> seqField = Field(name="Sequence Number", domain=Raw('\\x00\\x07'))
    >>> timeField = Field(name="Timestamp", domain=Raw('\\xa8\\xf3\\xf6\\x53\\x00\\x00\\x00\\x00'))
    >>> headerField = Field(name="header")
    >>> headerField.children = [typeField, codeField, chksumField, identField, seqField, timeField]
    >>> dataField = Field(name="Payload", domain=Raw('\\x60\\xb5\\x06\\x00\\x00\\x00\\x00\\x00\\x10\\x11\\x12\\x13\\x14\\x15\\x16\\x17\\x18\\x19\\x1a\\x1b\\x1c\\x1d\\x1e\\x1f\\x20\\x21\\x22\\x23\\x24\\x25\\x26\\x27\\x28\\x29\\x2a\\x2b\\x2c\\x2d\\x2e\\x2f\\x30\\x31\\x32\\x33\\x34\\x35\\x36\\x37'))

    >>> chksumField.domain = InternetChecksum([headerField, dataField], dataType=Raw(nbBytes=2))
    >>> s = Symbol(fields = [headerField, dataField])
    >>> msgs = [RawMessage(s.specialize()) for i in xrange(1)]
    >>> s.messages = msgs
    >>> s.addEncodingFunction(TypeEncodingFunction(HexaString))
    >>> print s
    08 | 00 | 1607 | 1d22 | 0007 | a8f3f65300000000 | 60b5060000000000101112131415161718191a1b1c1d1e1f202122232425262728292a2b2c2d2e2f3031323334353637

    Now, lets generate multiple ICMP packets with a random payload.

    # >>> dataField.domain = Raw(nbBytes=(0, 60))
    # >>> msgs = [RawMessage(s.specialize()) for i in xrange(10)]
    # >>> s.messages = msgs
    # >>> s.addEncodingFunction(TypeEncodingFunction(HexaString))
    # >>> print len(s.getCells())
    # 10

    

    """

    def __init__(self, fields, dataType=None, name=None):
        if isinstance(fields, AbstractField):
            fields = [fields]
        super(InternetChecksum, self).__init__("InternetChecksum", fieldDependencies=fields, name=name)
        if dataType is None:
            dataType = Raw(nbBytes=1)
        self.dataType = dataType
        raise Exception("Not implemented")

    def compareFormat(self, readingToken):
        raise Exception('Not Implemented')

        
    def getValue(self, processingToken):
        """Return the current value of targeted field.
        """
        raise Exception("Not Implemented")

        self._logger.debug("Get the value of {0}".format(self))
        
        # first checks the pointed fields all have a value
        hasValue = True
        for field in self.fieldDependencies:
            self._logger.fatal(field.name)
            if field.domain != self and not processingToken.isValueForVariableAvailable(field.domain):
                hasValue = False

        if not hasValue:
            raise Exception("Impossible to compute the value (getValue) of the current Size field since some of its dependencies have no value")

        fieldValues = []
        for field in self.fieldDependencies:
            self._logger.fatal("Domain of {0} = {1}".format(field.name, field.domain))
            fieldValue = TypeConverter.convert(processingToken.getValueForVariable(field.domain), BitArray, Raw)
            
            if fieldValue == "TEMPORARY" and field.domain.name == self.name:
                self._logger.fatal("Temporary found")
                # Internet checksum specifies that un undefined field must filled with 0's
                # we retrieve its size
                fieldSize = random.randint(field.domain.dataType.size[0], field.domain.dataType.size[1])
                # and set it full of zeros
                fieldValue = "\x00"* (fieldSize / 8)
                # return TypeConverter.convert(fieldValue, Raw, BitArray)

            # if len(fieldValue)%2 == 1:
            #     fieldValue = "\x00"+fieldValue
            self._logger.fatal("Fname = {0}, Values = {1}".format(field.name, repr(fieldValue)))
            fieldValues.append(fieldValue)

        fieldValues = ''.join(fieldValues)
        # compute the checksum of this value
        chsum = self.__checksum(fieldValues)
        b = TypeConverter.convert(chsum, Decimal, BitArray, src_unitSize=AbstractType.UNITSIZE_16, src_sign = AbstractType.SIGN_UNSIGNED)

        return b
        
    def __checksum(self, msg):
        self._logger.fatal("Computing checksum of {0}, {1}".format(TypeConverter.convert(msg, Raw, HexaString), len(msg)))
    
        def carry_around_add(a, b):
            c = a + b
            return (c & 0xffff) + (c >> 16)

        s = 0
        for i in range(0, len(msg), 2):
            if i + 1 >= len(msg):
                w = ord(msg[i]) & 0xFF
            else:        
                w = ord(msg[i]) + (ord(msg[i+1]) << 8)
            s = carry_around_add(s, w)
        res = ~s & 0xffff
        return res
        
    def __str__(self):
        """The str method."""
        return "InternetChecksum({0}) - Type:{1} (L={2}, M={3})".format(str([f.name for f in self.fieldDependencies]), self.dataType, self.learnable, self.mutable)

    @property
    def dataType(self):
        """The datatype used to encode the result of the computed Internet Checksum.

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
            raise ValueError("The datatype of a checksum field must declare its length")
        self.__dataType = dataType

