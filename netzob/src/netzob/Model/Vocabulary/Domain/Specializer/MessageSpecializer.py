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
# |             ANSSI,   https://www.ssi.gouv.fr                              |
# +---------------------------------------------------------------------------+

# +---------------------------------------------------------------------------+
# | File contributors :                                                       |
# |       - Georges Bossert <georges.bossert (a) supelec.fr>                  |
# |       - Frédéric Guihéry <frederic.guihery (a) amossys.fr>                |
# +---------------------------------------------------------------------------+

# +---------------------------------------------------------------------------+
# | Standard library imports                                                  |
# +---------------------------------------------------------------------------+
from bitarray import bitarray

# +---------------------------------------------------------------------------+
# | Related third party imports                                               |
# +---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger
from netzob.Model.Vocabulary.Domain.Variables.Memory import Memory
from netzob.Model.Vocabulary.Domain.Variables.Leafs.AbstractRelationVariableLeaf import AbstractRelationVariableLeaf
from netzob.Model.Vocabulary.Symbol import Symbol
from netzob.Model.Vocabulary.Domain.Specializer.FieldSpecializer import FieldSpecializer
from netzob.Model.Vocabulary.Domain.Specializer.SpecializingPath import SpecializingPath
from netzob.Model.Vocabulary.Types.AbstractType import AbstractType
from netzob.Model.Vocabulary.Types.TypeConverter import TypeConverter
from netzob.Model.Vocabulary.Types.BitArray import BitArray
from netzob.Model.Vocabulary.Types.String import String
from netzob.Model.Vocabulary.Field import Field


@NetzobLogger
class MessageSpecializer(object):
    """
    >>> from netzob.all import *
    >>> from netzob.Model.Vocabulary.Types.TypeConverter import TypeConverter

    >>> f0 = Field("TOTO")
    >>> f1 = Field()
    >>> f2 = Field(Raw(nbBytes=(2, 100)))
    >>> f1.domain = Size(f2)
    >>> f3 = Field(String(';'))
    >>> f4 = Field(Value(f2))
    >>> s = Symbol(fields=[f0, f1, f2, f3, f4])
    >>> msgs = [RawMessage(s.specialize()) for i in range(1)]
    >>> s.messages = msgs
    >>> s.addEncodingFunction(TypeEncodingFunction(HexaString))
    >>> valueInTab = s.getCells()[0]
    >>> print(valueInTab[0])
    b'544f544f'
    >>> size = valueInTab[1]
    >>> int(size, 16)*2 == len(valueInTab[2])
    True
    >>> valueInTab[2] == valueInTab[4]
    True

    >>> f11 = Field(domain=String("hello"), name="F11")
    >>> f12 = Field(domain=String(";"), name="F12")
    >>> f13 = Field(domain=String(nbChars=(5,10)), name="F13")
    >>> s1 = Symbol(fields=[f11, f12, f13], name="S1")

    >>> f21 = Field(domain=String("master"), name="F21")
    >>> f22 = Field(domain=String(">"), name="F22")
    >>> f23 = Field(domain=Value(f13), name="F23")
    >>> s2 = Symbol(fields=[f21, f22, f23])

    >>> ms = MessageSpecializer(memory=Memory())
    >>> m1 = TypeConverter.convert(next(ms.specializeSymbol(s1)).generatedContent, BitArray, String)
    >>> m1.startswith("hello;")
    True

    >>> m2 = TypeConverter.convert(next(ms.specializeSymbol(s2)).generatedContent, BitArray, String)
    >>> m2.startswith("master>")
    True

    >>> m1[6:] == m2[7:]
    True

    """

    def __init__(self, memory=None, presets=None, fuzz=None):
        self.memory = memory
        self.presets = presets
        self.fuzz = fuzz

    def specializeSymbol(self, symbol):
        """This method generates a message based on the provided symbol definition.

        >>> from netzob.all import *
        >>> f0 = Field(name="Type", domain=Raw(b"\x01"))
        >>> f2 = Field(name="Value", domain=Raw(nbBytes=10))
        >>> f1 = Field(name="Length", domain = Size(f2, dataType = Raw(nbBytes=3, unitSize = UnitSize.SIZE_32)))
        >>> s = Symbol(fields = [f0, f1, f2])
        >>> generated_data = TypeConverter.convert(next(MessageSpecializer().specializeSymbol(s)).generatedContent, BitArray, Raw)
        >>> len(generated_data) > 4
        True

        # we can use presets to arbitrary fix the value of one field
        >>> presets = { "Value": "hello" }
        >>> TypeConverter.convert(next(MessageSpecializer(presets = presets).specializeSymbol(s)).generatedContent, BitArray, Raw)
        b'\\x01\\x00\\x00\\x05hello'

        """
        if symbol is None:
            raise Exception("Specified symbol is None")

        self._logger.debug("Specifies symbol '{0}'.".format(symbol.name))

        # Normalize presets definition: fields described with field
        # name are converted into field object, and preseting values
        # are converted into bitarray.
        self._normalize_presets(symbol)

        # Remove preset fields when they are concerned with fuzzing
        self._filterPresetsWithFuzz(symbol)

        # This variable host all the specialization paths
        specializingPaths = [SpecializingPath(memory=self.memory)]

        # First, we normalize the variables
        for field in symbol.getLeafFields(includePseudoFields=True):
            if field.domain is not None and isinstance(field.domain, AbstractRelationVariableLeaf):
                self._logger.debug("Normalize field targets for field '{}'".format(field.name))
                field.domain.normalize_targets()

        # Second, we specialize the fields for which we have parameterized values (presets)
        for field in symbol.fields:

            fieldDomain = field.domain
            if fieldDomain is None:
                raise Exception(
                    "Cannot specialize field '{0}' since it defines no domain".
                    format(fieldDomain))

            if self.presets is not None and field in self.presets.keys():
                self._logger.debug("Specializing field {0} with preset value".format(field.name))

                for specializingPath in specializingPaths:
                    specializingPath.addResult(field.domain, self.presets[field])

        # Convert list into generator
        new_paths = (new_path for new_path in specializingPaths)

        # Iterate over each possibility of specialization
        i_current_field = 0
        return self._inner_specialize(new_paths, symbol.fields, i_current_field, symbol)

    def _inner_specialize(self, paths, fields, i_current_field, symbol):

        self._logger.debug("Specializing field: '{}'".format(fields[i_current_field]))

        field = fields[i_current_field]
        fieldDomain = field.domain

        if self.presets is not None and field in self.presets.keys():
            if i_current_field < len(fields) - 1:
                self._logger.debug("More fields remaining")
                yield from self._inner_specialize(paths, fields, i_current_field + 1, symbol)
            else:
                self._logger.debug("In last field")
                for path in paths:
                    self._produce_data(path, symbol)
                    yield path
        else:

            fs = FieldSpecializer(field, presets=self.presets, fuzz=self.fuzz)

            for specializingPath in paths:
                new_paths = fs.specialize(specializingPath)

                if i_current_field < len(fields) - 1:
                    self._logger.debug("More fields remaining")
                    yield from self._inner_specialize(new_paths, fields, i_current_field + 1, symbol)
                else:
                    self._logger.debug("In last field")
                    for idx, path in enumerate(new_paths):
                        if idx == 0:  # Do not produce when itering new_paths, as the generatedContent has already been set
                            self._produce_data(path, symbol)
                        yield path

    def _produce_data(self, retainedPath, symbol):
        first_pass = True  # Tells if the retained path has already a generated content

        # let's configure the generated content

        for field in symbol.fields:

            # do no produce content if it is a pseudo field
            if field.isPseudoField is True:
                continue

            if len(field.fields) == 0:
                if first_pass:
                    first_pass = False
                    retainedPath.generatedContent = retainedPath.getData(field.domain)
                else:
                    retainedPath.generatedContent += retainedPath.getData(field.domain)
            else:
                for child in field.fields:

                    # do no produce content if it is a pseudo field
                    if child.isPseudoField is True:
                        continue

                    if first_pass:
                        first_pass = False
                        retainedPath.generatedContent = retainedPath.getData(child.domain).copy()
                    else:
                        retainedPath.generatedContent += retainedPath.getData(child.domain).copy()

        # Only make persistent the memory if it has one at the start
        if self.memory is not None:
            self.memory = retainedPath.memory

    @property
    def memory(self):
        """Memory used while specializing current symbol.

        :type: :class:`Memory <netzob.Model.Vocabulary.Domain.Variables.Memory.Memory>`
        :raises: :class:`TypeError`, :class:`ValueError`
        """
        return self.__memory

    @memory.setter  # type: ignore
    @typeCheck(Memory)
    def memory(self, memory):
        self.__memory = memory

    @property
    def presets(self):
        """A dictionnary that maps arbitrary values some of the specified fields
        should take on specialization.

        :type: :class:`dict`
        :raises: :class:`TypeError`, :class:`ValueError`
        """

        return self.__presets

    @presets.setter  # type: ignore
    def presets(self, presets):
        if presets is None:
            presets = dict()

        for k, v in presets.items():
            if not isinstance(k, (Field, str)):
                raise Exception("Preset's keys must be of Field or string types")

        self.__presets = dict()

        for k, v in presets.items():
            self.__presets[k] = v

    @typeCheck(Symbol)
    def _normalize_presets(self, symbol):
        """Update the presets dict, according to the symbol definition.

        Fields described with field name are converted into field
        object, and preseting values are converted into bitarray.

        """

        if self.presets is None:
            return

        new_keys = {}
        old_keys = []
        for k, v in self.presets.items():

            # Handle case where k is a Field
            if isinstance(k, Field):
                if isinstance(v, bitarray):
                    continue
                elif hasattr(k.domain, "dataType"):
                    if isinstance(v, AbstractType):
                        self.presets[k] = v.value
                    else:  # v should be basic python type, such as an int, str, ...
                        self.presets[k] = TypeConverter.convert(v, k.domain.dataType.__class__, BitArray,
                                                                src_unitSize=k.domain.dataType.unitSize,
                                                                dst_unitSize=k.domain.dataType.unitSize,
                                                                src_sign=k.domain.dataType.sign,
                                                                dst_sign=k.domain.dataType.sign,
                                                                src_endianness=k.domain.dataType.endianness,
                                                                dst_endianness=k.domain.dataType.endianness)
                else:
                    raise Exception("Cannot find the default dataType for field '{}'".format(k))

            # Handle case where k is a string
            elif isinstance(k, str):

                # Retrieve associated Field based on its string name
                for f in symbol.getLeafFields(includePseudoFields=True):
                    if f.name == k:
                        if isinstance(v, bitarray):
                            new_keys[f] = v
                            old_keys.append(k)
                        elif isinstance(v, bytes):
                            valbits = bitarray(endian='big')
                            valbits.frombytes(v)
                            new_keys[f] = valbits
                            old_keys.append(k)
                        elif hasattr(f.domain, "dataType"):
                            if isinstance(v, AbstractType):
                                new_keys[f] = v.value
                            else:  # v should be basic python type, such as an int, str, ...
                                new_keys[f] = TypeConverter.convert(v, f.domain.dataType.__class__, BitArray,
                                                                    src_unitSize=f.domain.dataType.unitSize,
                                                                    dst_unitSize=f.domain.dataType.unitSize,
                                                                    src_sign=f.domain.dataType.sign,
                                                                    dst_sign=f.domain.dataType.sign,
                                                                    src_endianness=f.domain.dataType.endianness,
                                                                    dst_endianness=f.domain.dataType.endianness)
                            old_keys.append(k)
                        else:
                            raise Exception("Cannot find the default dataType for field '{}'".format(f))
                        break
            else:
                raise Exception("Preset's keys must be of Field or string types")

        # Replace string keys by their equivalent Field keys
        for old_key in old_keys:
            self.presets.pop(old_key)
        self.presets.update(new_keys)

    @typeCheck(Symbol)
    def _filterPresetsWithFuzz(self, symbol):
        """Remove preset fields when they are concerned with fuzzing,
        because mutation has priority over preseting values.

        """

        if self.presets is None:
            return

        if self.fuzz is None:
            return

        for (fuzz_k, fuzz_v) in self.fuzz.mappingFieldsMutators.items():
            if fuzz_k in self.presets.keys():
                self._logger.debug("Removing preset key '{0}' in self.presets as it is already used in self.fuzz.".format(fuzz_k))
                self.presets.pop(fuzz_k)
