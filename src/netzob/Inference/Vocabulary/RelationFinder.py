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
import uuid

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
        cells = [field.getCells()
                 for field in symbol.getExtendedFields()
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

    #+----------------------------------------------
    #| executeOnCells:
    #| @param cellsTable : a table of cells
    #+----------------------------------------------
    def executeOnCells(self, cellsTable):
        if cellsTable:
            # Invert array dimensions liks this:
            # < [[m0f0, m1f0, ...], [m0f1, m1f1, ...]]
            # > [(m0f0, m0f1, ...), (m1f0, m1f1, ...)]
            for algo, refs in _libRelation.find(zip(*cellsTable)).items():
                for ref_idx, ref_off, ref_size, rels in refs:
                    print "Relations(%s) with F%d:" % (algo, ref_idx)
                    for rel_id, rel_conf in enumerate(rels):
                        print "  %d. F[%d][%d:%d]" % ((rel_id,) + rel_conf)

    #+----------------------------------------------
    #| executeOnCellsWithAttributes:
    #+----------------------------------------------
    def executeOnCellsWithAttributes(self, x_field, x_attr, y_field, y_attr):
        # Convert cells according to their interesting attribute (data, size or offset)
        if x_attr == "s" and y_attr == "s":  # Two size field are uncertain...
            return
        x_values = x_field.getCells()
        y_values = y_field.getCells()

        # Try to find a relation that matches each cell
        results = []
        relation_fcts = {}
        relation_fcts["size"] = self.sizeRelation
        relation_fcts["equality"] = self.equalRelation

        for (relation_name, relation_fct) in relation_fcts.items():
            isRelation = True
            for i in range(len(x_values)):
                if not relation_fct(x_values[i], x_attr, y_values[i], y_attr):
                    isRelation = False
                    break
            if isRelation:
                logging.info("Relation found between '" + x_attr + ":" + x_field.getName() + "' and '" + y_attr + ":" + y_field.getName() + "'")
                logging.info("  Relation: " + relation_name)
                id_relation = str(uuid.uuid4())
                results.append({'id': id_relation,
                                "relation_type": relation_name,
                                'x_field': x_field,
                                'x_attribute': x_attr,
                                'y_field': y_field,
                                'y_attribute': y_attr})
        return results

    def equalRelation(self, x, x_attr, y, y_attr):
        if x == y:
            return True
        else:
            return False

    def sizeRelation(self, x, x_attr, y, y_attr):
        if x_attr == "s":
            if len(x) > 0:
                x = len(x) / 2
        else:
            if len(x) > 0:
                x = int(x, 16)
            else:
                x = 0
        if y_attr == "s":
            if len(y) > 0:
                y = len(y) / 2
        else:
            if len(y) > 0:
                y = int(y, 16)
            else:
                y = 0

        if x == y:
            return True
        else:
            return False
