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
from netzob.Common.Models.Vocabulary.AbstractField import AbstractField


class Symbol(AbstractField):

    def __init__(self, fields=None, name=None):
        """
        :keyword fields: the fields which participate in symbol definition
        :type fields: a :class:`list` of :class:`netzob.Common.Models.Vocabulary.Field`
        :keyword name: the name of the symbol
        :type name: :class:`str`
        """
        super(Symbol, self).__init__(name, None, True)
        self.children = fields

    def generate(self, mutator=None):
        """Generate an hexastring which content
        follows the fields definitions attached to current element.

        :keyword mutator: if set, the mutator will be used to mutate the fields definitions
        :type mutator: :class:`netzob.Common.Models.Mutators.AbstractMutator`

        :return: a generated content represented with an hexastring
        :rtype: :class:`str``
        :raises: :class:`netzob.Common.Models.Vocabulary.AbstractField.GenerationException` if an error occurs while generating a message
        """
        content = []
        for child in self.children:
            content.append(child.generate(mutator))
        return ''.join(content)
