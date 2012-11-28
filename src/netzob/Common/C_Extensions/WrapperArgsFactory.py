# -*- coding: utf-8 -*-

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

from netzob import _libScoreComputation
#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.Type.TypeConvertor import TypeConvertor
from netzob.Common.C_Extensions.WrapperMessage import WrapperMessage


class WrapperArgsFactory(object):
    """Factory dedicated to the manipulation of arguments passed to C wrapper"""

    def __init__(self, function):
        self.typeList = {"_libScoreComputation.getHighestEquivalentGroup": self.getHighestEquivalentGroup}
        if(function in self.typeList.keys()):
            self.function = function
        else:
            raise NetzobException("Function " + str(function) + " not implemented")

    def __str__(self):
        return str(self.args)

    def getHighestEquivalentGroup(self, symbols):
        self.args = []
        for s in symbols:
            self.args.append(WrapperMessage(s.getMessages()[0], s))
