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

#+----------------------------------------------
#| Global Imports
#+----------------------------------------------
import logging

#+----------------------------------------------
#| Local Imports
#+----------------------------------------------
from netzob import _libRelation

#+----------------------------------------------
#| RelationFinder:
#|     Provides multiple algorithms to find relations between messages
#+----------------------------------------------
class RelationFinder(object):
    #+----------------------------------------------
    #| Constructor:
    #| @param project : the project where the search will be executed
    #+----------------------------------------------
    def __init__(self, project):
        # create logger with the given configuration
        self.log = logging.getLogger(__name__ + '.py')
        self.project = project

    #+----------------------------------------------
    #| execute:
    #| @param symbol : if not None, the operation will be limited to provided symbol
    #+----------------------------------------------
    def execute(self, symbol):
        cells = [field.getCells() \
                 for field in symbol.getExtendedFields() \
                 #if not field.isStatic()
                 ]
        if cells:
            # Invert array dimensions liks this:
            # < [[m0f0, m1f0, ...], [m0f1, m1f1, ...]]
            # > [(m0f0, m0f1, ...), (m1f0, m1f1, ...)]
            for algo, refs in _libRelation.find(zip(*cells)).items():
                for ref_idx, ref_off, ref_size, rels in refs:
                    print "Relations(%s) with F%d:" % (algo, ref_idx)
                    for rel_id, rel_conf in enumerate(rels):
                        print "  %d. F[%d][%d:%d]" % ((rel_id,) + rel_conf)
