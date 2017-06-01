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
#|             ANSSI,   https://www.ssi.gouv.fr                              |
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
import abc

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+
from bitarray import bitarray

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger
from netzob.Model.Vocabulary.Domain.Variables.Leafs.AbstractVariableLeaf import AbstractVariableLeaf
from netzob.Model.Vocabulary.AbstractField import AbstractField
from netzob.Model.Vocabulary.Domain.Variables.SVAS import SVAS
from netzob.Model.Vocabulary.Domain.GenericPath import GenericPath
from netzob.Model.Vocabulary.Domain.Parser.ParsingPath import ParsingPath
from netzob.Model.Vocabulary.Domain.Specializer.SpecializingPath import SpecializingPath
from netzob.Model.Vocabulary.Types.TypeConverter import TypeConverter
from netzob.Model.Vocabulary.Types.String import String
from netzob.Model.Vocabulary.Types.BitArray import BitArray
from netzob.Model.Vocabulary.Types.Raw import Raw
from netzob.Model.Vocabulary.Types.HexaString import HexaString
from netzob.Model.Vocabulary.Types.Integer import Integer
from netzob.Model.Vocabulary.Types.AbstractType import AbstractType


@NetzobLogger
class AbstractRelationVariableLeaf(AbstractVariableLeaf):
    """Represents a relation relation between variables, one being updated with the others.

    """

    def __init__(self, varType, dataType=None, fieldDependencies=None, name=None):
        super(AbstractRelationVariableLeaf, self).__init__(
            varType, name, svas=SVAS.VOLATILE)

        # Handle fieldDependencies
        if fieldDependencies is None:
            fieldDependencies = []
        elif isinstance(fieldDependencies, AbstractField):
            fieldDependencies = [fieldDependencies]
        self.fieldDependencies = fieldDependencies

        # Handle dataType
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

    def __str__(self):
        """The str method."""
        return "Relation({0}) - Type:{1}".format(
            str([f.name for f in self.fieldDependencies]), self.dataType)

    @typeCheck(GenericPath)
    def isDefined(self, path):
        """Checks if a value is available either in data's definition or in memory

        :parameter path: the current path used either to abstract and specializa this data
        :type path: :class:`GenericPath <netzob.Model.Vocabulary.Domain.GenericPath.GenericPath>`
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

    @typeCheck(ParsingPath)
    def valueCMP(self, parsingPath, carnivorous=False):
        results = []
        if parsingPath is None:
            raise Exception("ParsingPath cannot be None")

        if isinstance(self.dataType, Integer):
            expectedSize = self.dataType.unitSize
        else:
            minValue, maxValue = self.dataType.size
            if minValue != maxValue:
                raise Exception(
                    "Impossible to abstract messages if a size field has a dynamic size"
                )
            expectedSize = maxValue

        content = parsingPath.getDataAssignedToVariable(self)
        if content is None:
            raise Exception("No data assigned.")

        possibleValue = content[:expectedValue]
        self._logger.debug("Possible value of relation field: {0}".
                           format(possibleValue))

        expectedValue = self.computeExpectedValue(parsingPath)
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
        self._logger.debug("RELATION LEARN")
        if parsingPath is None:
            raise Exception("VariableParserPath cannot be None")
        return []

    @typeCheck(ParsingPath)
    def domainCMP(self, parsingPath, acceptCallBack=True, carnivorous=False):
        """This method participates in the abstraction process.

        It creates a VariableSpecializerResult in the provided path if
        the remainingData (or some if it) follows the type definition"""

        results = []
        self._logger.debug(
            "domainCMP executed on {0} by a relation domain".format(
                parsingPath))

        if isinstance(self.dataType, Integer):
            expectedSize = self.dataType.unitSize
        else:
            minValue, maxValue = self.dataType.size
            if minValue != maxValue:
                raise Exception(
                    "Impossible to abstract messages if a size field has a dynamic size"
                )
            expectedSize = maxValue

        content = parsingPath.getDataAssignedToVariable(self)
        if content is None:
            raise Exception("No data assigned.")

        possibleValue = content[:expectedSize]

        expectedValue = None
        try:
            expectedValue = self.computeExpectedValue(parsingPath)
            if possibleValue[:len(expectedValue)] == expectedValue:
                self._logger.debug("Callback executed with success")
                parsingPath.addResult(self, expectedValue.copy())
                results.append(parsingPath)
            else:
                self._logger.debug("Executed callback has failed.")
        except Exception as e:
            self._logger.debug("The expected value cannot be computed. Reason: '{}'".format(e))
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
    def computeExpectedValue(self, parsingPath):
        self._logger.debug(
            "compute expected value for relation field")

        # first checks the pointed fields all have a value
        hasValue = True
        errorMessage = ""
        for field in self.fieldDependencies:
            if field.domain is not self and not parsingPath.isDataAvailableForVariable(field.domain):
                errorMessage = "The following field domain has no value: '{0}'".format(field.domain)
                self._logger.debug(errorMessage)
                hasValue = False

        if not hasValue:
            raise Exception(
                "Expected value cannot be computed, some dependencies are missing for domain {0}. Error: '{}'".
                format(self, errorMessage))

        fieldValues = []
        for field in self.fieldDependencies:
            if field.domain is self:
                #fieldValue = self.dataType.generate()
                fieldSize = random.randint(field.domain.dataType.size[0], field.domain.dataType.size[1])
                fieldValue = TypeConverter.convert(b"\x00" * int(fieldSize / 8), Raw, BitArray)
            else:
                fieldValue = parsingPath.getDataAssignedToVariable(field.domain)

            if fieldValue is None:
                raise Exception("Cannot generate value for field: '{}'".format(field.name))

            if fieldValue.tobytes() == TypeConverter.convert("PENDING VALUE", String, BitArray).tobytes():
                # Handle case where field value is not currently known.
                raise Exception("Target field '{}' has a pending value".format(field.name))
            else:
                fieldValues.append(fieldValue)

        # Aggregate all field value in a uniq bitarray object
        concatFieldValues = bitarray('')
        for f in fieldValues:
            concatFieldValues += f

        # Compute the relation result
        result = self.relationOperation(concatFieldValues)

        self._logger.debug("Computed value for relation field: '{}'".format(result))
        return result

    @typeCheck(SpecializingPath)
    def regenerate(self, variableSpecializerPath, moreCallBackAccepted=True):
        """This method participates in the specialization proces.

        It creates a VariableSpecializerResult in the provided path that
        contains a generated value that follows the definition of the Data
        """
        self._logger.debug("Regenerate relation domain {0}".format(self))
        if variableSpecializerPath is None:
            raise Exception("VariableSpecializerPath cannot be None")

        try:
            newValue = self.computeExpectedValue(variableSpecializerPath)
            variableSpecializerPath.addResult(self, newValue.copy())
        except Exception as e:
            self._logger.debug(
                "Cannot specialize since no value is available for the relation dependencies, we create a callback function in case it can be computed later: {0}".
                format(e))
            pendingValue = TypeConverter.convert("PENDING VALUE", String,
                                                 BitArray)
            variableSpecializerPath.addResult(self, pendingValue)

            if moreCallBackAccepted:
                #                for field in self.fields:
                variableSpecializerPath.registerFieldCallBack(
                    self.fieldDependencies, self, parsingCB=False)
            else:
                raise e

        return [variableSpecializerPath]

    @abc.abstractmethod
    def relationOperation(self, data):
        """Compute the relation result."""
        raise NotImplementedError("Method relationOperation() has to be implemented in sub-classes")

    @property
    def fieldDependencies(self):
        """A list of fields that are required before computing the value of this relation

        :type: a list of :class:`AbstractField <netzob.Model.Vocabulary.AbstractField.AbstractField>`
        """
        return self.__fieldDependencies

    @fieldDependencies.setter
    @typeCheck(list)
    def fieldDependencies(self, fields):
        if fields is None:
            fields = []
        for field in fields:
            if not isinstance(field, AbstractField):
                raise TypeError("At least one specified field is not a Field.")
        self.__fieldDependencies = []
        for f in fields:
            self.__fieldDependencies.extend(f.getLeafFields())

    @property
    def dataType(self):
        """The datatype used to encode the result of the computed relation field.

        :type: :class:`AbstractType <netzob.Model.Vocabulary.Types.AbstractType.AbstractType>`
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
                "The datatype of a relation field must declare its length")
        self.__dataType = dataType
