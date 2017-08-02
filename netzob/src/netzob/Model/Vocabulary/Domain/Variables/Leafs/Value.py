#-*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|          01001110 01100101 01110100 01111010 01101111 01100010            |
#|                                                                           |
#|               Netzob : Inferring communication protocols                  |
#+---------------------------------------------------------------------------+
#| Copyright (C) 2011-2017 Georges Bossert and Frédéric Guihéry              |
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
from bitarray import bitarray
from lxml import etree
from lxml.etree import ElementTree
#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger
from netzob.Model.Vocabulary.Domain.Variables.Leafs.AbstractRelationVariableLeaf import AbstractRelationVariableLeaf
from netzob.Model.Vocabulary.AbstractField import AbstractField
from netzob.Model.Vocabulary.Types.ASCII import ASCII
from netzob.Model.Vocabulary.Types.AbstractType import AbstractType
from netzob.Model.Vocabulary.Types.TypeConverter import TypeConverter
from netzob.Model.Vocabulary.Types.BitArray import BitArray
from netzob.Model.Vocabulary.Domain.Specializer.SpecializingPath import SpecializingPath
from netzob.Model.Vocabulary.Domain.Parser.ParsingPath import ParsingPath
from netzob.Model.Vocabulary.Domain.GenericPath import GenericPath


@NetzobLogger
class Value(AbstractRelationVariableLeaf):
    """A value relation between one variable and the value of a field

    >>> from netzob.all import *
    >>> msg = RawMessage("netzob;netzob!")
    >>> f1 = Field(ASCII(nbChars=(2, 8)), name="f1")
    >>> f2 = Field(ASCII(";"), name="f2")
    >>> f3 = Field(Value(f1), name="f3")
    >>> f4 = Field(ASCII("!"), name="f4")
    >>> s = Symbol(fields=[f1, f2, f3, f4])
    >>> mp = MessageParser()
    >>> print(mp.parseMessage(msg, s))
    [bitarray('011011100110010101110100011110100110111101100010'), bitarray('00111011'), bitarray('011011100110010101110100011110100110111101100010'), bitarray('00100001')]

    # lets try another way of expressing such a relation

    >>> from netzob.all import *
    >>> msg = RawMessage("netzob;netzob!")
    >>> f3 = Field(ASCII(nbChars=6), name="f3")
    >>> f1 = Field(Value(f3), name="f1")
    >>> f2 = Field(ASCII(";"), name="f2")
    >>> f4 = Field(ASCII("!"), name="f4")
    >>> s = Symbol(fields=[f1, f2, f3, f4])
    >>> mp = MessageParser()
    >>> print(mp.parseMessage(msg, s))
    [bitarray('011011100110010101110100011110100110111101100010'), bitarray('00111011'), bitarray('011011100110010101110100011110100110111101100010'), bitarray('00100001')]


    Lets see what happen when we specialize a Value field

    >>> from netzob.all import *
    >>> f1 = Field(ASCII("netzob"), name="f1")
    >>> f2 = Field(ASCII(";"), name="f2")
    >>> f3 = Field(Value(f1), name="f3")
    >>> f4 = Field(ASCII("!"), name="f4")
    >>> s = Symbol(fields=[f1, f2, f3, f4])
    >>> ms = MessageSpecializer()
    >>> print(TypeConverter.convert(ms.specializeSymbol(s).generatedContent, BitArray, Raw))
    b'netzob;netzob!'
    
    >>> from netzob.all import *
    >>> f3 = Field(ASCII("netzob"), name="f3")
    >>> f2 = Field(ASCII(";"), name="f2")
    >>> f1 = Field(Value(f3), name="f1")
    >>> f4 = Field(ASCII("!"), name="f4")
    >>> s = Symbol(fields=[f1, f2, f3, f4])
    >>> ms = MessageSpecializer()
    >>> print(TypeConverter.convert(ms.specializeSymbol(s).generatedContent, BitArray, Raw))
    b'netzob;netzob!'

    A value relationship also accepts custom operations

    >>> from netzob.all import *
    >>> f0 = Field(1, name="f0")
    >>> f1 = Field(ASCII(":"), name="f1")
    >>> f2 = Field(Value(f0, operation = lambda x: TypeConverter.convert(TypeConverter.convert(x, BitArray, Integer) + 1, Integer, BitArray)), name="f2")
    >>> s = Symbol([f0, f1, f2])
    >>> print(s.specialize())
    b'\\x01:\\x02'
    >>> m1 = RawMessage(s.specialize())
    >>> s.messages = [m1]
    >>> print(s)
    f0     | f1  | f2    
    ------ | --- | ------
    '\\x01' | ':' | '\\x02'
    ------ | --- | ------
    

    """

    def __init__(self, field, name=None, operation=None):
        if not isinstance(field, AbstractField):
            raise Exception("Expecting a field")
        super(Value, self).__init__(
            "Value", fieldDependencies=[field], name=name)
        self.operation = operation

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

        # we check if memory referenced its value (memory is priority)
        memory = path.memory

        if memory is None:
            raise Exception("Provided path has no memory attached.")

        return memory.hasValue(self)

    @typeCheck(GenericPath)
    def valueCMP(self, parsingPath, acceptCallBack=True, carnivorous=False):
        self._logger.debug("ValueCMP")
        results = []
        if parsingPath is None:
            raise Exception("ParsingPath cannot be None")

        content = parsingPath.getDataAssignedToVariable(self)
        if content is None:
            raise Exception("No data assigned.")

        # we verify we have access to the expected value
        expectedValue = self._computeExpectedValue(parsingPath)
        
        self._logger.debug(
            "Expected value to parse: {0}".format(expectedValue))

        if expectedValue is None:

            # lets compute what could be the possible value
            fieldDep = self.fieldDependencies[0]
            (minSizeDep, maxSizeDep) = fieldDep.domain.dataType.size
            if minSizeDep > len(content):
                self._logger.debug(
                    "Size of the content to parse is smallest than the min expected size of the dependency field"
                )
                return results

            for size in range(
                    min(maxSizeDep, len(content)), minSizeDep - 1, -1):
                # we create a new parsing path and returns it
                newParsingPath = parsingPath.duplicate()
                newParsingPath.addResult(self, content[:size].copy())
                self._addCallBacksOnUndefinedFields(newParsingPath)
                results.append(newParsingPath)
        else:
            if content[:len(expectedValue)] == expectedValue:
                self._logger.debug(
                    "add result: {0}".format(expectedValue.copy()))
                parsingPath.addResult(self, expectedValue.copy())
                results.append(parsingPath)

        return results

    @typeCheck(ParsingPath)
    def learn(self, parsingPath, acceptCallBack=True, carnivorous=False):
        self._logger.warn("Value LEARN")
        if parsingPath is None:
            raise Exception("VariableParserPath cannot be None")
        raise Exception("Not Implemented")
        return []

    @typeCheck(ParsingPath)
    def domainCMP(self, parsingPath, acceptCallBack=True, carnivorous=False):
        """This method participates in the abstraction process.

        It creates a VariableSpecializerResult in the provided path if
        the remainingData (or some if it) follows the type definition"""

        return self.valueCMP(parsingPath, acceptCallBack)

    @typeCheck(ParsingPath)
    def _addCallBacksOnUndefinedFields(self, parsingPath):
        """Identify each dependency field that is not yet defined and register a
        callback to try to recompute the value """
        parsingPath.registerFieldCallBack(self.fieldDependencies, self)

    def _computeExpectedValue(self, parsingPath):
        self._logger.debug("compute expected value for Value field")

        fieldDep = self.fieldDependencies[0]
        if fieldDep is None:
            raise Exception("No dependency field specified.")

        if not parsingPath.isDataAvailableForField(fieldDep):
            return None
        else:
            return self._applyOperation(parsingPath.getDataAssignedToField(fieldDep))

    @typeCheck(SpecializingPath)
    def regenerate(self, variableSpecializerPath, moreCallBackAccepted=True):
        """This method participates in the specialization proces.

        It creates a VariableSpecializerResult in the provided path that
        contains a generated value that follows the definition of the Data
        """
        self._logger.debug("Regenerate value {0}".format(self))
        if variableSpecializerPath is None:
            raise Exception("VariableSpecializerPath cannot be None")

        try:
            newValue = self._computeExpectedValue(variableSpecializerPath)

            variableSpecializerPath.addResult(self, newValue)
        except Exception as e:
            self._logger.debug(
                "Cannot specialize since no value is available for the value dependencies, we create a callback function in case it can be computed later: {0}".
                format(e))

            pendingValue = TypeConverter.convert("PENDING VALUE", ASCII,
                                                 BitArray)
            variableSpecializerPath.addResult(self, pendingValue)
            if moreCallBackAccepted:
                variableSpecializerPath.registerFieldCallBack(
                    self.fieldDependencies, self, parsingCB=False)
            else:
                raise e

        return [variableSpecializerPath]

    def _applyOperation(self, data):
        """This method can be use to apply the specified operation function to the data parameter.
        If no operation function is known, the data parameter is returned"""
        if self.__operation is None:
            return data

        return self.__operation(data)

    # def getValue(self, processingToken):
    #     """Return the current value of targeted field.
    #     """
    #     # first checks the pointed fields all have a value
    #     hasValue = True
    #     for field in self.fields:
    #         if field.domain != self and not processingToken.isValueForVariableAvailable(field.domain):
    #             hasValue = False

    #     if not hasValue:
    #         raise Exception("Impossible to compute the value (getValue) of the current Size field since some of its dependencies have no value")
    #     else:
    #         size = 0
    #         for field in self.fields:
    #             if field.domain is self:
    #                 fieldValue = self.dataType.generate()
    #             else:
    #                 fieldValue = processingToken.getValueForVariable(field.domain)
    #             if fieldValue is None:
    #                 break
    #             else:
    #                 tmpLen = len(fieldValue)
    #                 tmpLen = int(math.ceil(tmpLen / 8.0) * 8)  # Round to the upper closest multiple of 8 (the size of a byte),
    #                                                            # because this is what will be considered durring field specialization
    #                 size += tmpLen
    #         size = size * self.factor + self.offset
    #         b = TypeConverter.convert(size, Integer, BitArray)

    #         while len(b)<self.dataType.size[0]:
    #             b.insert(0, False)

    #         return b

    def __str__(self):
        """The str method."""
        return "Value({0})".format(str(self.fieldDependencies[0].name))

    @property
    def dataType(self):
        """The datatype used to encode the result of the computed size.

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
            raise ValueError(
                "The datatype of a size field must declare its length")
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
            raise TypeError(
                "Offset cannot be None, use 0 if no offset should be applied.")
        self.__offset = offset

    @property
    def operation(self):
        """Defines the operation to be performed on the found value. This operation takes the form
        of a python function that accepts a single parameter of BitArray type and returns a BitArray."""
        return self.__operation

    @operation.setter
    def operation(self, operation):
        if operation is not None and not callable(operation):
            raise TypeError("Operation must be a function")
        self.__operation = operation

    def XMLProperties(currentNode, xmlValue, symbol_namespace, common_namespace):
        AbstractRelationVariableLeaf.XMLProperties(currentNode, xmlValue, symbol_namespace, common_namespace)

        # Save Properties
        # if currentNode.factor is not None:
        #     xmlValue.set("factor", str(currentNode.factor))
        # if currentNode.offset is not None:
        #     xmlValue.set("offset", str(currentNode.offset))
        # Maybe not supported
        # if currentNode.operation is not None:
            # xmlValue.set("operation", str(currentNode.operation))

        # Save the DataType
        # if currentNode.dataType is not None:
        #     currentNode.dataType.saveToXML(xmlValue, symbol_namespace, common_namespace)

    def saveToXML(self, xmlroot, symbol_namespace, common_namespace):
        xmlValue = etree.SubElement(xmlroot, "{" + symbol_namespace + "}value")

        Value.XMLProperties(self, xmlValue, symbol_namespace, common_namespace)

    @staticmethod
    def restoreFromXML(xmlroot, symbol_namespace, common_namespace, attributes):

        # if xmlroot.get('factor') is not None:
        #     attributes['factor'] = float(xmlroot.get('factor'))
        # else:
        #     attributes['factor'] = None
        # if xmlroot.get('offset') is not None:
        #     attributes['offset'] = int(xmlroot.get('offset'))
        # else:
        #     attributes['offset'] = None
        AbstractRelationVariableLeaf.restoreFromXML(xmlroot, symbol_namespace, common_namespace, attributes)

        return attributes

    @staticmethod
    def loadFromXML(xmlroot, symbol_namespace, common_namespace):

        a = Value.restoreFromXML(xmlroot, symbol_namespace, common_namespace, dict())

        value = None

        if 'fieldDependencies' in a.keys():
            from netzob.Model.Vocabulary.Field import Field
            value = Value(name=a['name'], field=Field())
            if 'id' in a.keys():
                value.id = a['id']
            if 'svas' in a.keys():
                value.svas = a['svas']
            # if 'factor' in a.keys():
            #     value.factor = a['factor']
            # if 'offset' in a.keys():
            #     value.offset = a['offset']
            # TODO: Operation is missing. No way to save operation yet
            if 'fieldDependencies' in a.keys():
                from netzob.Export.XMLHandler.XMLHandler import XMLHandler
                # remove placeholder field again
                value.fieldDependencies = []
                unresolved = dict()
                for ref in a['fieldDependencies']:
                    unresolved[ref] = value
                XMLHandler.add_to_unresolved_dict('fieldDependencies', unresolved)
        return value





