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

@NetzobLogger
class MatrixList(list):
    """This type of list has been created to represent it as matrix
    which means its a list of list.

    The __str__ method has been redefined to propose
    a nice representation of its content.
    """
    def __init__(self):
        self.headers = []
    
    @property
    def headers(self):
        """A list of sorted strings. Each string will be displayed as a column header"""
        return self.__headers

    @headers.setter
    def headers(self, headers):
        self.__headers = []
        for h in headers:
            self.__headers.append(str(h))
        
    def __repr__(self):
        # Prepare data to be returned
        r_repr = []
        
        if len(self) > 0:
            nb_col = len(self[0])
            if self.headers is not None and len(self.headers) == nb_col:
                r_repr.append(self.headers)
            else:
                r_repr.append(["Field"] * nb_col)


        for r in self:
            r1_repr = []
            for r1 in r:
                if isinstance(r1, bytes):
                    try:
                        r1 = r1.decode('utf-8')
                    except UnicodeDecodeError:
                        pass
                r1 = repr(r1)
                r1_repr.append(r1)
            r_repr.append(r1_repr)

        # Prepare format
        cs = list(zip(*r_repr))
        c_ws = [max(len(value) for value in c) for c in cs]
        line = ["-"*w for w in c_ws]
        r_repr.insert(1, line)
        r_repr.append(line)
        format = ' | '.join(['%%-%ds' % w for w in c_ws])

        # Format data
        result = [(format % tuple(r)) for r in r_repr]
        return '\n'.join(result)
