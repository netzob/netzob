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
from netzob.Common.Models.Vocabulary.Field import Field
from netzob.Common.Models.Vocabulary.Domain.Parser.VariableParser import VariableParser
from netzob.Common.Models.Vocabulary.Domain.Variables.AbstractVariable import AbstractVariable
from netzob.Common.Models.Vocabulary.Domain.Parser.FieldParserResult import FieldParserResult

from netzob.Common.Models.Vocabulary.Domain.Specializer.VariableSpecializer import VariableSpecializer
from netzob.Common.Models.Vocabulary.Domain.Variables.Memory import Memory


@NetzobLogger
class FieldSpecializer():
    """Computes the specialization of a field and its token-tree into a raw data

    Examples:

    >>> from netzob.all import *
    >>> f = Field("Hello")
    >>> fs = FieldSpecializer(f)
    >>> print fs.specialize()
    bitarray('0001001010100110001101100011011011110110')

    >>> f = Field(ASCII(nbChars=10))
    >>> fs = FieldSpecializer(f)
    >>> print len(fs.specialize())
    80

    >>> f = Field(ASCII(nbChars=(4, 10)))
    >>> fs = FieldSpecializer(f)
    >>> print 32<=len(fs.specialize())<=80
    True

    >>> d = Alt([ASCII("netzob"), ASCII("zoby")])
    >>> f = Field(d)
    >>> fs = FieldSpecializer(f)
    >>> val = set([TypeConverter.convert(fs.specialize(), BitArray, ASCII) for x in range(100)])
    >>> print val
    set(['netzob', 'zoby'])

    >>> d = Agg([ASCII("hello"), ASCII(" "), Alt([ASCII("netzob"), ASCII("zoby")])])
    >>> f = Field(d)
    >>> fs = FieldSpecializer(f)
    >>> val = set([TypeConverter.convert(fs.specialize(), BitArray, ASCII) for x in range(100)])
    >>> print val
    set(['hello zoby', 'hello netzob'])

    """

    def __init__(self, field, memory = None):
        self.field = field
        if memory is not None:
            self.memory = memory
        else:
            self.memory = Memory()

    def specialize(self):
        """Execute the specialize operation"""

        self._logger.debug("Specialize field {0}".format(self.field.name))

        # we retrieve the field definition domain
        domain = self.field.domain

        # and check it exists
        if domain is None:
            raise Exception("No definition domain specified for field '{0}', cannnot parse the content against it.".format(self.field.name))

        # we create a first VariableParser and uses it to parse the domain
        variableSpecializer = self.__createVariableSpecializer(domain)
        if not variableSpecializer.specialize():
            raise Exception("An error occurred while specializing variable {0}".format(domain))

        paths = variableSpecializer.variableSpecializerPaths

        if len(paths) == 0:
            raise Exception("No valid specialization path found.")

        return random.choice(paths).generatedContent


    def __createVariableSpecializer(self, domain):
        """Creates a variable specializer"""
        variableSpecializer = VariableSpecializer(domain, self.memory)
        return variableSpecializer
