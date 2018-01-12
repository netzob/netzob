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
from netzob.Model.Vocabulary.Types.BitArray import BitArray
from netzob.Model.Vocabulary.Types.TypeConverter import TypeConverter


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
    ['john', 'kurt']

    >>> d = Agg([String("hello"), String(" "), Alt([String("john"), String("kurt")])])
    >>> f = Field(d)
    >>> fs = FieldSpecializer(f)
    >>> val = set([TypeConverter.convert(next(fs.specialize()).getData(f.domain), BitArray, String) for x in range(100)])
    >>> print(sorted(val))
    ['hello john', 'hello kurt']

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
    'hello kurt!'
    >>> TypeConverter.convert(result.getData(f1.domain), BitArray, String)
    'hello '
    >>> TypeConverter.convert(result.getData(f2.domain), BitArray, String)
    'kurt!'

    """

    def __init__(self, field, presets=None, fuzz=None):
        self._logger.debug("Creating a new FieldSpecializer.")

        self.field = field
        self.presets = presets
        self.fuzz = fuzz

        if self.presets is not None and self.field in self.presets.keys():
            self.arbitraryValue = self.presets[self.field]
        else:
            self.arbitraryValue = None

    def specialize(self, specializingPath=None):
        """Execute the specialize operation"""

        if specializingPath is None:
            specializingPath = SpecializingPath(memory=Memory())

        self._logger.debug("Specialize field {0}".format(self.field.name))

        # We look at where to retrieve the data used for specializing the current field
        specializingPaths = []
        if self.arbitraryValue is not None:

            # In case an arbitrary value is specified, we consider it for field specialization
            specializingPath.addResult(self.field.domain, self.arbitraryValue)
            specializingPaths = [specializingPath]

            # Convert list into generator
            specializingPaths = (path for path in specializingPaths)

        elif len(self.field.fields) > 0:

            # If no arbitrary value is specified, we specialize the sub-fields if there are any
            specializingPaths = self._specializeFieldWithChildren(specializingPath, 0)

            # Convert list into generator
            specializingPaths = (path for path in specializingPaths)

        else:
            # Else, we specialize the current field
            specializingPaths = self._specializeField(specializingPath)

        return specializingPaths

    def _specializeFieldWithChildren(self, specializingPath, idx):

        child = self.field.fields[idx]
        fs = FieldSpecializer(child, presets=self.presets, fuzz=self.fuzz)
        paths = fs.specialize(specializingPath)

        for path in paths:

            if idx == len(self.field.fields) - 1:

                for f in self.field.fields:
                    # do no produce content if it is a pseudo field
                    if path.hasData(f.domain) and not f.isPseudoField:
                        value = path.getData(f.domain)
                        if path.hasData(self.field.domain):
                            value = path.getData(self.field.domain) + value
                        path.addResult(self.field.domain, value)

                yield path
            else:
                yield from self._specializeFieldWithChildren(path, idx + 1)

    def _specializeField(self, specializingPath):

        # we retrieve the field definition domain
        domain = self.field.domain

        # we create a first VariableParser and uses it to parse the domain
        variableSpecializer = VariableSpecializer(domain, fuzz=self.fuzz)
        resultSpecializingPaths = variableSpecializer.specialize(specializingPath)

        return resultSpecializingPaths

    @property
    def arbitraryValue(self):
        """Arbitrary value that must be used when specializing the current field.
        If set, no specializing process is started on the field domain, instead the provided
        value is considered.

        It should be noted that no verification is made on the arbitrary value. Thus, this value
        is not forced to follow field definitions.

        :type: a :class:`BitArray` value
        :raises: :class:`TypeError`
        """
        return self.__arbitraryValue

    @arbitraryValue.setter  # type: ignore
    @typeCheck(bitarray)
    def arbitraryValue(self, value):
        self.__arbitraryValue = value
