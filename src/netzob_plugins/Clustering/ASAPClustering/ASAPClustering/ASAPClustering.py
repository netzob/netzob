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


#+---------------------------------------------------------------------------+
#| Local Imports
#+---------------------------------------------------------------------------+
from ASAPClusteringConfigurationController import ASAPClusteringConfigurationController


#+---------------------------------------------------------------------------+
#| ASAPClustering
#+---------------------------------------------------------------------------+
class ASAPClustering(AbstractClusteringAlgorithm):

    __algorithm_name__ = "ASAP"
    __algorithm_description = "bla bla"

    def __init__(self):
        super(ASAPClustering, self).__init__("asap")
        self.log = logging.getLogger(__name__)

    def execute(self, symbols):
        """Execute the clustering"""
        self.log.info("Execute ASAP Clustering...")

    def getConfigurationController(self):
        """Create the controller which allows the configuration of the algorithm"""
        controller = ASAPClusteringConfigurationController(self)
        return controller
