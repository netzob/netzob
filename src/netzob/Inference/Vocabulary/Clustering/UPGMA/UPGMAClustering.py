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

#+---------------------------------------------------------------------------+
#| Global Imports
#+---------------------------------------------------------------------------+
from locale import gettext as _
import logging
from netzob.Inference.Vocabulary.Clustering.AbstractClusteringAlgorithm import AbstractClusteringAlgorithm
from netzob.UI.Vocabulary.Controllers.Clustering.UPGMA.UPGMAClusteringConfigurationController import UPGMAClusteringConfigurationController

#+---------------------------------------------------------------------------+
#| Local Imports
#+---------------------------------------------------------------------------+


#+---------------------------------------------------------------------------+
#| UPGMAClustering:
#+---------------------------------------------------------------------------+
class UPGMAClustering(AbstractClusteringAlgorithm):
    """This class represents the UPGMA algorithm"""

    __algorithm_name__ = "UPGMA"
    __algorithm_description = "Hierarchical clustering"

    @staticmethod
    def getDefaultSimilarityMeasures():
        return None

    @staticmethod
    def getDefaultEquivalenceThreshold():
        return 50.0

    def __init__(self, similarityMeasures=None, equivalenceThreshold=None):
        super(UPGMAClustering, self).__init__("upgma")
        self.logger = logging.getLogger(__name__)
        if similarityMeasures is None or len(similarityMeasures) == 0:
            similarityMeasures = UPGMAClustering.getDefaultSimilarityMeasures()
        self.similarityMeasures = similarityMeasures
        if equivalenceThreshold is None:
            UPGMAClustering.getDefaultEquivalenceThreshold()
        self.equivalenceThreshold = equivalenceThreshold

    def execute(self, layers):
        """Execute the UPGMA clustering"""
        self.logger.info("Execute UPGMA Clustering...")

        return layers

    def getConfigurationErrorMessage(self):
        if self.equivalenceThreshold is None:
            return _("Equivalence Threshold is not valid")
        return None

    def getConfigurationController(self):
        """Create the controller which allows the configuration of the algorithm"""
        controller = UPGMAClusteringConfigurationController(self)
        return controller

    def getEquivalenceThreshold(self):
        return self.equivalenceThreshold

    def setEquivalenceThreshold(self, equivalenceThreshold):
        self.equivalenceThreshold = equivalenceThreshold
