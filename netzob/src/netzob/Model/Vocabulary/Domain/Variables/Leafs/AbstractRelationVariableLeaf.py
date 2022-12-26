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
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger, public_api
from netzob.Model.Vocabulary.Domain.Variables.Leafs.AbstractVariableLeaf import AbstractVariableLeaf
from netzob.Model.Vocabulary.AbstractField import AbstractField
from netzob.Model.Vocabulary.Domain.Variables.AbstractVariable import AbstractVariable
from netzob.Model.Vocabulary.Domain.Variables.Scope import Scope
from netzob.Model.Vocabulary.Domain.GenericPath import GenericPath
from netzob.Model.Vocabulary.Domain.Parser.ParsingPath import ParsingPath
from netzob.Model.Vocabulary.Domain.Specializer.SpecializingPath import SpecializingPath
from netzob.Model.Vocabulary.Types.TypeConverter import TypeConverter
from netzob.Model.Vocabulary.Types.BitArray import BitArray
from netzob.Model.Vocabulary.Types.Raw import Raw
from netzob.Model.Vocabulary.Types.Integer import Integer
from netzob.Model.Vocabulary.Types.AbstractType import AbstractType


class RelationException(Exception):
    pass


class RelationDependencyException(Exception):
    """Exception triggered when a dependency has no value"""
    def __init__(self, error_message, current_target):
        self.error_message = error_message
        self.current_target = current_target


@public_api
class InaccessibleVariableException(Exception):
    """Exception triggered when a dependency cannot be reached"""
    def __init__(self, error_message):
        self.error_message = error_message


@NetzobLogger
class AbstractRelationVariableLeaf(AbstractVariableLeaf):
    """Represents a relation relation between variables, one being updated with the others.

    """

    def __init__(self, varType, dataType=None, targets=None, name=None):

        # Verify dataType
        if dataType is None:
            dataType = Raw(nbBytes=1)
        elif isinstance(dataType, AbstractType):
            if dataType.value is not None:
                raise Exception("Relation dataType should not have a constant value: '{}'.".format(dataType))
        else:
            raise Exception("Relation dataType has a wrong type: '{}'.".format(dataType))

        # Call super
        super(AbstractRelationVariableLeaf, self).__init__(
            varType, name, dataType=dataType, scope=Scope.NONE)

        self.targets = targets

    def __str__(self):
        """The str method."""
        return "Relation({0}) - Type:{1}".format(
            str([v.name for v in self.targets]), self.dataType)

    def count(self, preset=None):
        from netzob.Fuzzing.Mutators.DomainMutator import FuzzingMode
        if preset is not None and preset.get(self) is not None and preset.get(self).mode == FuzzingMode.GENERATE:
            # Retrieve the mutator
            mutator = preset.get(self)
            return mutator.count()
        else:
            return 1

    def normalize_targets(self):
        # Normalize targets (so that targets now only contain variables)
        new_targets = []

        if self.targets is None or self.targets == []:
            pass

        elif isinstance(self.targets, AbstractField):
            leafFields = self.targets.getLeafFields()
            if len(leafFields) > 0:
                for field in leafFields:
                    if field.domain is not None:
                        new_targets.append(field.domain)
            elif self.targets.domain is not None:
                new_targets = [self.targets.domain]

        elif isinstance(self.targets, AbstractVariable):
            new_targets = [self.targets]

        elif isinstance(self.targets, list) and len(self.targets) > 0:
            for target in self.targets:

                if isinstance(target, AbstractField):
                    leafFields = target.getLeafFields()
                    if len(leafFields) > 0:
                        for field in leafFields:
                            if field.domain is not None:
                                new_targets.append(field.domain)
                    elif target.domain is not None:
                        new_targets.append(target.domain)

                elif isinstance(target, AbstractVariable):
                    new_targets.append(target)

                else:
                    raise Exception("Targeted object '{}' sould be a Field or Variable, not a '{}'".format(repr(target), type(target)))
        else:
            raise Exception("Targeted object '{}' sould be a Field or Variable, not a '{}'".format(repr(target), type(target)))

        self.__targets = new_targets

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
        if path.memory is not None:
            return path.memory.hasValue(self)
        else:
            return False

    @typeCheck(ParsingPath)
    def valueCMP(self, parsingPath, carnivorous=False, triggered=False):
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

        content = parsingPath.getData(self)
        if content is None:
            raise Exception("No data assigned.")

        possibleValue = content[:expectedSize]
        self._logger.debug("Possible value of relation field: {0}".
                           format(possibleValue))

        expectedValue = self.computeExpectedValue(parsingPath)
        if expectedValue is None:
            # the expected value cannot be computed
            # we add a callback
            self._addCallBacksOnUndefinedVariables(parsingPath)
        else:
            if possibleValue[:len(expectedValue)] == expectedValue:
                parsingPath.addResult(self, expectedValue.copy())
            results.append(parsingPath)

    @typeCheck(ParsingPath)
    def learn(self, parsingPath, carnivours=False, triggered=False):
        raise Exception("not implemented")
        self._logger.debug("RELATION LEARN")
        if parsingPath is None:
            raise Exception("ParsingPath cannot be None")
        return []

    def compareValues(self, content, expectedSize, computedValue):
        if content[:expectedSize].tobytes() == computedValue.tobytes():
            msg = "The current variable data '{}' contain the expected value '{}'".format(content[:expectedSize].tobytes(), computedValue.tobytes())
            self._logger.debug(msg)
            return True
        else:
            msg = "The current variable data '{}' does not contain the expected value '{}'".format(content[:expectedSize].tobytes(), computedValue.tobytes())
            self._logger.debug(msg)
            return False

    @typeCheck(ParsingPath)
    def domainCMP(self, parsingPath, acceptCallBack=True, carnivorous=False, triggered=False):
        """This method participates in the abstraction process.

        It creates a result in the provided path if the remainingData
        (or some if it) follows the type definition

        """

        results = []
        self._logger.debug(
            "domainCMP executed on {0} by a relation domain".format(
                parsingPath))

        if isinstance(self.dataType, Integer):
            expectedSize = self.dataType.unitSize.value
        else:
            minValue, maxValue = self.dataType.size
            if minValue != maxValue:
                raise Exception(
                    "Impossible to abstract messages if a size field has a dynamic size"
                )
            expectedSize = maxValue

        content = parsingPath.getData(self)
        if content is None:
            raise Exception("No data assigned.")

        possibleValue = content[:expectedSize]

        expectedValue = None
        try:
            expectedValue = self.computeExpectedValue(parsingPath)
            if self.compareValues(content, expectedSize, expectedValue):
                self._logger.debug("The target variables contain the expected value '{}'".format(expectedValue.tobytes()))
                parsingPath.ok &= True
                parsingPath.addResult(self, content[:len(expectedValue)])
                results.append(parsingPath)
            else:
                raise RelationException()
        except RelationException as e:
            if triggered:
                raise RelationDependencyException("Computed result for current variable targets does not match the expected value", []) from None
            else:
                parsingPath.ok = False
        except Exception as e:
            self._logger.debug("The expected value cannot be computed. Reason: '{}'".format(e))
            if acceptCallBack:
                # we add a callback
                self._addCallBacksOnUndefinedVariables(parsingPath)
                # register the remaining data
                parsingPath.addResult(self, possibleValue.copy(), notify=False)
                results.append(parsingPath)

        return results

    @typeCheck(GenericPath)
    def _addCallBacksOnUndefinedVariables(self, parsingPath):
        """Identify each dependency field that is not yet defined and register a
        callback to try to recompute the value """

        parsingPath.registerVariablesCallBack(self.targets, self)

    @typeCheck(GenericPath)
    def computeExpectedValue(self, parsingPath, preset=None):
        self._logger.debug("Compute expected value for relation variable '{}' from field '{}'".format(self, self.field))

        # first checks the pointed variables all have a value
        hasValue = True
        current_target = None
        error_message = ""
        for variable in self.targets:
            current_target = variable
            if variable is self:
                continue
            if parsingPath.isVariableInaccessible(variable):
                error_message = "The following variable is inaccessible: '{}' for field '{}'. This may be because a parent field or variable is preset.".format(variable, variable.field)
                self._logger.debug(error_message)
                raise InaccessibleVariableException(error_message)
            if self.is_same_symbol(variable):
                if not parsingPath.hasData(variable):
                    error_message = "The following variable has no value: '{}' for field '{}'".format(variable, variable.field)
                    self._logger.debug(error_message)
                    hasValue = False
                    break
            else:
                if not parsingPath.hasDataInMemory(variable):
                    error_message = "The following variable has no value: '{}' for field '{}'".format(variable, variable.field)
                    self._logger.debug(error_message)
                    hasValue = False
                    break

        if not hasValue:
            raise RelationDependencyException(error_message, current_target)

        values = []
        for variable in self.targets:
            if variable is self:
                size = random.randint(variable.dataType.size[0], variable.dataType.size[1])
                value = TypeConverter.convert(b"\x00" * int(size / 8), Raw, BitArray)
            else:
                if self.is_same_symbol(variable):
                    value = parsingPath.getData(variable)
                else:
                    value = parsingPath.getDataInMemory(variable)

            if value is None:
                raise Exception("Cannot generate value for variable: '{}'".format(variable.name))

            values.append(value)

        # Aggregate all values in a uniq bitarray object
        concatValues = bitarray()
        for f in values:
            concatValues += f

        # Compute the relation result
        result = self.relationOperation(concatValues)

        self._logger.debug("Computed value for relation variable: '{}'".format(result.tobytes()))
        return result

    @typeCheck(SpecializingPath)
    def regenerate(self, variableSpecializerPath, moreCallBackAccepted=True, preset=None, triggered=False):
        """This method participates in the specialization proces.

        It creates a result in the provided path that contains a
        generated value that follows the definition of the Data

        """
        self._logger.debug("Regenerate relation domain '{}' for field '{}'".format(self, self.field))
        if variableSpecializerPath is None:
            raise Exception("VariableSpecializerPath cannot be None")

        try:
            newValue = self.computeExpectedValue(variableSpecializerPath, preset=preset)

            if newValue is not None:
                (addresult_succeed, addresult_newpaths) = variableSpecializerPath.addResult(self, newValue.copy())
                if addresult_succeed:
                    return addresult_newpaths
                else:
                    self._logger.debug("addResult() dit not succeed")
                    return (variableSpecializerPath,)
            else:
                raise Exception("Target value is not defined currently")
        except RelationDependencyException as e:
            self._logger.debug(
                "Value not available in the relation dependencies: {}".format(e.current_target))

            if moreCallBackAccepted:
                self._logger.debug("A callback function is created to be computed later")

                ancestor_node = self
                # parent = self.parent
                # while parent is not None:
                #     if parent.isnode():
                #         ancestor_node = parent
                #     parent = parent.parent

                self._logger.debug("Callback registered on ancestor node: '{}'".format(ancestor_node))
                self._logger.debug("Callback registered due to absence of content in target: '{}'".format(e.current_target))
                variableSpecializerPath.registerVariablesCallBack(
                    [e.current_target], ancestor_node, parsingCB=False)
            else:
                raise

            return (variableSpecializerPath, )
        except Exception as e:
            raise

    @abc.abstractmethod
    def relationOperation(self, data):
        """Compute the relation result."""
        raise NotImplementedError("Method relationOperation() has to be implemented in sub-classes")

    @property
    def targets(self):
        """A list of variables that are required before computing the value of this relation

        :type: a list of :class:`Variable <netzob.Model.Vocabulary.Domain.Variables.AbstractVariable.AbstractVariable>`
        """
        return self.__targets

    @targets.setter  # type: ignore
    def targets(self, targets):
        from netzob.Model.Vocabulary.Field import Field

        if isinstance(targets, (Field, AbstractVariable)):
            targets = [targets]
        self.__targets = targets
