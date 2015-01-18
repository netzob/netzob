#-*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|          01001110 01100101 01110100 01111010 01101111 01100010            |
#|                                                                           |
#|               Netzob : Inferring communication protocols                  |
#+---------------------------------------------------------------------------+
#| Copyright (C) 2011-2014 Georges Bossert and Frédéric Guihéry              |
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
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| File contributors :                                                       |
#|       - Georges Bossert <georges.bossert (a) supelec.fr>                  |
#|       - Frédéric Guihéry <frederic.guihery (a) amossys.fr>                |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Standard library imports                                                  |
#+---------------------------------------------------------------------------+
import random
#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
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

        # we retrieve the field definition domain
        domain = self.field.domain

        # and check it exists
        if domain is None:
            raise Exception("No definition domain specified for field '{0}', cannnot parse the content against it.".format(self.field.name))

        # we create a first VariableParser and uses it to parse the domain
        variableSpecializer = VariableSpecializer(domain)
        resultSpecializingPaths = variableSpecializer.specialize(specializingPath)

        for resultSpecializingPath in resultSpecializingPaths:
            resultSpecializingPath.addResultToField(self.field, resultSpecializingPath.getDataAssignedToVariable(self.field.domain))

        return resultSpecializingPaths
