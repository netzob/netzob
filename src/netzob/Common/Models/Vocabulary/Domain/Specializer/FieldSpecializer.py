# -*- coding: utf-8 -*-

# +---------------------------------------------------------------------------+
# |          01001110 01100101 01110100 01111010 01101111 01100010            |
# |                                                                           |
# |               Netzob : Inferring communication protocols                  |
# +---------------------------------------------------------------------------+
# | Copyright (C) 2011-2014 Georges Bossert and Frédéric Guihéry              |
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

# +---------------------------------------------------------------------------+
# | Local application imports                                                 |
# +---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger
from netzob.Common.Models.Vocabulary.Domain.Specializer.VariableSpecializer import VariableSpecializer
from netzob.Common.Models.Vocabulary.Domain.Specializer.SpecializingPath import SpecializingPath
from netzob.Common.Models.Vocabulary.Domain.Variables.Memory import Memory


@NetzobLogger
class FieldSpecializer():
    """Computes the specialization of a field and its token-tree into a raw data

    Examples:

    >>> from netzob.all import *

    >>> f = Field("Hello")
    >>> fs = FieldSpecializer(f)
    >>> print TypeConverter.convert(fs.specialize()[0].getDataAssignedToField(f), BitArray, Raw)
    Hello

    >>> f = Field(ASCII(nbChars=10))
    >>> fs = FieldSpecializer(f)
    >>> print len(fs.specialize()[0].getDataAssignedToField(f))
    80

    >>> f = Field(ASCII(nbChars=(4, 10)))
    >>> fs = FieldSpecializer(f)
    >>> print 32<=len(fs.specialize()[0].getDataAssignedToField(f))<=80
    True

    >>> d = Alt([ASCII("netzob"), ASCII("zoby")])
    >>> f = Field(d)
    >>> fs = FieldSpecializer(f)
    >>> val = set([TypeConverter.convert(fs.specialize()[0].getDataAssignedToField(f), BitArray, ASCII) for x in range(100)])
    >>> print val
    set(['netzob', 'zoby'])

    >>> d = Agg([ASCII("hello"), ASCII(" "), Alt([ASCII("netzob"), ASCII("zoby")])])
    >>> f = Field(d)
    >>> fs = FieldSpecializer(f)
    >>> val = set([TypeConverter.convert(fs.specialize()[0].getDataAssignedToField(f), BitArray, ASCII) for x in range(100)])
    >>> print val
    set(['hello zoby', 'hello netzob'])

    >>> fpayload = Field()
    >>> f1 = Field(ASCII("hello "), name="f1")
    >>> f2 = Field(ASCII("zoby!"), name="f2")
    >>> fpayload.children = [f1, f2]
    >>> print fpayload._str_debug()
    Field
    |--   Data (Raw=None ((0, None)))
    |--  f1
         |--   Data (ASCII=hello  ((0, 48)))
    |--  f2
         |--   Data (ASCII=zoby! ((0, 40)))
    >>> fs = FieldSpecializer(fpayload)
    >>> result = fs.specialize()[0]
    >>> TypeConverter.convert(result.getDataAssignedToField(fpayload), BitArray, ASCII)
    'hello zoby!'
    >>> TypeConverter.convert(result.getDataAssignedToField(f1), BitArray, ASCII)
    'hello '
    >>> TypeConverter.convert(result.getDataAssignedToField(f2), BitArray, ASCII)
    'zoby!'

    """

    def __init__(self, field):
        self.field = field
        self._logger.debug("Creating a new FieldSpecializer.")

    @typeCheck(SpecializingPath)
    def specialize(self, specializingPath=None):
        """Execute the specialize operation"""

        if specializingPath is None:
            specializingPath = SpecializingPath(memory=Memory())

        self._logger.debug("Specialize field {0}".format(self.field.name))

        # does current field has children
        if len(self.field.children) > 0:
            return self._specializeFieldWithChildren(specializingPath)
        else:
            return self._specializeField(specializingPath)

    @typeCheck(SpecializingPath)
    def _specializeFieldWithChildren(self, specializingPath=None):

        if specializingPath is None:
            specializingPath = SpecializingPath(memory=Memory())

        resultPaths = [specializingPath]
        for child in self.field.children:
            fs = FieldSpecializer(child)

            tmpResultPaths = []
            for path in resultPaths:
                tmpResultPaths.extend(fs.specialize(path))
            resultPaths = tmpResultPaths

        for resultPath in resultPaths:
            value = None
            for child in self.field.children:
                childResult = resultPath.getDataAssignedToField(child)
                if value is None:
                    value = childResult.copy()
                else:
                    value += childResult.copy()
            resultPath.addResultToField(self.field, value)

        return resultPaths

    @typeCheck(SpecializingPath)
    def _specializeField(self, specializingPath=None):

        if specializingPath is None:
            specializingPath = SpecializingPath(memory=Memory())

        # we retrieve the field definition domain
        domain = self.field.domain

        # and check it exists
        if domain is None:
            raise Exception("No definition domain specified for field '{0}', cannnot parse the content against it.".format(self.field.name))

        # we create a first VariableParser and uses it to parse the domain
        variableSpecializer = VariableSpecializer(domain)
        resultSpecializingPaths = variableSpecializer.specialize(specializingPath)

        for resultSpecializingPath in resultSpecializingPaths:
            self._logger.debug("FieldSpecializer Result: {0}".format(resultSpecializingPath.getDataAssignedToVariable(self.field.domain)))
            resultSpecializingPath.addResultToField(self.field, resultSpecializingPath.getDataAssignedToVariable(self.field.domain))

        return resultSpecializingPaths
