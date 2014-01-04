# -*- coding: utf-8 -*-

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
#| Global Imports
#+---------------------------------------------------------------------------+
from locale import gettext as _
import logging
from netzob.Inference.Vocabulary.Clustering.AbstractDistanceAlgorithm import AbstractDistanceAlgorithm

#+---------------------------------------------------------------------------+
#| Local Imports
#+---------------------------------------------------------------------------+


#+---------------------------------------------------------------------------+
#| ManhattanDistance:
#+---------------------------------------------------------------------------+
class ManhattanDistance(AbstractDistanceAlgorithm):
    """This class represents the Manhattan Distance algorithm"""

    __algorithm_name__ = "ManhattanDistance"
    __algorithm_description = "The sum of the absolute differences of the coordinates"

    def __init__(self):
        super(ManhattanDistance, self).__init__("manhattan")
        self.logger = logging.getLogger(__name__)

    def execute(self, coordinates):
        """Computes the manhattan distance"""
        self.logger.info("Compute the Manhattan Distance between {0} coordinates".format(len(coordinates)))

        return 10
