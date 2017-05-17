#-*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|          01001110 01100101 01110100 01111010 01101111 01100010            |
#|                                                                           |
#|               Netzob : Inferring communication protocols                  |
#+---------------------------------------------------------------------------+
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
import binascii
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
from netzob.Model.Vocabulary.Types.HexaString import HexaString
from netzob.Model.Vocabulary.Types.AbstractType import AbstractType
from netzob.Model.Vocabulary.Types.TypeConverter import TypeConverter
from netzob.Model.Vocabulary.Types.ASCII import ASCII
from netzob.Model.Vocabulary.Types.BitArray import BitArray
from netzob.Model.Vocabulary.Types.Raw import Raw
from netzob.Model.Vocabulary.Types.Integer import Integer
from netzob.Model.Vocabulary.Domain.GenericPath import GenericPath
from netzob.Model.Vocabulary.Domain.Parser.ParsingPath import ParsingPath
from netzob.Model.Vocabulary.Domain.Specializer.SpecializingPath import SpecializingPath


@NetzobLogger
class CRC32(AbstractRelationVariableLeaf):
    r"""A crc32 relaton between a variable and the value of one or several other fields.

    >>> from netzob.all import *
    >>> messageCRC_LE = RawMessage(b'\xc5k@@\x003\x00\n|\xd9\x80\x04\x00\n|\n\x90\x00\x00\x00\x01\x81x\x00\x03\x00\x00\x00\x02\x00\x00\x00\x18\x00\x00\x00\x8f\xf1f\x0fU\xcd\x0c\x00\x01\x00\x03\x00\xcf\x03\xa7\xc4\x08\x00\x00\x00\x01\x84\x80\x00\xcf\x03\xa7\xc4')
    >>> headerField = Field(domain=Raw(b'\xc5k@@\x003\x00\n|\xd9\x80\x04\x00\n|\n\x90\x00\x00\x00\x01\x81x\x00\x03\x00\x00\x00\x02\x00\x00\x00\x18\x00\x00\x00'))
    >>> dataField = Field(domain=Raw(b'U\xcd\x0c\x00\x01\x00\x03\x00\xcf\x03\xa7\xc4\x08\x00\x00\x00\x01\x84\x80\x00\xcf\x03\xa7\xc4'))
    >>> chksumField = Field(domain = CRC32([dataField],endianness=AbstractType.ENDIAN_LITTLE))
    >>> s = Symbol(fields = [headerField,chksumField, dataField],messages=[messageCRC_LE])
    >>> s.addEncodingFunction(TypeEncodingFunction(HexaString))
    >>> print(s)# doctest: +NORMALIZE_WHITESPACE
    Field                                                                      | Field      | Field
    -------------------------------------------------------------------------- | ---------- | --------------------------------------------------
    'c56b40400033000a7cd98004000a7c0a9000000001817800030000000200000018000000' | '8ff1660f' | '55cd0c0001000300cf03a7c40800000001848000cf03a7c4'
    -------------------------------------------------------------------------- | ---------- | --------------------------------------------------

    Fixed an issue with Alt Field

    >>> messageCRC = RawMessage(b'\x8f\x48\xeb\xcc\x55\xcd\x0c\x00\x01')
    >>> messageCRC2 = RawMessage(b'\xb5\x44\x72\x9e\x58\xcf\x0c\x00\x01')
    >>> field1 = Field(name="aftermut", domain=Alt([Raw(b'\x55\xcd'), Raw(b'\x58\xcf')]))
    >>> field2 = Field(name="afterstat", domain=Raw(b'\x0c\x00\x01'))
    >>> fieldCS = Field(name="CRC", domain=CRC32([field1, field2],endianness='little'))
    >>> sym = Symbol(messages=[messageCRC, messageCRC2], fields=[fieldCS, field1, field2])
    >>> print(sym)# doctest: +NORMALIZE_WHITESPACE
    Source | Destination | CRC       | aftermut | afterstat
    ------ | ----------- | --------- | -------- | --------------
    None   | None        | '\x8fHëÌ' | 'UÍ'     | '\x0c\x00\x01'
    None   | None        | 'µDr\x9e' | 'XÏ'     | '\x0c\x00\x01'
    ------ | ----------- | --------- | -------- | --------------

    """

    def __init__(self, fields, dataType=None, name=None, endianness = AbstractType.defaultEndianness()):
        if isinstance(fields, AbstractField):
            fields = [fields]
        super(CRC32, self).__init__(varType="CRC32", fieldDependencies=fields, name=name)
        if dataType is None:
            dataType = Raw(nbBytes=4)
        self.dataType = dataType
        self.endianness = endianness

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
        self._logger.warn("Possible value of CRC32 field: {0}".format(possibleValue))

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
        self._logger.debug("CRC32 LEARN")
        if parsingPath is None:
            raise Exception("VariableParserPath cannot be None")
        return []


    @typeCheck(ParsingPath)
    def domainCMP(self, parsingPath, acceptCallBack=True, carnivorous=False):
        """This method participates in the abstraction process.

        It creates a VariableSpecializerResult in the provided path if
        the remainingData (or some if it) follows the type definition"""


        results = []
        self._logger.debug("domainCMP executed on {0} by an CRC32 domain".format(parsingPath))

        minSize, maxSize = self.dataType.size
        if minSize != maxSize:
            raise Exception("Impossible to abstract messages if a size field has a dynamic size")

        content = parsingPath.getDataAssignedToVariable(self)
        possibleValue = content[:maxSize]

        expectedValue = None
        try:
            expectedValue = self._computeExpectedValue(parsingPath)
            if possibleValue[:len(expectedValue)] == expectedValue: #or expectedValue[:len(possibleValue)] == possibleValue:
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
        self._logger.debug("compute expected value for CRC32 field")

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
                # Retrieve field value
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
            # compute the crc of this value
            chsum = self.__crc32(fieldValues)
            b = TypeConverter.convert(chsum, Integer, BitArray, src_unitSize=AbstractType.UNITSIZE_32, src_sign = AbstractType.SIGN_UNSIGNED,src_endianness= self.endianness)
            return b

    @typeCheck(SpecializingPath)
    def regenerate(self, variableSpecializerPath, moreCallBackAccepted=True):
        """This method participates in the specialization proces.

        It creates a VariableSpecializerResult in the provided path that
        contains a generated value that follows the definition of the Data
        """
        self._logger.debug("Regenerate CRC32 {0}".format(self))
        if variableSpecializerPath is None:
            raise Exception("VariableSpecializerPath cannot be None")

        try:
            newValue = self._computeExpectedValue(variableSpecializerPath)
            variableSpecializerPath.addResult(self, newValue.copy())
        except Exception as e:
            self._logger.debug("Cannot specialize since no value is available for the CRC32 dependencies, we create a callback function in case it can be computed later: {0}".format(e))
            pendingValue = TypeConverter.convert("PENDING VALUE", ASCII, BitArray)
            variableSpecializerPath.addResult(self, pendingValue)

            if moreCallBackAccepted:
#                for field in self.fields:
                variableSpecializerPath.registerFieldCallBack(self.fieldDependencies, self, parsingCB=False)
            else:
                raise e

        return [variableSpecializerPath]



    def __crc32(self, msg):
        self._logger.debug("Computing crc32 of {0}, {1}".format(TypeConverter.convert(msg, Raw, HexaString), len(msg)))

        res = binascii.crc32(msg)

        return res

    def __str__(self):
        """The str method."""
        return "crc32{0}) - Type:{1}".format(str([f.name for f in self.fieldDependencies]), self.dataType)

    @property
    def dataType(self):
        """The datatype used to encode the result of the computed CRC32.

        :type: :class:`netzob.Model.Vocabulary.Types.AbstractType.AbstractType`
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

    @property
    def endianness(self):
        """The endianness of the current value.
                The endianness definition is synchronized with the bitarray value.

                :type: `str`
                :raises: :class: `TypeError` if endianness is not an str and not a supported value.

                """
        return self.__endianness

    @endianness.setter
    @typeCheck(str)
    def endianness(self, endianness):
        if endianness is None:
            raise TypeError("Endianness cannot be None")
        if not endianness in AbstractType.supportedEndianness():
            raise TypeError(
                "Specified Endianness is not supported, please refer to the list in AbstractType.supportedEndianness().")

        self.__endianness = endianness
