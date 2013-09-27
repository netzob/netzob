#-*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|          01001110 01100101 01110100 01111010 01101111 01100010            |
#|                                                                           |
#|               Netzob : Inferring communication protocols                  |
#+---------------------------------------------------------------------------+
#| Copyright (C) 2011 Georges Bossert and Frédéric Guihéry                   |
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

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import NetzobLogger
from netzob.Common.Models.Types.TypeConverter import TypeConverter
from netzob.Common.Models.Types.BitArray import BitArray
from netzob.Common.Models.Vocabulary.Functions.EncodingFunction import EncodingFunction


@NetzobLogger
class DomainEncodingFunction(EncodingFunction):
    """This encoding function applies the definition of the domain
    attached to each variable that has parsed the data to compute
    its encoding.

    Lets take a typical example of domain encoding, a field
    which domains is based on the aggregation of two other variables.

    >>> from netzob.all import *
    >>> f = Field(name="f0", domain=Agg(["There are ", Decimal(10), " solutions."]))
    >>> m = RawMessage("There are " + TypeConverter.convert(10, Decimal, Raw) + " solutions.")
    >>> s = Symbol(fields=[f], messages=[m], name="Symbol")
    >>> print s
    There are 10 solutions.

    """

    def encode(self, field, data, variablesByPos):
        # Single variable for the entire field ?
        if len(set(variablesByPos.values())) == 1:
            domain = variablesByPos[0].dataType.__class__
            return TypeConverter.convert(data, BitArray, domain)
        else:
            # First we compute ranges of variables
            ranges = []  # a list of (start, end, variable)
            lastVariable = None
            startPos = 0
            for pos in sorted(variablesByPos.keys()):
                currentVariable = variablesByPos[pos]
                if currentVariable != lastVariable:
                    endPos = pos
                    if endPos > startPos:
                        ranges.append((startPos, endPos, lastVariable))
                    startPos = pos
                lastVariable = currentVariable
            ranges.append((startPos, pos, lastVariable))

            # For each computed range, we convert the data following the type
            # of the variable used to parse them.
            result = []
            for (startPos, endPos, variable) in ranges:
                domain = variable.dataType.__class__
                result.append(str(TypeConverter.convert(data[startPos:endPos], BitArray, domain)))

            return ''.join(result)

    def priority(self):
        """Returns the priority of the current encoding filter."""
        return 100
