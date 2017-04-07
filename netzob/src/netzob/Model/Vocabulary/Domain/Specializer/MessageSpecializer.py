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
from netzob.Model.Vocabulary.Symbol import Symbol
from netzob.Model.Vocabulary.Domain.Specializer.FieldSpecializer import FieldSpecializer
from netzob.Model.Vocabulary.Domain.Specializer.SpecializingPath import SpecializingPath
from netzob.Model.Vocabulary.Types.TypeConverter import TypeConverter
from netzob.Model.Vocabulary.Types.BitArray import BitArray
from netzob.Model.Vocabulary.Types.ASCII import ASCII
from netzob.Model.Vocabulary.Field import Field


@NetzobLogger
class MessageSpecializer(object):
    """
    >>> from netzob.all import *

    >>> f0 = Field("TOTO")
    >>> f1 = Field()
    >>> f2 = Field(Raw(nbBytes=(2, 100)))
    >>> f1.domain = Size(f2)
    >>> f3 = Field(ASCII(';'))
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

    >>> f11 = Field(domain=ASCII("hello"), name="F11")
    >>> f12 = Field(domain=ASCII(";"), name="F12")
    >>> f13 = Field(domain=ASCII(nbChars=(5,10)), name="F13")
    >>> s1 = Symbol(fields=[f11, f12, f13], name="S1")

    >>> f21 = Field(domain=ASCII("master"), name="F21")
    >>> f22 = Field(domain=ASCII(">"), name="F22")
    >>> f23 = Field(domain=Value(f13), name="F23")
    >>> s2 = Symbol(fields=[f21, f22, f23])

    >>> ms = MessageSpecializer()
    >>> m1 = TypeConverter.convert(ms.specializeSymbol(s1).generatedContent, BitArray, ASCII)
    >>> m1.startswith("hello;")
    True

    >>> m2 = TypeConverter.convert(ms.specializeSymbol(s2).generatedContent, BitArray, ASCII)
    >>> m2.startswith("master>")
    True

    >>> m1[6:] == m2[7:]
    True

    """

    def __init__(self, memory=None, presets=None):
        if memory is None:
            memory = Memory()
        self.memory = memory
        self.presets = presets

    @typeCheck(Symbol)
    def specializeSymbol(self, symbol):
        """This method generates a message based on the provided symbol definition."""
        if symbol is None:
            raise Exception("Specified symbol is None")

        self._logger.debug("Specifies symbol '{0}'.".format(symbol.name))

        self._update_presets(symbol)

        # this variable host all the specialization path
        specializingPaths = [SpecializingPath(memory=self.memory)]

        for field in symbol.fields:
            self._logger.debug("Specializing field {0}".format(field.name))

            fieldDomain = field.domain
            if fieldDomain is None:
                raise Exception(
                    "Cannot specialize field '{0}' since it defines no domain".
                    format(fieldDomain))

            fs = FieldSpecializer(field, presets=self.presets)

            newSpecializingPaths = []
            for specializingPath in specializingPaths:
                newSpecializingPaths.extend(fs.specialize(specializingPath))

            specializingPaths = newSpecializingPaths

        if len(specializingPaths) > 1:
            self._logger.info(
                "TODO: multiple valid paths found when specializing this message."
            )

        if len(specializingPaths) == 0:
            raise Exception("Cannot specialize this symbol.")

        retainedPath = specializingPaths[0]

        generatedContent = None
        # let's configure the generated content
        for field in symbol.fields:

            # do no produce content if it is a pseudo field
            if field.isPseudoField is True:
                continue

            # TODO: only support one level of children... must be improved
            if len(field.fields) > 0:
                d = None
                for child in field.fields:

                    # do no produce content if it is a pseudo field
                    if child.isPseudoField is True:
                        continue

                    if d is None:
                        d = retainedPath.getDataAssignedToVariable(
                            child.domain).copy()
                    else:
                        d += retainedPath.getDataAssignedToVariable(
                            child.domain).copy()

            else:
                d = retainedPath.getDataAssignedToVariable(field.domain)

            if generatedContent is None:
                generatedContent = d.copy()
            else:
                generatedContent += d.copy()

        retainedPath.generatedContent = generatedContent

        self._logger.debug("Specialized message: {0}".format(
            TypeConverter.convert(retainedPath.generatedContent, BitArray,
                                  ASCII)))
        self.memory = retainedPath.memory

        return retainedPath

    @property
    def memory(self):
        """Memory used while specializing current symbol.

        :type: :class:`netzob.Model.Vocabulary.Domain.Variables.Memory.Memory`
        :raises: :class:`TypeError`, :class:`ValueError`
        """
        return self.__memory

    @memory.setter
    @typeCheck(Memory)
    def memory(self, memory):
        if memory is None:
            raise ValueError("Memory cannot be None")
        self.__memory = memory

    @property
    def presets(self):
        """A dictionnary that maps arbitrary values some of the specified fields
        should take on specialization.

        :type: :class:`dict`
        :raises: :class:`TypeError`, :class:`ValueError`
        """

        return self.__presets

    @presets.setter
    def presets(self, presets):
        if presets is None:
            presets = dict()

        for k, v in list(presets.items()):
            if not isinstance(k, (Field, str)):
                raise Exception("Preset's keys must be of Field or string types")

        self.__presets = dict()

        for k, v in list(presets.items()):
            self.__presets[k] = v

    @typeCheck(Symbol)
    def _update_presets(self, symbol):
        """Update the presets dict, according to the symbol definition.

        """

        if self.presets is None:
            return

        new_keys = {}
        old_keys = []
        for k, v in list(self.presets.items()):

            # Handle case where k is a Field
            if isinstance(k, Field):
                if isinstance(v, bitarray):
                    continue
                elif hasattr(k.domain, "dataType"):
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
                        elif hasattr(f.domain, "dataType"):
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
