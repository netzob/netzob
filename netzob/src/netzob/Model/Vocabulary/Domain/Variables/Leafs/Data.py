# -*- coding: utf-8 -*-

# +---------------------------------------------------------------------------+
# |          01001110 01100101 01110100 01111010 01101111 01100010            |
# |                                                                           |
# |               Netzob : Inferring communication protocols                  |
# +---------------------------------------------------------------------------+
# | Copyright (C) 2011-2017 Georges Bossert and Frédéric Guihéry              |
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
from bitarray import bitarray
from lxml import etree
from lxml.etree import ElementTree
# +---------------------------------------------------------------------------+
# | Local application imports                                                 |
# +---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger
from netzob.Model.Vocabulary.Domain.Variables.Leafs.AbstractVariableLeaf import AbstractVariableLeaf
from netzob.Model.Vocabulary.Domain.Specializer.SpecializingPath import SpecializingPath
from netzob.Model.Vocabulary.Domain.Parser.ParsingPath import ParsingPath
from netzob.Model.Vocabulary.Domain.GenericPath import GenericPath


@NetzobLogger
class Data(AbstractVariableLeaf):
    """Represents a data, meaning a portion of content in the final
    message. This representation is achieved using a definition domain.
    So the Data stores at least two things: 1) the definition domain and constraints over it and 2) its current value

    For instance:

    >>> from netzob.all import *
    >>> f = Field()
    >>> f.domain = Data(dataType=ASCII(), originalValue=TypeConverter.convert("zoby", ASCII, BitArray), name="pseudo")
    >>> print(f.domain.varType)
    Data
    >>> print(TypeConverter.convert(f.domain.currentValue, BitArray, Raw))
    b'zoby'
    >>> print(f.domain.dataType)
    ASCII=None ((0, None))
    >>> print(f.domain.name)
    pseudo

    >>> f = Field(ASCII("hello zoby"))
    >>> print(f.domain.varType)
    Data
    >>> print(TypeConverter.convert(f.domain.currentValue, BitArray, ASCII))
    hello zoby


    Below are more unit tests that aims at testing that a Data variable is correctly handled in all cases
    of abstraction and specialization.

    Let's begin with abstraction. We must consider the following cases:
    * CONSTANT
    * PERSISTENT
    * EPHEMERAL
    * VOLATILE

    Case 1: Abstraction of a constant data

    >>> from netzob.all import *
    >>> f0 = Field(domain=Data(dataType=ASCII(), originalValue=TypeConverter.convert("netzob", ASCII, BitArray), name="netzob", svas=SVAS.CONSTANT))
    >>> s = Symbol(name="S0", fields=[f0])
    >>> msg1 = RawMessage("netzob")
    >>> mp = MessageParser()
    >>> print(mp.parseMessage(msg1, s))
    [bitarray('011011100110010101110100011110100110111101100010')]

    >>> msg2 = RawMessage("netzab")
    >>> mp = MessageParser()
    >>> print(mp.parseMessage(msg2, s))
    Traceback (most recent call last):
      ...
    netzob.Model.Vocabulary.Domain.Parser.MessageParser.InvalidParsingPathException: No parsing path returned while parsing 'b'netzab''


    Case 2: Abstraction of a persitent data

    >>> from netzob.all import *
    >>> f0 = Field(domain=Data(dataType=ASCII(nbChars=(5, 10)), name="netzob", svas=SVAS.PERSISTENT))
    >>> s = Symbol(name="S0", fields=[f0])
    >>> msg1 = RawMessage("netzob")
    >>> msg2 = RawMessage("netzob")
    >>> msg3 = RawMessage("netzab")
    >>> mp = MessageParser()
    >>> print(mp.parseMessage(msg1, s))
    [bitarray('011011100110010101110100011110100110111101100010')]
    >>> print(mp.parseMessage(msg2, s))
    [bitarray('011011100110010101110100011110100110111101100010')]
    >>> print(mp.parseMessage(msg3, s))
    Traceback (most recent call last):
      ...
    netzob.Model.Vocabulary.Domain.Parser.MessageParser.InvalidParsingPathException: No parsing path returned while parsing 'b'netzab''


    >>> f0 = Field(domain=Data(dataType=ASCII(), originalValue=TypeConverter.convert("netzob", ASCII, BitArray), name="netzob", svas=SVAS.PERSISTENT))
    >>> s = Symbol(name="S0", fields=[f0])
    >>> msg1 = RawMessage("netzab")
    >>> mp = MessageParser()
    >>> print(mp.parseMessage(msg1, s))
    Traceback (most recent call last):
      ...
    netzob.Model.Vocabulary.Domain.Parser.MessageParser.InvalidParsingPathException: No parsing path returned while parsing 'b'netzab''


    Case 3: Abstraction of an ephemeral data

    >>> from netzob.all import *
    >>> f0 = Field(domain=Data(dataType=ASCII(nbChars=(5, 10)), name="netzob", svas=SVAS.EPHEMERAL))
    >>> s = Symbol(name="S0", fields=[f0])
    >>> msg1 = RawMessage("netzob")
    >>> msg2 = RawMessage("netzob")
    >>> msg3 = RawMessage("netzab")
    >>> mp = MessageParser()
    >>> print(mp.parseMessage(msg1, s))
    [bitarray('011011100110010101110100011110100110111101100010')]
    >>> print(mp.memory)
    Data (ASCII=None ((40, 80))): b'netzob'

    >>> print(mp.parseMessage(msg2, s))
    [bitarray('011011100110010101110100011110100110111101100010')]
    >>> print(mp.memory)
    Data (ASCII=None ((40, 80))): b'netzob'
    
    >>> print(mp.parseMessage(msg3, s))
    [bitarray('011011100110010101110100011110100110000101100010')]
    >>> print(mp.memory)
    Data (ASCII=None ((40, 80))): b'netzab'


    Case 4: Abstraction of a volatile data

    >>> from netzob.all import *
    >>> f0 = Field(domain=Data(dataType=ASCII(nbChars=(5, 10)), name="netzob", svas=SVAS.VOLATILE))
    >>> s = Symbol(name="S0", fields=[f0])
    >>> msg1 = RawMessage("netzob")
    >>> msg2 = RawMessage("netzob")
    >>> msg3 = RawMessage("netzab")
    >>> mp = MessageParser()
    >>> print(mp.parseMessage(msg1, s))
    [bitarray('011011100110010101110100011110100110111101100010')]
    >>> print(len(str(mp.memory)))
    0

    >>> print(mp.parseMessage(msg2, s))
    [bitarray('011011100110010101110100011110100110111101100010')]
    >>> print(len(str(mp.memory)))
    0
    
    >>> print(mp.parseMessage(msg3, s))
    [bitarray('011011100110010101110100011110100110000101100010')]
    >>> print(len(str(mp.memory)))
    0

    
    Now, let's focus on the specialization of a data field

    Case 1: Specialization of a constant data

    >>> from netzob.all import *
    >>> f0 = Field(domain=Data(dataType=ASCII(), originalValue=TypeConverter.convert("netzob", ASCII, BitArray), name="netzob", svas=SVAS.CONSTANT))
    >>> s = Symbol(name="S0", fields=[f0])
    >>> ms = MessageSpecializer()
    >>> print(ms.specializeSymbol(s).generatedContent)
    bitarray('011011100110010101110100011110100110111101100010')
    >>> print(ms.specializeSymbol(s).generatedContent)
    bitarray('011011100110010101110100011110100110111101100010')
    >>> print(len(str(ms.memory)))
    0

    >>> f0 = Field(domain=Data(dataType=ASCII(nbChars=(5, 10)), name="netzob", svas=SVAS.CONSTANT))
    >>> s = Symbol(name="S0", fields=[f0])
    >>> ms = MessageSpecializer()
    >>> print(ms.specializeSymbol(s).generatedContent)
    Traceback (most recent call last):
      ...
    Exception: Cannot specialize this symbol.


    Case 2: Specialization of a persistent data

    >>> from netzob.all import *
    >>> f0 = Field(domain=Data(dataType=ASCII(), originalValue=TypeConverter.convert("netzob", ASCII, BitArray), name="netzob", svas=SVAS.PERSISTENT))
    >>> s = Symbol(name="S0", fields=[f0])
    >>> ms = MessageSpecializer()
    >>> print(ms.specializeSymbol(s).generatedContent)
    bitarray('011011100110010101110100011110100110111101100010')
    >>> print(len(str(ms.memory)))
    0

    >>> f0 = Field(domain=Data(dataType=ASCII(nbChars=5), name="netzob", svas=SVAS.PERSISTENT))
    >>> s = Symbol(name="S0", fields=[f0])
    >>> ms = MessageSpecializer()
    >>> generated1 = ms.specializeSymbol(s).generatedContent
    >>> print(len(generated1))
    40
    >>> print(ms.memory.hasValue(f0.domain))
    True
    >>> generated2 = ms.specializeSymbol(s).generatedContent
    >>> print(len(generated2))
    40
    >>> generated1 == generated2
    True

    Case 3: Specialization of an ephemeral data


    >>> from netzob.all import *
    >>> f0 = Field(domain=Data(dataType=ASCII(), originalValue=TypeConverter.convert("netzob", ASCII, BitArray), name="netzob", svas=SVAS.EPHEMERAL))
    >>> s = Symbol(name="S0", fields=[f0])
    >>> ms = MessageSpecializer()
    >>> print(ms.memory.hasValue(f0.domain))
    False
    >>> generated1 = ms.specializeSymbol(s).generatedContent
    >>> print(ms.memory.hasValue(f0.domain))
    True
    >>> generated2 = ms.specializeSymbol(s).generatedContent
    >>> generated2 == ms.memory.getValue(f0.domain)
    True
    >>> generated1 == generated2
    False

    
    >>> from netzob.all import *
    >>> f0 = Field(domain=Data(dataType=ASCII(nbChars=(5, 10)), name="netzob", svas=SVAS.EPHEMERAL))
    >>> s = Symbol(name="S0", fields=[f0])
    >>> ms = MessageSpecializer()
    >>> print(ms.memory.hasValue(f0.domain))
    False
    >>> generated1 = ms.specializeSymbol(s).generatedContent
    >>> print(ms.memory.hasValue(f0.domain))
    True
    >>> generated2 = ms.specializeSymbol(s).generatedContent
    >>> generated2 == ms.memory.getValue(f0.domain)
    True
    >>> generated1 == generated2
    False

    
    Case 4: Specialization of a volatile data


    >>> from netzob.all import *
    >>> f0 = Field(domain=Data(dataType=ASCII(nbChars=(5,10)), name="netzob", svas=SVAS.VOLATILE))
    >>> s = Symbol(name="S0", fields=[f0])
    >>> ms = MessageSpecializer()
    >>> print(ms.memory.hasValue(f0.domain))
    False
    >>> generated1 = ms.specializeSymbol(s).generatedContent
    >>> print(ms.memory.hasValue(f0.domain))
    False
    >>> generated2 = ms.specializeSymbol(s).generatedContent
    >>> generated2 == ms.memory.hasValue(f0.domain)
    False
    >>> generated1 == generated2
    False
    
        
    """

    def __init__(self, dataType, originalValue=None, name=None, svas=None):
        """The constructor of a data variable

        :param dataType: the definition domain of the data.
        :type dataType: :class:`netzob.Model.Vocabulary.Types.AbstractType.AbstractType`
        :keyword originalValue: the value of the data (can be None)
        :type originalValue: :class:`object`
        :keyword name: the name of the data, if None name will be generated
        :type name: :class:`str`
        :keyword learnable: a flag stating if the current value of the data can be overwritten following with parsed data
        :type learnable: :class:`bool`
        :keyword mutable: a flag stating if the current value can changes with the parsing process
        :type mutable: :class:`bool`

        :raises: :class:`TypeError` or :class:`ValueError` if parameters are not valid.
        """

        super(Data, self).__init__(
            self.__class__.__name__, name=name, svas=svas)

        self.dataType = dataType
        self.currentValue = originalValue

    def __str__(self):
        return "Data ({0})".format(self.dataType)

    def __key(self):
        return (self.__class__.__name__, self.currentValue, self.dataType,
                self.svas, self.name)

    @typeCheck(GenericPath)
    def isDefined(self, path):
        """Checks if a value is available either in data's definition or in memory

        :parameter path: the current path used either to abstract and specializa this data
        :type path: :class:`netzob.Model.Vocabulary.Domain.GenericPath.GenericPath`
        :return: a boolean that indicates if a value is available for this data
        :rtype: :class:`bool`
    
        """
        if path is None:
            raise Exception("Path cannot be None")

        #  first we check if current value is assigned to the data
        if not self.currentValue is None:
            return True

        # we check if memory referenced its value (memory is priority)
        memory = path.memory

        if memory is None:
            raise Exception("Provided path has no memory attached.")

        return memory.hasValue(self)

    @typeCheck(ParsingPath)
    def domainCMP(self, parsingPath, acceptCallBack=True, carnivorous=False):
        """Checks if the value assigned to this variable could be parsed against
        the definition domain of the data.

        """

        if parsingPath is None:
            raise Exception("ParsingPath cannot be None")

        content = parsingPath.getDataAssignedToVariable(self)

        self._logger.debug(
            "DomainCMP {0} with {1}".format(content, self.dataType))

        (minSize, maxSize) = self.dataType.size
        if maxSize is None:
            maxSize = len(content)

        if len(content) < minSize:
            self._logger.debug(
                "Length of the content is too short ({0}), expect data of at least {1} bits".
                format(len(content), minSize))
        else:

            # if carnivorous:
            #     minSize = len(content)
            #     maxSize = len(content)

            # for offset in xrange(len(content) / 2):

            #     # left
            #     size = content[:offset]
            #     if size == 0 or self.dataType.canParse(content[:size]):
            #         # we create a new parsing path and returns it
            #         newParsingPath = parsingPath.duplicate()
            #         newParsingPath.addResult(self, content[:size].copy())
            #         yield newParsingPath

            #     # right
            #     size = len(content) - 1 - offset
            #     if self.dataType.canParse(content[:size]):
            #         # we create a new parsing path and returns it
            #         newParsingPath = parsingPath.duplicate()
            #         newParsingPath.addResult(self, content[:size].copy())
            #         yield newParsingPath

            # if len(content) / 2 % 2 == 1:
            #     size = len(content) / 2
            #     if self.dataType.canParse(content[:size]):
            #         # we create a new parsing path and returns it
            #         newParsingPath = parsingPath.duplicate()
            #         newParsingPath.addResult(self, content[:size].copy())
            #         yield newParsingPath

            for size in range(min(maxSize, len(content)), minSize - 1, -1):
                # size == 0 : deals with 'optional' data
                if size == 0 or self.dataType.canParse(content[:size]):
                    # we create a new parsing path and returns it
                    newParsingPath = parsingPath.duplicate()

                    newParsingPath.addResult(self, content[:size].copy())
                    yield newParsingPath

    @typeCheck(ParsingPath)
    def valueCMP(self, parsingPath, acceptCallBack=True, carnivorous=False):
        if parsingPath is None:
            raise Exception("ParsingPath cannot be None")

        expectedValue = self.currentValue

        # we check a value is available in memory
        memory = parsingPath.memory
        if memory is None:
            raise Exception("No memory available")

        if memory.hasValue(self):
            expectedValue = memory.getValue(self)

        if expectedValue is None:
            raise Exception(
                "Data '{0}' has no value defined in its definition domain".
                format(self))

        content = parsingPath.getDataAssignedToVariable(self)
        if content is None:
            raise Exception("No data assigned to the variable")

        results = []
        if len(content) >= len(expectedValue) and content[:len(
                expectedValue)] == expectedValue:
            parsingPath.addResult(self, expectedValue.copy())
            results.append(parsingPath)
        else:
            self._logger.debug("{0} cannot be parsed with variable {1}".format(
                content, self.id))
        return results

    @typeCheck(ParsingPath)
    def learn(self, parsingPath, acceptCallBack=True, carnivorous=False):

        if parsingPath is None:
            raise Exception("ParsingPath cannot be None")

        content = parsingPath.getDataAssignedToVariable(self)

        self._logger.debug("Learn {0} with {1}".format(content, self.dataType))

        (minSize, maxSize) = self.dataType.size
        if maxSize is None:
            maxSize = len(content)


        if len(content) < minSize:
            self._logger.debug(
                "Length of the content is too short ({0}), expect data of at least {1} bits".
                format(len(content), minSize))
        else:

            #        if carnivorous:
            #            minSize = len(content)
            #            maxSize = len(content)

            for size in range(min(maxSize, len(content)), minSize - 1, -1):
                # size == 0 : deals with 'optional' data
                if size == 0 or self.dataType.canParse(content[:size]):
                    # we create a new parsing path and returns it
                    newParsingPath = parsingPath.duplicate()
                    newParsingPath.addResult(self, content[:size].copy())
                    newParsingPath.memory.memorize(self, content[:size].copy())
                    yield newParsingPath

    @typeCheck(SpecializingPath)
    def use(self, variableSpecializerPath, acceptCallBack=True):
        """This method participates in the specialization proces.
        It creates a VariableSpecializerResult in the provided path that either
        contains the memorized value or the predefined value of the variable"""

        if variableSpecializerPath is None:
            raise Exception("VariableSpecializerPath cannot be None")

        memory = variableSpecializerPath.memory

        result = []

        if memory.hasValue(self):
            variableSpecializerPath.addResult(self, memory.getValue(self))
            result.append(variableSpecializerPath)
        elif self.currentValue is not None:
            variableSpecializerPath.addResult(self, self.currentValue)
            result.append(variableSpecializerPath)

        return result

    @typeCheck(SpecializingPath)
    def regenerate(self, variableSpecializerPath, acceptCallBack=True):
        """This method participates in the specialization proces.
        It creates a VariableSpecializerResult in the provided path that
        contains a generated value that follows the definition of the Data
        """
        self._logger.debug("Regenerate Variable {0}".format(self))

        if variableSpecializerPath is None:
            raise Exception("VariableSpecializerPath cannot be None")

        newValue = self.dataType.generate()

        variableSpecializerPath.addResult(self, newValue)
        return [variableSpecializerPath]

    @typeCheck(SpecializingPath)
    def regenerateAndMemorize(self,
                              variableSpecializerPath,
                              acceptCallBack=True):
        """This method participates in the specialization proces.
        It memorizes the value present in the path of the variable
        """

        self._logger.debug("RegenerateAndMemorize Variable {0}".format(self))

        if variableSpecializerPath is None:
            raise Exception("VariableSpecializerPath cannot be None")

        newValue = self.dataType.generate()
        variableSpecializerPath.memory.memorize(self, newValue)

        variableSpecializerPath.addResult(self, newValue)
        return [variableSpecializerPath]

    @property
    def currentValue(self):
        """The current value of the data.

        :type: :class:`bitarray`
        """
        if self.__currentValue is not None:
            return self.__currentValue.copy()
        else:
            return None

    @currentValue.setter
    @typeCheck(bitarray)
    def currentValue(self, currentValue):
        if currentValue is not None:
            cv = currentValue.copy()
        else:
            cv = currentValue
        self.__currentValue = cv

    def XMLProperties(currentNode, xmlData, symbol_namespace, common_namespace):

        AbstractVariableLeaf.XMLProperties(currentNode, xmlData, symbol_namespace, common_namespace)

        if currentNode.currentValue is not None:
            xmlData.set("currentValue", str(currentNode.currentValue)[10:-2])

        # Save the DataType
        if currentNode.dataType is not None:
            xmlDataType = etree.SubElement(xmlData, "{" + symbol_namespace + "}datatype")
            currentNode.dataType.saveToXML(xmlDataType, symbol_namespace, common_namespace)

    def saveToXML(self, xmlroot, symbol_namespace, common_namespace):
        xmlData = etree.SubElement(xmlroot, "{" + symbol_namespace + "}data")

        Data.XMLProperties(self, xmlData, symbol_namespace, common_namespace)

    @staticmethod
    def restoreFromXML(xmlroot, symbol_namespace, common_namespace, attributes):

        from bitarray import bitarray
        if xmlroot.get('currentValue') is not None:
            attributes['currentValue'] = bitarray(str(xmlroot.get('currentValue')))
        else:
            attributes['currentValue'] = None

        dataType = None
        if xmlroot.find("{" + symbol_namespace + "}datatype") is not None:
            xmlDataType = xmlroot.find("{" + symbol_namespace + "}datatype")
            if xmlDataType.find("{" + symbol_namespace + "}raw") is not None:
                xmlRaw = xmlDataType.find("{" + symbol_namespace + "}raw")
                from netzob.Model.Vocabulary.Types.Raw import Raw
                raw = Raw.loadFromXML(xmlRaw, symbol_namespace, common_namespace)
                if raw is not None:
                    dataType = raw
            elif xmlDataType.find("{" + symbol_namespace + "}ascii") is not None:
                xmlASCII = xmlDataType.find("{" + symbol_namespace + "}ascii")
                from netzob.Model.Vocabulary.Types.ASCII import ASCII
                ascii = ASCII.loadFromXML(xmlASCII, symbol_namespace, common_namespace)
                if ascii is not None:
                    dataType = ascii
            elif xmlDataType.find("{" + symbol_namespace + "}bitarray") is not None:
                xmlBitarray = xmlDataType.find("{" + symbol_namespace + "}bitarray")
                from netzob.Model.Vocabulary.Types.BitArray import BitArray
                bitarray = BitArray.loadFromXML(xmlBitarray, symbol_namespace, common_namespace)
                if bitarray is not None:
                    dataType = bitarray
            elif xmlDataType.find("{" + symbol_namespace + "}hexaString") is not None:
                xmlHexaString = xmlDataType.find("{" + symbol_namespace + "}hexaString")
                from netzob.Model.Vocabulary.Types.HexaString import HexaString
                hexastring = HexaString.loadFromXML(xmlHexaString, symbol_namespace, common_namespace)
                if hexastring is not None:
                    dataType = hexastring
            elif xmlDataType.find("{" + symbol_namespace + "}integer") is not None:
                xmlInteger = xmlDataType.find("{" + symbol_namespace + "}integer")
                from netzob.Model.Vocabulary.Types.Integer import Integer
                integer = Integer.loadFromXML(xmlInteger, symbol_namespace, common_namespace)
                if integer is not None:
                    dataType = integer
            elif xmlDataType.find("{" + symbol_namespace + "}ipv4") is not None:
                xmlIPv4 = xmlDataType.find("{" + symbol_namespace + "}ipv4")
                from netzob.Model.Vocabulary.Types.IPv4 import IPv4
                ipv4 = IPv4.loadFromXML(xmlIPv4, symbol_namespace, common_namespace)
                if ipv4 is not None:
                    dataType = ipv4
            elif xmlDataType.find("{" + symbol_namespace + "}Timestamp") is not None:
                xmlTimestamp = xmlDataType.find("{" + symbol_namespace + "}Timestamp")
                from netzob.Model.Vocabulary.Types.Timestamp import Timestamp
                timestamp = Timestamp.loadFromXML(xmlTimestamp, symbol_namespace, common_namespace)
                if timestamp is not None:
                    dataType = timestamp
            elif xmlDataType.find("{" + symbol_namespace + "}abstractType") is not None:
                xmlAbstractType = xmlDataType.find("{" + symbol_namespace + "}abstractType")
                from netzob.Model.Vocabulary.Types.AbstractType import AbstractType
                abstractType = AbstractType.loadFromXML(xmlAbstractType, symbol_namespace, common_namespace)
                if abstractType is not None:
                    dataType = abstractType

        attributes['dataType'] = dataType

        AbstractVariableLeaf.restoreFromXML(xmlroot, symbol_namespace, common_namespace, attributes)
        return attributes

    @staticmethod
    def loadFromXML(xmlroot, symbol_namespace, common_namespace):

        a = Data.restoreFromXML(xmlroot, symbol_namespace, common_namespace, dict())

        data = None

        if 'dataType' in a.keys():
            data = Data(dataType=a['dataType'], originalValue=a['currentValue'], name=a['name'], svas=a['svas'])
            if 'id' in a.keys():
                data.id = a['id']
            # Not possible and not necessary
            # if 'varType' in a.keys():
            #     data.varType = a['varType']
        return data


