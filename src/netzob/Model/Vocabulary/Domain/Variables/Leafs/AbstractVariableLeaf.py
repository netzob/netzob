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
import abc
from bitarray import bitarray

# +---------------------------------------------------------------------------+
# | Related third party imports                                               |
# +---------------------------------------------------------------------------+

# +---------------------------------------------------------------------------+
# | Local application imports                                                 |
# +---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger
from netzob.Model.Vocabulary.Domain.Variables.AbstractVariable import AbstractVariable
from netzob.Model.Vocabulary.Domain.Variables.Scope import Scope
from netzob.Model.Vocabulary.Domain.Parser.ParsingPath import ParsingException
from netzob.Model.Vocabulary.Types.AbstractType import AbstractType


@NetzobLogger
class AbstractVariableLeaf(AbstractVariable):
    """Represents a leaf in the variable definition of a field.

    A leaf is a variable with no children. Most of of leaf variables
    are :class:`Data <netzob.Model.Vocabulary.Domain.Variables.Leafs.Data.Data>` variables and
    :class:`AbstractRelation <netzob.Model.Vocabulary.Domain.Variables.Leafs.Relations.AbstractRelation.AbstractRelation>`.

    """

    def __init__(self, varType, name=None, dataType=None, scope=None):
        super(AbstractVariableLeaf, self).__init__(
            varType, name=name, scope=scope)

        self.dataType = dataType

    def isnode(self):
        return False

    def count(self, preset=None):
        from netzob.Fuzzing.Mutators.DomainMutator import FuzzingMode
        if preset is not None and preset.get(self) is not None and preset.get(self).mode in [FuzzingMode.GENERATE, FuzzingMode.FIXED]:
            # Retrieve the mutator
            mutator = preset.get(self)
            return mutator.count()
        else:
            return self.dataType.count()

    def parse(self, parsingPath, acceptCallBack=True, carnivorous=False, triggered=False):
        """@toto TO BE DOCUMENTED"""

        if self.scope is None:
            raise Exception(
                "Cannot parse if the variable has no assigned Scope.")

        try:
            if self.isDefined(parsingPath):
                if self.scope == Scope.CONSTANT or self.scope == Scope.SESSION:
                    return self.valueCMP(
                        parsingPath, acceptCallBack, carnivorous=carnivorous, triggered=triggered)
                elif self.scope == Scope.MESSAGE:
                    return self.learn(
                        parsingPath, acceptCallBack, carnivorous=carnivorous, triggered=triggered)
                elif self.scope == Scope.NONE:
                    return self.domainCMP(
                        parsingPath, acceptCallBack, carnivorous=carnivorous, triggered=triggered)
            else:
                if self.scope == Scope.CONSTANT:
                    self._logger.debug(
                        "Cannot parse '{0}' as scope is CONSTANT and no value is available.".
                        format(self))
                    return []
                elif self.scope == Scope.MESSAGE or self.scope == Scope.SESSION:
                    return self.learn(
                        parsingPath, acceptCallBack, carnivorous=carnivorous, triggered=triggered)
                elif self.scope == Scope.NONE:
                    return self.domainCMP(
                        parsingPath, acceptCallBack, carnivorous=carnivorous, triggered=triggered)
        except ParsingException:
            self._logger.info("Error in parsing of variable")
            return []

        raise Exception("Not yet implemented: {0}.".format(self.scope))

    #
    # methods that must be defined to support the abstraction process
    #
    @abc.abstractmethod
    def isDefined(self, parsingPath):
        raise NotImplementedError("method isDefined is not implemented")

    @abc.abstractmethod
    def domainCMP(self, parsingPath, acceptCallBack, carnivorous):
        raise NotImplementedError("method domainCMP is not implemented")

    @abc.abstractmethod
    def valueCMP(self, parsingPath, acceptCallBack, carnivorous):
        raise NotImplementedError("method valueCMP is not implemented")

    @abc.abstractmethod
    def learn(self, parsingPath, acceptCallBack, carnivorous):
        raise NotImplementedError("method learn is not implemented")

    def getVariables(self):
        return [self]

    def specialize(self, parsingPath, preset=None, acceptCallBack=True, triggered=False):
        """Specializes a Leaf"""

        from netzob.Fuzzing.Mutator import MaxFuzzingException
        from netzob.Fuzzing.Mutators.DomainMutator import FuzzingMode
        # Fuzzing has priority over generating a legitimate value
        if preset is not None and preset.get(self) is not None and preset.get(self).mode in [FuzzingMode.GENERATE, FuzzingMode.FIXED]:

            # Retrieve the mutator
            mutator = preset.get(self)

            def fuzzing_generate():
                if preset.get(self).mode == FuzzingMode.FIXED:
                    nb_iterations = AbstractType.MAXIMUM_POSSIBLE_VALUES
                else:
                    nb_iterations = self.count(preset=preset)

                for _ in range(nb_iterations):

                    try:
                        # Mutate a value according to the current field attributes
                        generated_value = mutator.generate()
                    except MaxFuzzingException:
                        self._logger.debug("Maximum mutation counter reached")
                        break
                    else:
                        if isinstance(generated_value, bitarray):
                            value = generated_value
                        else:
                            # Convert the return bytes into bitarray
                            value = bitarray()
                            value.frombytes(generated_value)

                        # Associate the generated value to the current variable
                        newParsingPath = parsingPath.copy()
                        newParsingPath.addResult(self, value)
                        yield newParsingPath

            return fuzzing_generate()

        if self.scope is None:
            raise Exception(
                "Cannot specialize if the variable has no assigned Scope.")

        if self.isDefined(parsingPath):
            if self.scope == Scope.CONSTANT or self.scope == Scope.SESSION:
                newParsingPaths = self.use(parsingPath, acceptCallBack, preset=preset, triggered=triggered)
            elif self.scope == Scope.MESSAGE:
                newParsingPaths = self.regenerateAndMemorize(parsingPath, acceptCallBack, preset=preset, triggered=triggered)
            elif self.scope == Scope.NONE:
                newParsingPaths = self.regenerate(parsingPath, acceptCallBack, preset=preset, triggered=triggered)
        else:
            if self.scope == Scope.CONSTANT:
                self._logger.debug(
                    "Cannot specialize '{0}' as scope is CONSTANT and no value is available.".
                    format(self))
                newParsingPaths = iter(())
            elif self.scope == Scope.MESSAGE or self.scope == Scope.SESSION:
                newParsingPaths = self.regenerateAndMemorize(parsingPath, acceptCallBack, preset=preset, triggered=triggered)
            elif self.scope == Scope.NONE:
                newParsingPaths = self.regenerate(parsingPath, acceptCallBack, preset=preset, triggered=triggered)

        if preset is not None and preset.get(self) is not None and preset.get(self).mode == FuzzingMode.MUTATE:

            def fuzzing_mutate():
                for path in newParsingPaths:
                    generatedData = path.getData(self)

                    # Retrieve the mutator
                    mutator = preset.get(self)

                    while True:
                        # Mutate a value according to the current field attributes
                        mutator.mutate(generatedData)
                        yield path

            return fuzzing_mutate()
        else:
            return newParsingPaths

    def str_structure(self, preset=None, deepness=0):
        """Returns a string which denotes
        the current field definition using a tree display"""

        tab = ["     " for x in range(deepness - 1)]
        tab.append("|--   ")
        tab.append("{0}".format(self))

        # Add information regarding preset configuration
        if preset is not None and preset.get(self) is not None:
            tmp_data = " ["
            tmp_data += str(preset.get(self).mode)
            try:
                tmp_data += " ({})".format(preset[self])
            except Exception as e:
                pass
            tmp_data += "]"
            tab.append(tmp_data)

        return ''.join(tab)

    def getFixedBitSize(self):
        self._logger.debug("Determine the deterministic size of the value of "
                           "the leaf variable")

        if not hasattr(self, 'dataType'):
            return super().getFixedBitSize()

        return self.dataType.getFixedBitSize()


    ## Properties

    @property
    def dataType(self):
        """The datatype used to encode the result of the computed relation field.

        :type: :class:`AbstractType <netzob.Model.Vocabulary.Types.AbstractType.AbstractType>`
        """

        return self.__dataType

    @dataType.setter  # type: ignore
    @typeCheck(AbstractType)
    def dataType(self, dataType):
        if dataType is None:
            raise TypeError("Datatype cannot be None")
        (minSize, maxSize) = dataType.size
        if maxSize is None:
            raise ValueError(
                "The datatype of a relation field must declare its length")
        self.__dataType = dataType
