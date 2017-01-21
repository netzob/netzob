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
import random
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
from netzob.Model.Types.HexaString import HexaString
from netzob.Model.Types.AbstractType import AbstractType
from netzob.Model.Types.TypeConverter import TypeConverter
from netzob.Model.Types.ASCII import ASCII
from netzob.Model.Types.BitArray import BitArray
from netzob.Model.Types.Raw import Raw
from netzob.Model.Types.Integer import Integer
from netzob.Model.Vocabulary.Domain.GenericPath import GenericPath
from netzob.Model.Vocabulary.Domain.Parser.ParsingPath import ParsingPath
from netzob.Model.Vocabulary.Domain.Specializer.SpecializingPath import SpecializingPath


@NetzobLogger
class InternetChecksum(AbstractRelationVariableLeaf):
    """An internet checksum relaton as specified in RFC 1071 (https://www.ietf.org/rfc/rfc1071.txt).
    This checksum is used by ICMP, UDP, IP, TCP protocols.


    The following example, illustrates the creation of an ICMP Echo request packet
    with a valid checksum computed on-the-fly.
    
    >>> from netzob.all import *
    >>> typeField = Field(name="Type", domain=Raw(b'\\x08'))
    >>> codeField = Field(name="Code", domain=Raw(b'\\x00'))
    >>> chksumField = Field(name="Checksum")
    >>> identField = Field(name="Identifier", domain=Raw(b'\\x1d\\x22'))
    >>> seqField = Field(name="Sequence Number", domain=Raw(b'\\x00\\x07'))
    >>> timeField = Field(name="Timestamp", domain=Raw(b'\\xa8\\xf3\\xf6\\x53\\x00\\x00\\x00\\x00'))
    >>> headerField = Field(name="header")
    >>> headerField.fields = [typeField, codeField, chksumField, identField, seqField, timeField]
    >>> dataField = Field(name="Payload", domain=Raw(b'\\x60\\xb5\\x06\\x00\\x00\\x00\\x00\\x00\\x10\\x11\\x12\\x13\\x14\\x15\\x16\\x17\\x18\\x19\\x1a\\x1b\\x1c\\x1d\\x1e\\x1f\\x20\\x21\\x22\\x23\\x24\\x25\\x26\\x27\\x28\\x29\\x2a\\x2b\\x2c\\x2d\\x2e\\x2f\\x30\\x31\\x32\\x33\\x34\\x35\\x36\\x37'))

    >>> chksumField.domain = InternetChecksum([headerField, dataField], dataType=Raw(nbBytes=2))
    >>> s = Symbol(fields = [headerField, dataField])
    >>> msgs = [RawMessage(s.specialize()) for i in range(1)]
    >>> s.messages = msgs
    >>> s.addEncodingFunction(TypeEncodingFunction(HexaString))
    >>> print(s)
    Type | Code | Checksum | Identifier | Sequence Number | Timestamp          | Payload                                                                                           
    ---- | ---- | -------- | ---------- | --------------- | ------------------ | --------------------------------------------------------------------------------------------------
    '08' | '00' | '0716'   | '1d22'     | '0007'          | 'a8f3f65300000000' | '60b5060000000000101112131415161718191a1b1c1d1e1f202122232425262728292a2b2c2d2e2f3031323334353637'
    ---- | ---- | -------- | ---------- | --------------- | ------------------ | --------------------------------------------------------------------------------------------------

    """

    def __init__(self, fields, dataType=None, name=None):
        if isinstance(fields, AbstractField):
            fields = [fields]
        super(InternetChecksum, self).__init__("InternetChecksum", fieldDependencies=fields, name=name)
        if dataType is None:
            dataType = Raw(nbBytes=1)
        self.dataType = dataType

    def __key(self):
        return (self.dataType)

    def __eq__(x, y):
        try:
            return x.__key() == y.__key()
        except:
            return False
        
    def __hash__(self):
        return hash(self.__key())
        
    @typeCheck(GenericPath)
    def isDefined(self, genericPath):
        
        # we retrieve the memory of the current path
        memory = genericPath.memory
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
        self._logger.debug("Possible value of Internet Checksum field: {0}".format(possibleValue))
        
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
        self._logger.debug("INTERNET CHECKSUM LEARN")
        if parsingPath is None:
            raise Exception("VariableParserPath cannot be None")
        return []


    @typeCheck(ParsingPath)
    def domainCMP(self, parsingPath, acceptCallBack=True, carnivorous=False):
        """This method participates in the abstraction process.

        It creates a VariableSpecializerResult in the provided path if
        the remainingData (or some if it) follows the type definition"""


        results = []
        self._logger.debug("domainCMP executed on {0} by an Internet Checksum domain".format(parsingPath))

        minSize, maxSize = self.dataType.size
        if minSize != maxSize:
            raise Exception("Impossible to abstract messages if a size field has a dynamic size")

        content = parsingPath.getDataAssignedToVariable(self)
        possibleValue = content[:maxSize]

        expectedValue = None
        try:
            expectedValue = self._computeExpectedValue(parsingPath)
            if possibleValue[:len(expectedValue)] == expectedValue:
                self._logger.debug("Callback executed with success")
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

    @typeCheck(GenericPath)
    def _computeExpectedValue(self, parsingPath):
        self._logger.debug("compute expected value for Internet checksum field")
                
        # first checks the pointed fields all have a value
        hasValue = True
        for field in self.fieldDependencies:
            if field.domain != self and not parsingPath.isDataAvailableForVariable(field.domain):
                self._logger.debug("Field : {0} has no value".format(field.id))
                hasValue = False

        if not hasValue:
            raise Exception("Expected value cannot be computed, some dependencies are missing for domain {0}".format(self))
        else:
            fieldValues = []
            for field in self.fieldDependencies:
                if field.domain is self:
                    fieldSize = random.randint(field.domain.dataType.size[0], field.domain.dataType.size[1])
                    fieldValue = b"\x00" * int(fieldSize / 8)
                else:
                    fieldValue = TypeConverter.convert(parsingPath.getDataAssignedToVariable(field.domain), BitArray, Raw)
                if fieldValue is None:
                    break
                else:
                    fieldValues.append(fieldValue)

            fieldValues = b''.join(fieldValues)
            # compute the checksum of this value
            chsum = self.__checksum(fieldValues)
            b = TypeConverter.convert(chsum, Integer, BitArray, src_unitSize=AbstractType.UNITSIZE_16, src_sign = AbstractType.SIGN_UNSIGNED)
            return b

    @typeCheck(SpecializingPath)
    def regenerate(self, variableSpecializerPath, moreCallBackAccepted=True):
        """This method participates in the specialization proces.

        It creates a VariableSpecializerResult in the provided path that
        contains a generated value that follows the definition of the Data
        """
        self._logger.debug("Regenerate Internet Checksum {0}".format(self))
        if variableSpecializerPath is None:
            raise Exception("VariableSpecializerPath cannot be None")

        try:
            newValue = self._computeExpectedValue(variableSpecializerPath)
            variableSpecializerPath.addResult(self, newValue.copy())
        except Exception as e:
            self._logger.debug("Cannot specialize since no value is available for the Internet checksum dependencies, we create a callback function in case it can be computed later: {0}".format(e))
            pendingValue = TypeConverter.convert("PENDING VALUE", ASCII, BitArray)
            variableSpecializerPath.addResult(self, pendingValue)

            if moreCallBackAccepted:
#                for field in self.fields:
                variableSpecializerPath.registerFieldCallBack(self.fieldDependencies, self, parsingCB=False)
            else:
                raise e
            
        return [variableSpecializerPath]

            
            
    def __checksum(self, msg):
        self._logger.debug("Computing checksum of {0}, {1}".format(TypeConverter.convert(msg, Raw, HexaString), len(msg)))
    
        def carry_around_add(a, b):
            c = a + b
            return (c & 0xffff) + (c >> 16)

        s = 0
        for i in range(0, len(msg), 2):
            if i + 1 >= len(msg):
                w = msg[i] & 0xFF
            else:        
                w = msg[i] + (msg[i+1] << 8)
            s = carry_around_add(s, w)
        res = ~s & 0xffff
        return res
        
    def __str__(self):
        """The str method."""
        return "InternetChecksum({0}) - Type:{1}".format(str([f.name for f in self.fieldDependencies]), self.dataType)

    @property
    def dataType(self):
        """The datatype used to encode the result of the computed Internet Checksum.

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
            raise ValueError("The datatype of a checksum field must declare its length")
        self.__dataType = dataType


