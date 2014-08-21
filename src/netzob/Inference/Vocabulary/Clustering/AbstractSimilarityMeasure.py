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
from abc import abstractproperty, abstractmethod

#+---------------------------------------------------------------------------+
#| Local Imports
#+---------------------------------------------------------------------------+


#+---------------------------------------------------------------------------+
#| AbstractSimilarityMeasure
#+---------------------------------------------------------------------------+
class AbstractSimilarityMeasure(object):
    """This abstract class must be inherited from all the similarity measures."""

    @staticmethod
    def getAllSimilarityMeasures():
        defaults = []
        from netzob.Inference.Vocabulary.Clustering.SimilarityMeasures.RatioOfDynamicBytes import RatioOfDynamicBytes
        defaults.append(RatioOfDynamicBytes)

        return defaults

    __measure_name = abstractproperty()
    __measure_description = abstractproperty()

    def __init__(self, id):
        self.logger = logging.getLogger(__name__)
        self.id = id

    def getID(self):
        return self.id

    def getName(self):
        """Returns the name of the measure"""
        return self.__algorithm_name__

    def getDescription(self):
        """Returns the description of measure"""
        return self.__algorithm_description

    @abstractmethod
    def execute(self):
        self.logger.warning("This method must be defined by the inherited class")

    @abstractmethod
    def getConfigurationController(self):
        self.logger.warning("This method must be defined by the inherited class")
