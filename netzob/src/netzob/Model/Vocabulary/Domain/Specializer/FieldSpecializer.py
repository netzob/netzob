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
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger
from netzob.Model.Vocabulary.Domain.Specializer.VariableSpecializer import VariableSpecializer
from netzob.Model.Vocabulary.Domain.Specializer.SpecializingPath import SpecializingPath
from netzob.Model.Vocabulary.Domain.Variables.Memory import Memory


@NetzobLogger
class FieldSpecializer(object):
    """Computes the specialization of a field and its token-tree into a raw data

    Examples:

    >>> from netzob.all import *
    >>> from netzob.Model.Vocabulary.Types.TypeConverter import TypeConverter

    >>> f = Field("Hello")
    >>> fs = FieldSpecializer(f)
    >>> print(TypeConverter.convert(next(fs.specialize()).getData(f.domain), BitArray, Raw))
    b'Hello'

    >>> f = Field(String(nbChars=10))
    >>> fs = FieldSpecializer(f)
    >>> print(len(next(fs.specialize()).getData(f.domain)))
    80

    >>> f = Field(String(nbChars=(4, 10)))
    >>> fs = FieldSpecializer(f)
    >>> print(32<=len(next(fs.specialize()).getData(f.domain))<=80)
    True

    >>> d = Alt([String("john"), String("kurt")])
    >>> f = Field(d)
    >>> fs = FieldSpecializer(f)
    >>> val = set([TypeConverter.convert(next(fs.specialize()).getData(f.domain), BitArray, String) for x in range(100)])
    >>> print(sorted(val))
    [b'john', b'kurt']

    >>> d = Agg([String("hello"), String(" "), Alt([String("john"), String("kurt")])])
    >>> f = Field(d)
    >>> fs = FieldSpecializer(f)
    >>> val = set([TypeConverter.convert(next(fs.specialize()).getData(f.domain), BitArray, String) for x in range(100)])
    >>> print(sorted(val))
    [b'hello john', b'hello kurt']

    >>> fpayload = Field()
    >>> f1 = Field(String("hello "), name="f1")
    >>> f2 = Field(String("kurt!"), name="f2")
    >>> fpayload.fields = [f1, f2]
    >>> print(fpayload.str_structure())
    Field
    |--  f1
         |--   Data (String('hello '))
    |--  f2
         |--   Data (String('kurt!'))
    >>> fs = FieldSpecializer(fpayload)
    >>> result = next(fs.specialize())
    >>> TypeConverter.convert(result.getData(fpayload.domain), BitArray, String)
    b'hello kurt!'
    >>> TypeConverter.convert(result.getData(f1.domain), BitArray, String)
    b'hello '
    >>> TypeConverter.convert(result.getData(f2.domain), BitArray, String)
    b'kurt!'

    """

    def __init__(self, field, preset=None, memory=None):
        self._logger.debug("Creating a new FieldSpecializer for field '{}'".format(field))

        self.field = field
        self.preset = preset
        self.memory = memory

    def specialize(self, specializingPath=None):
        """Execute the specialize operation"""

        if specializingPath is None:
            specializingPath = SpecializingPath(memory=self.memory)

        self._logger.debug("Specialize field {0}".format(self.field.name))

        # We look at where to retrieve the data used for specializing the current field
        specializingPaths = []
        if len(self.field.fields) > 0:

            # We specialize the sub-fields if there are any
            specializingPaths = self._specializeFieldWithChildren(specializingPath, 0)

            # Convert list into generator
            specializingPaths = iter(specializingPaths)

        else:
            # Else, we specialize the current field
            specializingPaths = self._specializeField(specializingPath)

        return specializingPaths

    def _specializeFieldWithChildren(self, specializingPath, idx):

        child = self.field.fields[idx]
        fs = FieldSpecializer(child, preset=self.preset)
        paths = fs.specialize(specializingPath)

        for path in paths:

            if idx == len(self.field.fields) - 1:

                value = bitarray('')

                for f in self.field.fields:
                    # do no produce content if it is a pseudo field
                    if path.hasData(f.domain) and not f.isPseudoField:
                        value += path.getData(f.domain)

                path.addResult(self.field.domain, value)

                yield path
            else:
                yield from self._specializeFieldWithChildren(path, idx + 1)

    def _specializeField(self, specializingPath):

        # we retrieve the field definition domain
        domain = self.field.domain

        # we create a first VariableParser and uses it to parse the domain
        variableSpecializer = VariableSpecializer(domain, preset=self.preset)
        resultSpecializingPaths = variableSpecializer.specialize(specializingPath)

        return resultSpecializingPaths
