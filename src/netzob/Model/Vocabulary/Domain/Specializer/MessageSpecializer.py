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

# +---------------------------------------------------------------------------+
# | Related third party imports                                               |
# +---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger
from netzob.Model.Vocabulary.Domain.Variables.Memory import Memory
from netzob.Model.Vocabulary.Domain.Variables.Leafs.AbstractRelationVariableLeaf import AbstractRelationVariableLeaf
from netzob.Model.Vocabulary.Domain.Specializer.FieldSpecializer import FieldSpecializer
from netzob.Model.Vocabulary.Domain.Specializer.SpecializingPath import SpecializingPath
from netzob.Fuzzing.Mutators.DomainMutator import FuzzingMode


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
    >>> msgs = [RawMessage(next(s.specialize())) for i in range(1)]
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
    >>> f13 = Field(domain=Data(String(nbChars=(5,10)), scope=Scope.MESSAGE), name="F13")
    >>> s1 = Symbol(fields=[f11, f12, f13], name="S1")

    >>> f21 = Field(domain=String("master"), name="F21")
    >>> f22 = Field(domain=String(">"), name="F22")
    >>> f23 = Field(domain=Value(f13), name="F23")
    >>> s2 = Symbol(fields=[f21, f22, f23])

    >>> ms = MessageSpecializer(memory=Memory())
    >>> m1 = TypeConverter.convert(next(ms.specializeSymbol(s1)).generatedContent, BitArray, String)
    >>> m1.startswith(b"hello;")
    True

    >>> m2 = TypeConverter.convert(next(ms.specializeSymbol(s2)).generatedContent, BitArray, String)
    >>> m2.startswith(b"master>")
    True

    >>> m1[6:] == m2[7:]
    True

    """

    def __init__(self, memory=None, preset=None):
        self.memory = memory
        self.preset = preset

    def specializeSymbol(self, symbol):
        r"""This method generates a message based on the provided symbol definition.

        >>> from netzob.all import *
        >>> from netzob.Model.Vocabulary.Types.TypeConverter import TypeConverter
        >>> f0 = Field(name="Type", domain=Raw(b"\x01"))
        >>> f2 = Field(name="Value", domain=Raw(nbBytes=10))
        >>> f1 = Field(name="Length", domain = Size(f2, dataType = Raw(nbBytes=3, unitSize = UnitSize.SIZE_32)))
        >>> s = Symbol(fields = [f0, f1, f2])
        >>> generated_data = next(s.specialize())
        >>> len(generated_data) > 4
        True

        # we can use fix the value of one field through the preset object
        >>> preset = Preset(s)
        >>> preset["Value"] = b"hello"
        >>> next(s.specialize(preset))
        b'\x01\x00\x00\x05hello'

        """
        if symbol is None:
            raise Exception("Specified symbol is None")

        self._logger.debug("Specifies symbol '{0}'.".format(symbol.name))

        # This variable host all the specialization paths
        specializingPaths = [SpecializingPath(memory=self.memory)]

        # First, we normalize the targets of relantionship variables
        for field in symbol.getLeafFields(includePseudoFields=True):
            if field.domain is not None and isinstance(field.domain, AbstractRelationVariableLeaf):
                self._logger.debug("Normalize field targets for field '{}'".format(field.name))
                field.domain.normalize_targets()

        # Convert list into generator
        new_paths = (new_path for new_path in specializingPaths)

        # Iterate over each possibility of specialization
        i_current_field = 0
        return self._inner_specialize(new_paths, symbol.fields, i_current_field, symbol)

    def _inner_specialize(self, paths, fields, i_current_field, symbol):

        self._logger.debug("Specializing field: '{}'".format(fields[i_current_field]))

        field = fields[i_current_field]

        fs = FieldSpecializer(field, preset=self.preset)

        for specializingPath in paths:
            new_paths = fs.specialize(specializingPath)

            if i_current_field < len(fields) - 1:
                self._logger.debug("More fields remaining")
                yield from self._inner_specialize(new_paths, fields, i_current_field + 1, symbol)
            else:
                self._logger.debug("In last field")
                for idx, path in enumerate(new_paths):
                    if field.domain.isnode() or i_current_field > 0:
                        self._produce_data(path, symbol)
                    else:
                        # In mutate mode, do not produce when
                        # itering new_paths, as the
                        # generatedContent has already been set
                        # (only works when symbol has one field
                        # and the field domain is a leaf)
                        if idx > 0 and self.preset is not None and self.preset.get(field.domain) is not None and self.preset.get(field.domain).mode == FuzzingMode.MUTATE:
                            pass
                        else:
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
                    retainedPath.generatedContent = retainedPath.getData(field.domain).copy()
                else:
                    retainedPath.generatedContent += retainedPath.getData(field.domain).copy()
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
    def preset(self):
        return self.__preset

    @preset.setter  # type: ignore
    def preset(self, preset):
        self.__preset = preset
