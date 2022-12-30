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

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+
from bitarray import bitarray

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger, public_api
from netzob.Model.Vocabulary.Domain.Variables.Leafs.AbstractVariableLeaf import AbstractVariableLeaf
from netzob.Model.Vocabulary.Domain.Variables.Leafs.AbstractRelationVariableLeaf import AbstractRelationVariableLeaf, RelationDependencyException
from netzob.Model.Vocabulary.Domain.Variables.Nodes.AbstractVariableNode import AbstractVariableNode
from netzob.Model.Vocabulary.Domain.Variables.Nodes.Agg import Agg
from netzob.Model.Vocabulary.Types.AbstractType import AbstractType
from netzob.Model.Vocabulary.Domain.GenericPath import GenericPath


@NetzobLogger
class Padding(AbstractRelationVariableLeaf):
    r"""The Padding class is a variable whose content makes it possible to produce a
    padding value that can be used to align a structure to a fixed
    size.

    The Padding constructor expects some parameters:

    :param targets: The targeted objects of the relationship. If a :class:`~netzob.Model.Vocabulary.Field.Field` is provided, it will be normalized by the associated :class:`Variable <netzob.Model.Vocabulary.Domain.Variables.AbstractVariable.AbstractVariable>`.
    :param data: Specify that the produced value should be represented
                 according to this data. A callback function,
                 returning the padding value, can be used here.
    :param modulo: Specify the expected modulo size. The padding value
                   will be computed so that the whole structure aligns
                   to this value. This typically corresponds to a
                   block size in cryptography.
    :param once: If True, the padding is applied only if the total size of the
                 targeted fields is smaller than the modulo value.
                 Default value is ``False``.
    :param factor: Specify that the length of the targeted structure (always
                   expressed in bits) should be
                   multiplied by this factor. The default value is ``1.0``.
                   For example, to express a length in bytes, the factor should
                   be ``1.0/8``, whereas to express a length in bits, the
                   factor should be ``1.0``.
    :param offset: Specify a value in bits that should be added to the length
                   of the targeted structure (after applying the factor
                   parameter). The default value is 0.
    :param name: The name of the variable. If None, the name
                 will be generated.
    :type targets: a :class:`~netzob.Model.Vocabulary.Field` or a :class:`Variable <netzob.Model.Vocabulary.Domain.Variables.AbstractVariable.AbstractVariable>` or a :class:`list` of :class:`~netzob.Model.Vocabulary.Field` or :class:`Variable <netzob.Model.Vocabulary.Domain.Variables.AbstractVariable.AbstractVariable>`, required
    :type data: a :class:`~netzob.Model.Vocabulary.Types.AbstractType.AbstractType`
                or a :class:`Callable <collections.abc.Callable>`, required
    :type modulo: :class:`int`, required
    :type once: :class:`bool`, optional
    :type factor: :class:`float`, optional
    :type offset: :class:`int`, optional
    :type name: :class:`str`, optional


    The Padding class provides the following public variables:

    :var targets: The list of variables that are required before computing
                   the value of this relation
    :var dataType: The type of the data.
    :var factor: Defines the multiplication factor to apply to the targeted
                 length.
    :var offset: Defines the offset to apply to the computed length.
    :vartype dataType: :class:`~netzob.Model.Vocabulary.Types.AbstractType.AbstractType`
    :vartype factor: :class:`float`
    :vartype offset: :class:`int`
    :vartype targets: a list of
                      :class:`Variable <netzob.Model.Vocabulary.Domain.Variables.AbstractVariable.AbstractVariable>`


    **Callback prototype**

    The callback function that can be used in the ``data``
    parameter to specify the padding value has the following prototype:

    .. function:: cbk_data(current_length, modulo)
       :noindex:

       :param current_length: corresponds to the current size in bits of
                              the targeted structure.
       :type current_length: :class:`int`

       :param modulo: corresponds to the expected modulo size in bits.
       :type modulo: :class:`int`

       :return: The callback function should return a :class:`bitarray <bitarray.bitarray>`.
       :rtype: :class:`bitarray <bitarray.bitarray>`


    **Padding examples**

    The following code illustrates a padding with a modulo integer.
    Here, the padding data ``b'\x00'`` is repeated ``n``
    times, where ``n`` is computed by decrementing the modulo number,
    ``128``, by the current length of the targeted structure. The
    padding length is therefore equal to ``128 - (10+2)*8 = 32`` bits.

    >>> from netzob.all import *
    >>> f0 = Field(Raw(nbBytes=10))
    >>> f1 = Field(Raw(b"##"))
    >>> f2 = Field(Padding([f0, f1], data=Raw(b'\x00'), modulo=128))
    >>> f = Field([f0, f1, f2])
    >>> d = next(f.specialize())
    >>> d[12:]
    b'\x00\x00\x00\x00'
    >>> len(d) * 8
    128

    The following code illustrates a padding with the use of the
    ``offset`` parameter, where the targeted field sizes are decremented by
    8 when computing the padding value length.

    >>> from netzob.all import *
    >>> f0 = Field(Raw(nbBytes=10))
    >>> f1 = Field(Raw(b"##"))
    >>> f2 = Field(Padding([f0, f1], data=Raw(b'\x00'), modulo=128, offset=8))
    >>> f = Field([f0, f1, f2])
    >>> d = next(f.specialize())
    >>> d[12:]
    b'\x00\x00\x00'
    >>> len(d) * 8
    120

    The following code illustrates a padding with the use of the
    ``factor`` parameter, where the targeted field sizes are multiplied by ``1.0/2``
    before computing the padding value length.

    >>> from netzob.all import *
    >>> f0 = Field(Raw(nbBytes=10))
    >>> f1 = Field(Raw(b"##"))
    >>> f2 = Field(Padding([f0, f1], data=Raw(b'\x00'), modulo=128, factor=1./2))
    >>> f = Field([f0, f1, f2])
    >>> d = next(f.specialize())
    >>> d[12:]
    b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    >>> len(d) * 8
    256

    The following code illustrates a padding with the use of a
    callback function that helps to determine the padding value. In
    this example, the padding value is an incrementing integer.

    >>> from netzob.all import *
    >>> f0 = Field(Raw(nbBytes=10))
    >>> f1 = Field(Raw(b"##"))
    >>> def cbk_data(current_length, modulo):
    ...     length_to_pad = modulo - (current_length % modulo)  # Length in bits
    ...     length_to_pad = int(length_to_pad / 8)  # Length in bytes
    ...     res_bytes = b"".join([t.to_bytes(1, byteorder='big') for t in list(range(length_to_pad))])
    ...     res_bits = bitarray()
    ...     res_bits.frombytes(res_bytes)
    ...     return res_bits
    >>> f2 = Field(Padding([f0, f1], data=cbk_data, modulo=128))
    >>> f = Field([f0, f1, f2])
    >>> d = next(f.specialize())
    >>> d[12:]
    b'\x00\x01\x02\x03'
    >>> len(d) * 8
    128

    The following code illustrates a padding with the use of a
    callback function that helps to determine the padding value. In
    this example, the padding value is a repetition of an incrementing
    integer, thus implementing the PKCS #7 padding.

    >>> from netzob.all import *
    >>> f0 = Field(Raw(nbBytes=10))
    >>> f1 = Field(Raw(b"##"))
    >>> def cbk_data(current_length, modulo):
    ...     length_to_pad = modulo - (current_length % modulo)  # Length in bits
    ...     length_to_pad = int(length_to_pad / 8)  # Length in bytes
    ...     res_bytes = b"".join([int(length_to_pad).to_bytes(1, byteorder='big') * length_to_pad])
    ...     res_bits = bitarray()
    ...     res_bits.frombytes(res_bytes)
    ...     return res_bits
    >>> f2 = Field(Padding([f0, f1], data=cbk_data, modulo=128))
    >>> f = Field([f0, f1, f2])
    >>> d = next(f.specialize())
    >>> d[12:]
    b'\x04\x04\x04\x04'
    >>> len(d) * 8
    128

    """

    @public_api
    def __init__(self,
                 targets,
                 data,
                 modulo,
                 once=False,
                 factor=1.,
                 offset=0,
                 name=None):
        super(Padding, self).__init__(self.__class__.__name__, targets=targets, name=name)
        self.modulo = modulo
        self.once = once
        self.factor = factor
        self.offset = offset

        # Internal variable used to store current value of length to pad for further usage in self.compareValue()
        self._current_length_to_pad = 0

        # Internal variable used to tell if the padding is random (if so, parsing will be less constrained)
        self._is_padding_random = True

        # Handle the data parameter which can be a dataType or a method that return the padding data
        if callable(data):
            self.data_callback = data
        else:
            self.dataType = data
            self.data_callback = None

    @public_api
    def copy(self, map_objects=None):
        """Copy the current object as well as all its dependencies.

        :return: A new object of the same type.
        :rtype: :class:`Padding <netzob.Model.Vocabulary.Domain.Variables.Leafs.Padding.Padding>`

        """
        if map_objects is None:
            map_objects = {}
        if self in map_objects:
            return map_objects[self]

        if self.dataType is not None:
            new_data = self.dataType
        else:
            new_data = self.data_callback

        new_padding = Padding([], new_data, self.modulo, once=self.once, factor=self.factor, offset=self.offset)
        map_objects[self] = new_padding

        new_targets = []
        for target in self.targets:
            if target in map_objects.keys():
                new_targets.append(map_objects[target])
            else:
                new_target = target.copy(map_objects)
                new_targets.append(new_target)

        new_padding.targets = new_targets
        return new_padding

    def compareLength(self, content, expectedSize, computedValue, preset=None):
        return len(content[:self._current_length_to_pad]) == len(computedValue)

    def compareValues(self, content, expectedSize, computedValue):
        if self.dataType.value is None:
            return self.compareLength(content, expectedSize, computedValue)

        if content[:self._current_length_to_pad].tobytes() == computedValue.tobytes():
            msg = "The current variable data '{}' contain the expected value '{}'".format(content[:self._current_length_to_pad].tobytes(), computedValue.tobytes())
            self._logger.debug(msg)
            return True
        else:
            msg = "The current variable data '{}' does not contain the expected value '{}'".format(content[:expectedSize].tobytes(), computedValue.tobytes())
            self._logger.debug(msg)
            return False

    def __computeExpectedValue_stage1(self, targets, parsingPath, remainingVariables):
        """
        Compute the total size of targets
        """
        size = 0

        for variable in targets:

            # variable is a leaf
            if isinstance(variable, AbstractVariableLeaf):
                try:
                    size += variable.getFixedBitSize()
                except ValueError:
                    pass
                else:
                    continue

            # variable is a node
            elif isinstance(variable, AbstractVariableNode):
                if isinstance(variable, Agg):
                    size += self.__computeExpectedValue_stage1(
                        variable.children, parsingPath, remainingVariables)
                    continue

            remainingVariables.append(variable)

        return size

    def __computeExpectedValue_stage2(self, parsingPath, remainingVariables):
        """
        Compute the size of remaining variables
        """
        size = 0

        for variable in remainingVariables:

            # Retrieve variable value
            if variable is self:
                value = bitarray()
            else:
                if parsingPath.hasData(variable):
                    value = parsingPath.getData(variable)
                else:
                    error_message = "The following variable has no value: '{}' for field '{}'".format(variable, variable.field)
                    self._logger.debug(error_message)
                    raise RelationDependencyException(error_message, variable)

            if value is None:
                break

            # Retrieve length of variable value
            size += len(value)

        return size

    @typeCheck(GenericPath)
    def computeExpectedValue(self, parsingPath, preset=None):
        self._logger.debug("Compute expected value for Padding variable")

        # Reinitialize current length size
        self._current_length_to_pad = 0

        # first checks the pointed fields all have a value
        remainingVariables = []

        size = self.__computeExpectedValue_stage1(self.targets, parsingPath, remainingVariables)
        size += self.__computeExpectedValue_stage2(parsingPath, remainingVariables)
        size = int(size * self.factor + self.offset)

        # Compute the padding value according to the current size
        padding_value = bitarray()

        length_to_pad = 0
        if self.data_callback is not None:
            if callable(self.data_callback):
                data_to_extend = self.data_callback(size, self.modulo)
                length_to_pad += len(data_to_extend)
                padding_value.extend(data_to_extend)
            else:
                raise TypeError("Callback parameter is not callable.")
        else:
            # Compute length to pad
            mod = size % self.modulo
            length_to_pad = self.modulo - mod if mod > 0 else 0

            if self.once and size > self.modulo:
                length_to_pad = 0

            # Handle factor parameter
            length_to_pad = length_to_pad / self.factor

            if self.dataType.value is not None:
                self._is_padding_random = False

            # Add potential padding
            while len(padding_value) < length_to_pad:
                padding_value.extend(self.dataType.generate())

        self._logger.debug("Computed padding for {}: '{}'".format(self, padding_value.tobytes()))

        # Save current value of length to pad for further usage in self.compareValue()
        self._current_length_to_pad = int(length_to_pad)
        return padding_value

    def __str__(self):
        """The str method."""
        return "Padding({0}) - Type:{1}".format(
            str([v.name for v in self.targets]), self.dataType)

    def getFixedBitSize(self):
        self._logger.debug("Determine the deterministic size of the value of "
                           "the padding variable")
        raise ValueError("Cannot determine a deterministic size of a padding "
                         "variable")

    @property
    def dataType(self):
        """The datatype used to encode the result of the computed size.

        :type: :class:`AbstractType <netzob.Model.Vocabulary.Types.AbstractType.AbstractType>`
        """

        return self.__dataType

    @dataType.setter  # type: ignore
    @typeCheck(AbstractType)
    def dataType(self, dataType):
        if dataType is None:
            raise TypeError("Datatype cannot be None")
        size = dataType.unitSize
        if size is None:
            raise ValueError(
                "The datatype of a Size field must declare its unitSize")
        self.__dataType = dataType

    @property
    def factor(self):
        """Defines the multiplication factor to apply on the targeted length (in bits)"""
        return self.__factor

    @factor.setter  # type: ignore
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

    @offset.setter  # type: ignore
    @typeCheck((int, float))
    def offset(self, offset):
        if offset is None:
            raise TypeError(
                "Offset cannot be None, use 0 if no offset should be applied.")
        self.__offset = offset


def _test():
    r"""
    >>> from netzob.all import *

    >>> f_data = Field(Raw(nbBytes=(0, 8)), "payload")
    >>> f_size = Field(Size([f_data], dataType=uint8(), factor=1/8), "size")
    >>> f_pad = Field(Padding([f_size, f_data], data=Raw(b"\x00"), modulo=8*16), "padding")
    >>>
    >>> s = Symbol([f_size, f_data, f_pad])
    >>> data = next(s.specialize())
    >>>
    >>> structured_data = s.abstract(data)
    >>> ord(structured_data['size']) == len(structured_data['payload'])
    True
    """
