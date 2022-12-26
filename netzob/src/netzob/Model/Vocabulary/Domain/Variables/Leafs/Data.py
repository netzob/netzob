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

# +---------------------------------------------------------------------------+
# | Local application imports                                                 |
# +---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck, public_api, NetzobLogger
from netzob.Model.Vocabulary.Domain.Variables.Leafs.AbstractVariableLeaf import AbstractVariableLeaf
from netzob.Model.Vocabulary.Types.AbstractType import AbstractType
from netzob.Model.Vocabulary.Types.BitArray import BitArray


@NetzobLogger
class Data(AbstractVariableLeaf):
    """The Data class is a variable which embeds specific content.

    A Data object stores the definition domain of a variable and the constraints
    over it, through a :class:`Type
    <netzob.Model.Vocabulary.Types.AbstractType>` object.

    The Data constructor expects some parameters:

    :param dataType: The type of the data (for example Integer,
                     Raw, String, ...).
    :param name: The name of the data (if None, the name will
                 be generated).
    :param scope: The Scope strategy defining how the Data value is
                 used during the abstraction and specialization process.
                 The default strategy is ``Scope.NONE``.
    :type dataType: :class:`~netzob.Model.Vocabulary.Types.AbstractType.AbstractType`, required
    :type name: :class:`str`, optional
    :type scope: :class:`~netzob.Model.Vocabulary.Domain.Variables.Scope.Scope`, optional


    The Data class provides the following public variables:

    :var dataType: The type of the data.
    :var name: The name of the variable (Read-only).
    :vartype dataType: :class:`~netzob.Model.Vocabulary.Types.AbstractType.AbstractType`
    :vartype name: :class:`str`


    The following example shows the definition of the Data `pseudo`
    with a String type and a `"hello"` default value. This means that
    this Data object accepts any string, and the default generated value
    of this object is `"hello"`.

    >>> from netzob.all import *
    >>> s = String(nbChars=5, default='hello')
    >>> data = Data(dataType=s, name="pseudo")
    >>> print(data.dataType)
    String(nbChars=5)
    >>> data.name
    'pseudo'
    >>> s.generate().tobytes()
    b'hello'


    """

    @public_api
    def __init__(self, dataType, name=None, scope=None):
        super(Data, self).__init__(
            self.__class__.__name__, name=name, scope=scope)

        self.dataType = dataType

    @public_api
    def copy(self, map_objects=None):
        """Copy the current object as well as all its dependencies.

        :return: A new object of the same type.
        :rtype: :class:`Data <netzob.Model.Vocabulary.Domain.Variables.Leafs.Data.Data>`

        """
        if map_objects is None:
            map_objects = {}
        if self in map_objects:
            return map_objects[self]

        new_data = Data(self.dataType, name=self.name, scope=self.scope)
        map_objects[self] = new_data
        return new_data

    def __str__(self):
        return "Data ({0})".format(self.dataType)

    def isDefined(self, path):
        """Checks if a value is available either in data's definition or in memory

        :parameter path: the current path used either to abstract and specialize this data
        :type path: :class:`GenericPath <netzob.Model.Vocabulary.Domain.GenericPath.GenericPath>`
        :return: a boolean that indicates if a value is available for this data
        :rtype: :class:`bool`
        """

        if path is None:
            raise Exception("Path cannot be None")

        # we check if memory referenced its value (memory is priority)
        if path.memory is not None and path.memory.hasValue(self):
            return True
        elif self.dataType.value is not None:
            return True
        else:
            return False

    def domainCMP(self, parsingPath, acceptCallBack=True, carnivorous=False, triggered=False):

        if parsingPath is None:
            raise Exception("ParsingPath cannot be None")

        content = parsingPath.getData(self)
        actualSize = len(content)

        self._logger.debug("Learn '{}' with {} ({})".format(content.tobytes(),
                                                            self.dataType, self.name))

        try:
            minSize = maxSize = self.getFixedBitSize()
        except ValueError:
            (minSize, maxSize) = self.dataType.size
            if minSize is None:
                minSize = 0
            if maxSize is None:
                maxSize = actualSize

        if actualSize < minSize:
            self._logger.debug(
                "Length of the content is too short ({0}), expect data of at least {1} bits".
                format(len(content), minSize))
        else:
            # Handle specific case where the parsing can be made at the bit level
            if isinstance(self.dataType, BitArray):
                step = -1
            else:
                step = -8

            for size in range(min(maxSize, len(content)), minSize - 1, step):
                self._logger.debug("Try to parse {}/{} bits for variable '{}'".format(size, min(maxSize, len(content)), self.field))
                # size == 0 : deals with 'optional' data
                if size == 0 or self.dataType.canParse(content[:size]):
                    # we create a new parsing path and returns it
                    newParsingPath = parsingPath.copy()
                    (addresult_succeed, addresult_parsingPaths) = newParsingPath.addResult(self, content[:size].copy())
                    if addresult_succeed:
                        for addresult_parsingPath in addresult_parsingPaths:
                            yield addresult_parsingPath
                    else:
                        self._logger.debug("Parsed data does not respect a relation")

    def valueCMP(self, parsingPath, acceptCallBack=True, carnivorous=False, triggered=False):
        if parsingPath is None:
            raise Exception("ParsingPath cannot be None")

        expectedValue = self.dataType.value

        # we check a value is available in memory
        if parsingPath.memory is not None and parsingPath.memory.hasValue(self):
            expectedValue = parsingPath.memory.getValue(self)

        if expectedValue is None:
            raise Exception(
                "Data '{0}' has no value defined in its definition domain".
                format(self))

        content = parsingPath.getData(self)
        if content is None:
            raise Exception("No data assigned to the variable")

        self._logger.debug("ValueCMP {} with {} ({})".format(content.tobytes(), self.dataType, self.name))

        results = []
        if len(content) >= len(expectedValue) and content[:len(
                expectedValue)].tobytes() == expectedValue.tobytes():
            (addresult_succeed, addresult_parsingPaths) = parsingPath.addResult(self, content[:len(expectedValue)].copy())
            results.extend(addresult_parsingPaths)
            self._logger.debug("Data '{}' can be parsed with variable {}, providing '{}'".format(content.tobytes(), self, content[:len(expectedValue)].tobytes()))
        else:
            self._logger.debug("Data '{}' cannot be parsed with variable {}".format(content.tobytes(), self))
        return results

    def learn(self, parsingPath, acceptCallBack=True, carnivorous=False, triggered=False):

        if parsingPath is None:
            raise Exception("ParsingPath cannot be None")

        content = parsingPath.getData(self)
        actualSize = len(content)

        self._logger.debug("Learn '{}' with {} ({})".format(content.tobytes(),
                                                            self.dataType, self.name))

        try:
            minSize = maxSize = self.getFixedBitSize()
        except ValueError:
            (minSize, maxSize) = self.dataType.size
            if minSize is None:
                minSize = 0
            if maxSize is None:
                maxSize = actualSize

        if actualSize < minSize:
            self._logger.debug(
                "Length of the content is too short ({0}), expect data of at least {1} bits".
                format(len(content), minSize))
        else:
            # Handle specific case where the parsing can be made at the bit level
            if isinstance(self.dataType, BitArray):
                step = -1
            else:
                step = -8

            for size in range(min(maxSize, len(content)), minSize - 1, step):
                self._logger.debug("Try to parse {}/{} bits for variable '{}'".format(size, min(maxSize, len(content)), self.field))
                # size == 0 : deals with 'optional' data
                if size == 0 or self.dataType.canParse(content[:size]):
                    # we create a new parsing path and returns it
                    newParsingPath = parsingPath.copy()
                    (addresult_succeed, addresult_parsingPaths) = newParsingPath.addResult(self, content[:size].copy())
                    if addresult_succeed:
                        for addresult_parsingPath in addresult_parsingPaths:
                            if addresult_parsingPath.memory is not None:
                                addresult_parsingPath.memory.memorize(self, content[:size].copy())
                            yield addresult_parsingPath
                    else:
                        self._logger.debug("Parsed data does not respect a relation")

    def use(self, variableSpecializerPath, acceptCallBack=True, preset=None, triggered=False):
        """This method participates in the specialization proces.

        It creates a result in the provided path that either contains
        the memorized value or the predefined value of the variable

        """

        while True:
            self._logger.debug("Use variable {} ({})".format(self.dataType, self.name))

            if variableSpecializerPath is None:
                raise Exception("VariableSpecializerPath cannot be None")

            if variableSpecializerPath.memory is not None and variableSpecializerPath.memory.hasValue(self):
                variableSpecializerPath.addResult(self, variableSpecializerPath.memory.getValue(self))
            elif self.dataType.value is not None:
                variableSpecializerPath.addResult(self, self.dataType.value.copy())
            else:
                raise Exception("No value has been memorized or value is not a constant")

            yield variableSpecializerPath

    def regenerate(self, variableSpecializerPath, acceptCallBack=True, preset=None, triggered=False):
        """This method participates in the specialization proces.

        It creates a result in the provided path that contains a
        generated value that follows the definition of the Data

        """

        while True:
            self._logger.debug("Regenerate variable {} ({})".format(self.dataType, self.name))

            if variableSpecializerPath is None:
                raise Exception("VariableSpecializerPath cannot be None")

            newValue = self.dataType.generate()

            self._logger.debug("Generated value for {}: {}".format(self, newValue))

            variableSpecializerPath.addResult(self, newValue)

            yield variableSpecializerPath

    def regenerateAndMemorize(self,
                              variableSpecializerPath,
                              acceptCallBack=True,
                              preset=None, triggered=False):
        """This method participates in the specialization proces.
        It memorizes the value present in the path of the variable
        """

        while True:
            self._logger.debug("Regenerate and memorize variable '{}' ({}) for field '{}'".format(self.dataType, self.name, self.field))

            if variableSpecializerPath is None:
                raise Exception("VariableSpecializerPath cannot be None")

            variableSpecializerPath = variableSpecializerPath.copy()

            if variableSpecializerPath.memory is not None and variableSpecializerPath.memory.hasValue(self):
                newValue = variableSpecializerPath.memory.getValue(self)
            else:
                newValue = self.dataType.generate()
                if variableSpecializerPath.memory is not None:
                    variableSpecializerPath.memory.memorize(self, newValue)

            self._logger.debug("Generated value for {}: {}".format(self, newValue.tobytes()))

            variableSpecializerPath.addResult(self, newValue.copy())

            yield variableSpecializerPath.copy()

    @public_api
    @property
    def dataType(self):
        """
        Property (getter.setter  # type: ignore).
        The type of the data.

        :type: :class:`AbstractType <netzob.Model.Vocabulary.Types.AbstractType>`
        """
        return self.__dataType

    @dataType.setter  # type: ignore
    @typeCheck(AbstractType)
    def dataType(self, dataType):
        self.__dataType = dataType
