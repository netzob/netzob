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
# |       - Alexandre Pigné <alexandre.pigne (a) amossys.fr>                  |
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
from netzob.Model.Vocabulary.Domain.Variables.Nodes.Repeat import Repeat


class Opt(Repeat):
    """The Opt class is a node variable that represents a variable
    that may or may not produce a value, either in abstraction or
    specialization.

    The Opt constructor expects some parameters:

    :param child: The optional variable element.
    :type child: :class:`Variable <netzob.Model.Vocabulary.Domain.Variables.AbstractVariable>`, required


    >>> from netzob.all import *
    >>> f0 = Field(String("a"), "f0")
    >>> f1 = Field(Opt(String("b")), "f1")
    >>> assert Symbol([f0, f1]).specialize() in (b"a", b"ab")

    """

    def __init__(self, child):
        super(Opt, self).__init__(child, (0, 1))

    def clone(self, map_objects={}):
        if self in map_objects:
            return map_objects[self]

        if self.children[0] in map_objects.keys():
            new_children = map_objects[self.children[0]]
        else:
            new_children = self.children[0].clone(map_objects)

        new_opt = Opt(new_children)
        map_objects[self] = new_opt
        return new_opt
