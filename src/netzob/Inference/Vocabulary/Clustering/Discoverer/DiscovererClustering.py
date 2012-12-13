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
from netzob.UI.Vocabulary.Controllers.Clustering.Discoverer.DiscovererClusteringConfigurationController import DiscovererClusteringConfigurationController

#+---------------------------------------------------------------------------+
#| Local Imports
#+---------------------------------------------------------------------------+


#+---------------------------------------------------------------------------+
#| UPGMAClustering:
#+---------------------------------------------------------------------------+
class DiscovererClustering(AbstractClusteringAlgorithm):
    """This represents the Discoverer algorithm as described in the paper 'Discoverer: Automatic Protocol Reverse Engineering from Network Traces'"""

    __algorithm_name__ = "Discoverer"
    __algorithm_description = "Cluster messages following their ASCII/Bin tokens as described in the paper 'Discoverer: Automatic Protocol Reverse Engineering from Network Traces'"

    def __init__(self):
        super(DiscovererClustering, self).__init__("discoverer")
        self.logger = logging.getLogger(__name__)

    def execute(self, layers):
        """Execute the clustering"""
        self.logger.info("Execute DISCOVERER Clustering...")

        return layers

    def getConfigurationErrorMessage(self):

        return None

    def getConfigurationController(self):
        """Create the controller which allows the configuration of the algorithm"""
        controller = DiscovererClusteringConfigurationController(self)
        return controller
