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
    >>> print(TypeConverter.convert(fs.specialize()[0].getDataAssignedToVariable(f.domain), BitArray, Raw))
    b'Hello'

    >>> f = Field(String(nbChars=10))
    >>> fs = FieldSpecializer(f)
    >>> print(len(fs.specialize()[0].getDataAssignedToVariable(f.domain)))
    80

    >>> f = Field(String(nbChars=(4, 10)))
    >>> fs = FieldSpecializer(f)
    >>> print(32<=len(fs.specialize()[0].getDataAssignedToVariable(f.domain))<=80)
    True

    >>> d = Alt([String("netzob"), String("kurt")])
    >>> f = Field(d)
    >>> fs = FieldSpecializer(f)
    >>> val = set([TypeConverter.convert(fs.specialize()[0].getDataAssignedToVariable(f.domain), BitArray, String) for x in range(100)])
    >>> print(sorted(val))
    ['kurt', 'netzob']

    >>> d = Agg([String("hello"), String(" "), Alt([String("netzob"), String("kurt")])])
    >>> f = Field(d)
    >>> fs = FieldSpecializer(f)
    >>> val = set([TypeConverter.convert(fs.specialize()[0].getDataAssignedToVariable(f.domain), BitArray, String) for x in range(100)])
    >>> print(sorted(val))
    ['hello kurt', 'hello netzob']

    >>> fpayload = Field()
    >>> f1 = Field(String("hello "), name="f1")
    >>> f2 = Field(String("kurt!"), name="f2")
    >>> fpayload.fields = [f1, f2]
    >>> print(fpayload.str_structure())
    Field
    |--  f1
         |--   Data (String=hello  ((None, None)))
    |--  f2
         |--   Data (String=kurt! ((None, None)))
    >>> fs = FieldSpecializer(fpayload)
    >>> result = fs.specialize()[0]
    >>> TypeConverter.convert(result.getDataAssignedToVariable(fpayload.domain), BitArray, String)
    'hello kurt!'
    >>> TypeConverter.convert(result.getDataAssignedToVariable(f1.domain), BitArray, String)
    'hello '
    >>> TypeConverter.convert(result.getDataAssignedToVariable(f2.domain), BitArray, String)
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

    @typeCheck(SpecializingPath)
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
            #specializingPath.addResultToField(self.field, self.arbitraryValue)
            specializingPaths = [specializingPath]
        elif len(self.field.fields) > 0:
            # If no arbitrary value is specified, we specialize the sub-fields if there are any
            specializingPaths = self._specializeFieldWithChildren(specializingPath)
        else:
            # Else, we specialize the current field
            specializingPaths = self._specializeField(specializingPath)

        return specializingPaths

    @typeCheck(SpecializingPath)
    def _specializeFieldWithChildren(self, specializingPath=None):

        if specializingPath is None:
            specializingPath = SpecializingPath(memory=Memory())

        resultPaths = [specializingPath]
        for child in self.field.fields:
            fs = FieldSpecializer(child, presets=self.presets, fuzz=self.fuzz)

            tmpResultPaths = []
            for path in resultPaths:
                tmpResultPaths.extend(fs.specialize(path))
            resultPaths = tmpResultPaths

        for resultPath in resultPaths:
            value = None
            for child in self.field.fields:
                childResult = resultPath.getDataAssignedToVariable(
                    child.domain)
                if value is None:
                    value = childResult.copy()
                else:
                    value += childResult.copy()

            resultPath.addResult(self.field.domain, value)
            #resultPath.addResultToField(self.field, value)

        return resultPaths

    @typeCheck(SpecializingPath)
    def _specializeField(self, specializingPath=None):

        if specializingPath is None:
            specializingPath = SpecializingPath(memory=Memory())

        # we retrieve the field definition domain
        domain = self.field.domain

        # and check it exists
        if domain is None:
            raise Exception(
                "No definition domain specified for field '{0}', cannnot parse the content against it.".
                format(self.field.name))

        # we create a first VariableParser and uses it to parse the domain
        variableSpecializer = VariableSpecializer(domain, fuzz=self.fuzz)
        resultSpecializingPaths = variableSpecializer.specialize(specializingPath)

        for resultSpecializingPath in resultSpecializingPaths:

            assignedData = bitarray('')
            if resultSpecializingPath.isDataAvailableForVariable(self.field.domain):
                assignedData = resultSpecializingPath.getDataAssignedToVariable(self.field.domain)
            else:
                resultSpecializingPath.addResult(self.field.domain, assignedData)

            self._logger.debug(
                "FieldSpecializer Result: {0}".format(assignedData))

            resultSpecializingPath.addResult(self.field.domain, assignedData)

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

    @arbitraryValue.setter
    @typeCheck(bitarray)
    def arbitraryValue(self, value):
        self.__arbitraryValue = value
