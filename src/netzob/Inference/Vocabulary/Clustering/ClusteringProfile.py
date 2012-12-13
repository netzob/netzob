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
import uuid
from netzob.Inference.Vocabulary.Clustering.UPGMA.UPGMAClustering import UPGMAClustering
from netzob.Inference.Vocabulary.Clustering.Discoverer.DiscovererClustering import DiscovererClustering

#+---------------------------------------------------------------------------+
#| Local Imports
#+---------------------------------------------------------------------------+


#+---------------------------------------------------------------------------+
#| ClusteringProfile:
#+---------------------------------------------------------------------------+
class ClusteringProfile(object):
    """This class represents the clustering profiles"""

    @staticmethod
    def getDefaultClusteringProfiles():
        defaults = []

        # UPGMA
        originalProfile = ClusteringProfile(_("Original Clustering"), _("Execute an UPGMA clustering using original similarity measure."))
        UPGMAAlgorithm = UPGMAClustering()
        originalProfile.addAlgorithm(UPGMAAlgorithm)
        defaults.append(originalProfile)

        # Discoverer
        discovererProfile = ClusteringProfile(_("Discoverer by W.Cui"), _("Cluster messages following their ASCII/Bin tokens as described in paper 'Discoverer: Automatic Protocol Reverse Engineering from Network Traces'"))
        DiscovererAlgorithm = DiscovererClustering()
        discovererProfile.addAlgorithm(DiscovererAlgorithm)
        defaults.append(discovererProfile)

        return defaults

    def __init__(self, name, description=None):
        self.logger = logging.getLogger(__name__)
        self.id = uuid.uuid4()
        self.name = name
        self.description = description
        self.algorithms = []

    def getID(self):
        return self.id

    def getName(self):
        return self.name

    def getDescription(self):
        return self.description

    def getAlgorithms(self):
        return self.algorithms

    def addAlgorithm(self, algorithm):
        self.algorithms.append(algorithm)

    def removeAlgorithm(self, algorithm):
        if algorithm in self.algorithms:
            self.algorithms.remove(algorithm)
        else:
            self.logger.warning("Impossible to remove the unexisting provided algorithm ({0}) from the list of registered algorithms".format(algorithm.getID()))

    def execute(self, layers):
        tmp_layers = layers
        for algorithm in self.getAlgorithms():
            tmp_layers = algorithm.execute(tmp_layers)
        return tmp_layers
