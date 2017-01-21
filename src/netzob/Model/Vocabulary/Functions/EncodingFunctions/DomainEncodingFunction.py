#-*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|          01001110 01100101 01110100 01111010 01101111 01100010            |
#|                                                                           |
#|               Netzob : Inferring communication protocols                  |
#+---------------------------------------------------------------------------+
#| Copyright (C) 2011-2016 Georges Bossert and Frédéric Guihéry              |
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
from netzob.Model.Types.TypeConverter import TypeConverter
from netzob.Model.Types.BitArray import BitArray
from netzob.Model.Vocabulary.Functions.EncodingFunction import EncodingFunction
from netzob.Model.Vocabulary.Domain.Variables.Nodes.Agg import Agg


@NetzobLogger
class DomainEncodingFunction(EncodingFunction):
    """This encoding function applies the definition of the domain
    attached to each variable that has parsed the data to compute
    its encoding.

    Lets take a typical example of domain encoding, a field
    which domains is based on the aggregation of two other variables.

    >>> from netzob.all import *
    >>> f = Field(name="f0", domain=Agg(["There are ", Integer(10), " solutions."]))
    >>> m = RawMessage(b"There are " + TypeConverter.convert(10, Integer, Raw) + b" solutions.")
    >>> s = Symbol(fields=[f], messages=[m], name="Symbol")
    >>> s.addEncodingFunction(TypeEncodingFunction(ASCII))
    >>> print(s)
    f0                      
    ------------------------
    'There are . solutions.'
    ------------------------
    """

    def encode(self, field, readingToken):
        if not readingToken.getValueForVariable(field.domain):
            return ''

        return self.encodeChild(field.domain, readingToken)

    def encodeChild(self, variable, readingToken):
        result = []

        if not readingToken.isValueForVariableAvailable(variable):
            return result

        if variable.varType == "Data" or variable.varType == "Size" or variable.varType == "InternetChecksum":
            val = readingToken.getValueForVariable(variable)
            encodedVal = TypeConverter.convert(val, BitArray, variable.dataType.__class__)
            result.append(str(encodedVal))
        elif variable.varType == "Agg" or variable.varType == "Alt":
            for child in variable.children:
                result.extend(self.encodeChild(child, readingToken))
        elif variable.varType == "Eol":
            # nothing to encode when child is EOL
            pass
        else:
            raise Exception("Unknown type of variable: {0}".format(variable.varType))

        if len(result) == 0:
            return ''
        else:
            return ''.join(result)

    def priority(self):
        """Returns the priority of the current encoding filter."""
        return 100

