#-*- coding: utf-8 -*-

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
from bitarray import bitarray

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger
from netzob.Model.Vocabulary.Domain.Variables.Leafs.AbstractRelationVariableLeaf import AbstractRelationVariableLeaf
from netzob.Model.Vocabulary.AbstractField import AbstractField
from netzob.Model.Types.ASCII import ASCII
from netzob.Model.Types.AbstractType import AbstractType
from netzob.Model.Types.TypeConverter import TypeConverter
from netzob.Model.Types.BitArray import BitArray
from netzob.Model.Types.Raw import Raw
from netzob.Model.Types.Integer import Integer
from netzob.Model.Vocabulary.Domain.GenericPath import GenericPath
from netzob.Model.Vocabulary.Domain.Specializer.SpecializingPath import SpecializingPath
from netzob.Model.Vocabulary.Domain.Parser.ParsingPath import ParsingPath


@NetzobLogger
class Size(AbstractRelationVariableLeaf):
    """A size relation between one variable and a the value of a field

    In the following example, a size field is declared after its field.

    >>> from netzob.all import *

    >>> f0 = Field(ASCII(nbChars=(1,10)))
    >>> f1 = Field(ASCII(";"))
    >>> f2 = Field(Size(f0))
    >>> s  = Symbol(fields=[f0, f1, f2])
    >>> msg1  = RawMessage(b"netzob;\\x06")
    >>> mp = MessageParser()
    >>> print(mp.parseMessage(msg1, s))
    [bitarray('011011100110010101110100011110100110111101100010'), bitarray('00111011'), bitarray('00000110')]
    >>> msg2  = RawMessage(b"netzob;\\x03")
    >>> mp = MessageParser()
    >>> print(mp.parseMessage(msg2, s))
    Traceback (most recent call last):
      ...
    netzob.Model.Vocabulary.Domain.Parser.MessageParser.InvalidParsingPathException: No parsing path returned while parsing 'b'netzob;\\x03''

    
    # While next demo, illustrates a size field declared before its target field

    >>> f2 = Field(ASCII(nbChars=(1,10)), name="f2")
    >>> f1 = Field(ASCII(";"), name="f1", )
    >>> f0 = Field(Size(f2), name="f0")
    >>> s  = Symbol(fields=[f0, f1, f2])
    >>> msg1  = RawMessage(b"\\x06;netzob")
    >>> mp = MessageParser()

    >>> print(mp.parseMessage(msg1, s))
    [bitarray('00000110'), bitarray('00111011'), bitarray('011011100110010101110100011110100110111101100010')]

    >>> msg2  = RawMessage(b"\\x03;netzob")
    >>> mp = MessageParser()
    >>> print(mp.parseMessage(msg2, s))
    Traceback (most recent call last):
      ...
    netzob.Model.Vocabulary.Domain.Parser.MessageParser.InvalidParsingPathException: No parsing path returned while parsing 'b'\\x03;netzob''

    # Let's see what happen with specialization of a Size field
    
    >>> f0 = Field(ASCII(nbChars=20))
    >>> f1 = Field(ASCII(";"))
    >>> f2 = Field(Size(f0))
    >>> s  = Symbol(fields=[f0, f1, f2])
    >>> ms = MessageSpecializer()
    >>> res= TypeConverter.convert(ms.specializeSymbol(s).generatedContent, BitArray, Raw)
    >>> b'\\x14' in res
    True

    Another set of examples (and tests)

    >>> f0 = Field(ASCII("CMDauthentify"), name="f0")
    >>> f1 = Field(ASCII('#'), name="sep")
    >>> f2 = Field(name="f2")
    >>> f3 = Field(name="size field")
    >>> f4 = Field(Raw(b"\\x00\\x00\\x00\\x00"), name="f4")
    >>> f5 = Field(Raw(nbBytes=11))
    >>> f6 = Field(Raw(b'wd'), name="f6")
    >>> f7 = Field(Raw(nbBytes=(0, 1)))
    >>> f3.domain = Size([f4, f5, f6])
    >>> f2.fields = [f3, f4, f5, f6, f7]
    >>> s = Symbol(fields=[f0, f1, f2])
    >>> ms = MessageSpecializer()
    >>> b"CMDauthentify#\\x11" in TypeConverter.convert(ms.specializeSymbol(s).generatedContent, BitArray, Raw)
    True

    A more real world example with an IP header with two Size fields

    >>> ip_ver = Field(name='Version', domain=BitArray(value=bitarray('0100')))
    >>> ip_ihl = Field(name='Header length', domain=BitArray(bitarray('0000')))
    >>> ip_tos = Field(name='TOS', domain=Data(dataType=BitArray(nbBits=8), originalValue=bitarray('00000000'), svas=SVAS.PERSISTENT))
    >>> ip_tot_len = Field(name='Total length', domain=BitArray(bitarray('0000000000000000')))
    >>> ip_id = Field(name='Identification number', domain=BitArray(nbBits=16))
    >>> ip_flags = Field(name='Flags', domain=Data(dataType=BitArray(nbBits=3), originalValue=bitarray('000'), svas=SVAS.PERSISTENT))
    >>> ip_frag_off = Field(name='Fragment offset', domain=Data(dataType=BitArray(nbBits=13), originalValue=bitarray('0000000000000'), svas=SVAS.PERSISTENT))
    >>> ip_ttl = Field(name='TTL', domain=Data(dataType=BitArray(nbBits=8), originalValue=bitarray('10000000'), svas=SVAS.PERSISTENT))
    >>> ip_proto = Field(name='Protocol', domain=Integer(value=6, unitSize=AbstractType.UNITSIZE_8, endianness=AbstractType.ENDIAN_BIG, sign=AbstractType.SIGN_UNSIGNED))
    >>> ip_checksum = Field(name='Checksum', domain=BitArray(bitarray('0000000000000000')))
    >>> ip_saddr = Field(name='Source address', domain=IPv4("127.0.0.1"))
    >>> ip_daddr = Field(name='Destination address', domain=IPv4("127.0.0.1"))
    >>> ip_payload = Field(name='Payload', domain=BitArray(bitarray('0000000000000000')))

    >>> ip_ihl.domain = Size([ip_ver, ip_ihl, ip_tos, ip_tot_len, ip_id, ip_flags, ip_frag_off, ip_ttl, ip_proto, ip_checksum, ip_saddr, ip_daddr], dataType=BitArray(nbBits=4), factor=1/float(32))
    >>> ip_tot_len.domain = Size([ip_ver, ip_ihl, ip_tos, ip_tot_len, ip_id, ip_flags, ip_frag_off, ip_ttl, ip_proto, ip_checksum, ip_saddr, ip_daddr, ip_payload], dataType=Raw(nbBytes=2), factor=1/float(8))
        
    >>> packet = Symbol(name='IP layer', fields=[ip_ver, ip_ihl, ip_tos, ip_tot_len, ip_id, ip_flags, ip_frag_off, ip_ttl, ip_proto, ip_checksum, ip_saddr, ip_daddr, ip_payload])
    >>> data = packet.specialize()
    >>> repr(hex(data[0]))  # This corresponds to the first octect of the IP layer. '5' means 5*32 bits, which is the size of the default IP header.
    "'0x45'"

    >>> repr(hex(data[3]))  # This corresponds to the third octect of the IP layer. '0x16' means 22 octets, which is the size of the default IP header + 2 octets of payload.
    "'0x16'"


    """

    def __init__(self, fields, dataType=None, factor=1/float(8), offset=0, name=None):
        if isinstance(fields, AbstractField):
            fields = [fields]
        super(Size, self).__init__("Size", fieldDependencies=fields, name=name)
        self.fields = fields
        if dataType is None:
            dataType = Raw(nbBytes=1)
        self.dataType = dataType
        self.factor = factor
        self.offset = offset

    def __key(self):
        return (self.dataType, self.factor, self.offset)

    def __eq__(x, y):
        try:
            return x.__key() == y.__key()
        except:
            return False

    def __hash__(self):
        return hash(self.__key())

    @typeCheck(GenericPath)
    def isDefined(self, parsingPath):        
        # we retrieve the memory of the current path
        memory = parsingPath.memory
        return memory.hasValue(self)

    @typeCheck(ParsingPath)
    def valueCMP(self, parsingPath, carnivorous=False):
        results = []
        if parsingPath is None:
            raise Exception("ParsingPath cannot be None")

        sizeOfPossibleValue = self.dataType.size()
        if sizeOfPossibleValue[0] != sizeOfPossibleValue[1]:
            raise Exception("Impossible to abstract messages if a size field has a dynamic size")

        content = parsingPath.getDataAssignedToVariable(self)
        possibleValue = content[:sizeOfPossibleValue[1]]
        self._logger.warn("Possible value of size field: {0}".format(possibleValue))
        
        expectedValue = self._computeExpectedValue(parsingPath)
        if expectedValue is None:
            # the expected value cannot be computed
            # we add a callback
            self._addCallBacksOnUndefinedFields(parsingPath)
        else:
            if possibleValue[:len(expectedValue)] == expectedValue:
                parsingPath.addResult(self, expectedValue.copy())
            results.append(parsingPath)                

    @typeCheck(ParsingPath)
    def learn(self, parsingPath, carnivours=False):
        raise Exception("not implemented")
        self._logger.warn("SIZE LEARN")
        if parsingPath is None:
            raise Exception("VariableParserPath cannot be None")
        return []

    @typeCheck(ParsingPath)
    def domainCMP(self, parsingPath, acceptCallBack=True, carnivorous=False):
        """This method participates in the abstraction process.

        It creates a VariableSpecializerResult in the provided path if
        the remainingData (or some if it) follows the type definition"""


        results = []
        self._logger.debug("domainCMP executed on {0} by a size domain".format(parsingPath))

        minSize, maxSize = self.dataType.size
        if minSize != maxSize:
            raise Exception("Impossible to abstract messages if a size field has a dynamic size")

        content = parsingPath.getDataAssignedToVariable(self)
        possibleValue = content[:maxSize]
        
        expectedValue = None
        try:
            expectedValue = self._computeExpectedValue(parsingPath)
        
            if possibleValue[:len(expectedValue)] == expectedValue:
                parsingPath.addResult(self, expectedValue.copy())
                results.append(parsingPath)
            else:
                self._logger.debug("Executed callback has failed.")
        except Exception as e:
            # the expected value cannot be computed
            if acceptCallBack:
                # we add a callback
                self._addCallBacksOnUndefinedFields(parsingPath)
                # register the remaining data
                parsingPath.addResult(self, possibleValue.copy())
                results.append(parsingPath)
            else:
                raise Exception("no more callback accepted.")

        return results

    @typeCheck(GenericPath)
    def _addCallBacksOnUndefinedFields(self, parsingPath):
        """Identify each dependency field that is not yet defined and register a
        callback to try to recompute the value """

        parsingPath.registerFieldCallBack(self.fieldDependencies, self)
        # for field in self.fieldDependencies:
        #     if field.domain != self and not parsingPath.isDataAvailableForField(field):
                

    @typeCheck(GenericPath)
    def _computeExpectedValue(self, parsingPath):
        self._logger.debug("compute expected value for Size field")

        # first checks the pointed fields all have a value
        hasValue = True
        for field in self.fieldDependencies:
            if field.domain != self and not parsingPath.isDataAvailableForVariable(field.domain):
                self._logger.debug("Field : {0} has no value".format(field.id))
                hasValue = False

        if not hasValue:
            raise Exception("Expected value cannot be computed, some dependencies are missing for domain {0}".format(self))
        else:
            size = 0
            for field in self.fieldDependencies:

                # Retrieve field value
                if field.domain is self:
                    fieldValue = self.dataType.generate()
                else:
                    fieldValue = parsingPath.getDataAssignedToVariable(field.domain)
                if fieldValue is None:
                    break

                # Retrieve length of field value
                if fieldValue == TypeConverter.convert("PENDING VALUE", ASCII, BitArray):
                    # Handle case where field value is not currently known.
                    # In such case, we retrieve the max length of the datatype
                    minSize, maxSize = field.domain.dataType.size
                    if maxSize is None:
                        maxSize = AbstractType.MAXIMUM_GENERATED_DATA_SIZE
                    tmpLen = maxSize
                else:
                    tmpLen = len(fieldValue)
                size += tmpLen


            size = int(size * self.factor + self.offset)
            size_raw = TypeConverter.convert(size, Integer, Raw, src_unitSize=self.dataType.unitSize)
            b = TypeConverter.convert(size_raw, Raw, BitArray)
            
            # add heading '0'
            while len(b)<self.dataType.size[0]:
                b.insert(0, False)

            # in some cases (when unitSize and size are not equal), it may require to delete some '0' in front
            while len(b)>self.dataType.size[0]:
                b.remove(0)

        return b

    @typeCheck(SpecializingPath)
    def regenerate(self, variableSpecializerPath, moreCallBackAccepted=True):
        """This method participates in the specialization proces.

        It creates a VariableSpecializerResult in the provided path that
        contains a generated value that follows the definition of the Data
        """
        self._logger.debug("Regenerate size {0}".format(self))
        if variableSpecializerPath is None:
            raise Exception("VariableSpecializerPath cannot be None")

        try:
            newValue = self._computeExpectedValue(variableSpecializerPath)
            variableSpecializerPath.addResult(self, newValue)
        except Exception as e:
            self._logger.debug("Cannot specialize since no value is available for the size dependencies, we create a callback function in case it can be computed later: {0}".format(e))
            pendingValue = TypeConverter.convert("PENDING VALUE", ASCII, BitArray)
            variableSpecializerPath.addResult(self, pendingValue)
            if moreCallBackAccepted:
#                for field in self.fields:
                variableSpecializerPath.registerFieldCallBack(self.fields, self, parsingCB=False)

            else:
                raise e
            
        return [variableSpecializerPath]
            
    def __str__(self):
        """The str method."""
        return "Size({0}) - Type:{1}".format(str([f.name for f in self.fields]), self.dataType)

    @property
    def dataType(self):
        """The datatype used to encode the result of the computed size.

        :type: :class:`netzob.Model.Types.AbstractType.AbstractType`
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

