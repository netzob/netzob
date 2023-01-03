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
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger, public_api
from netzob.Model.Vocabulary.Domain.Variables.Nodes.Repeat import Repeat
from netzob.Model.Vocabulary.Domain.Variables.Leafs.Data import Data
from netzob.Model.Vocabulary.Types.Raw import Raw


class Opt(Repeat):
    r"""The Opt class is a node variable that represents a variable
    that may or may not produce a value, either in abstraction or
    specialization.

    The Opt constructor expects some parameters:

    :param child: The optional variable element.
    :param name: The name of the variable (if None, the name will
                 be generated).
    :type child: :class:`Variable <netzob.Model.Vocabulary.Domain.Variables.AbstractVariable.AbstractVariable>`, required
    :type name: :class:`str`, optional


    The following code shows an example of the Opt usage.

    >>> from netzob.all import *
    >>> f0 = Field(String("a"), "f0")
    >>> f1 = Field(Opt(String("b")), "f1")
    >>> assert next(Symbol([f0, f1]).specialize()) in (b"a", b"ab")

    """

    @public_api
    def __init__(self, child, name=None):
        super(Opt, self).__init__(child, (0, 1), name=name)

    @public_api
    def copy(self, map_objects=None):
        """Copy the current object as well as all its dependencies.

        :return: A new object of the same type.
        :rtype: :class:`Opt <netzob.Model.Vocabulary.Domain.Variables.Nodes.Opt.Opt>`

        """
        if map_objects is None:
            map_objects = {}
        if self in map_objects:
            return map_objects[self]

        new_opt = Opt(Data(Raw()))
        map_objects[self] = new_opt

        if self.children[0] in map_objects.keys():
            new_children = map_objects[self.children[0]]
        else:
            new_children = self.children[0].copy(map_objects)

        new_opt.children = [new_children]
        return new_opt
