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
#| AbstractClusteringAlgorithm:
#+---------------------------------------------------------------------------+
class AbstractClusteringAlgorithm(object):
    """This abstract class must be inherited from all the clustering algorithms."""

    @staticmethod
    def getClusteringAlgorithmClassByID(id):
        for algo in AbstractClusteringAlgorithm.getAllClusteringAlgorithms():
            if algo().getID() == id:
                return algo
        return None

    @staticmethod
    def getAllClusteringAlgorithms():
        defaults = []
        # UPGMA
        from netzob.Inference.Vocabulary.Clustering.UPGMA.UPGMAClustering import UPGMAClustering
        defaults.append(UPGMAClustering)

        # Add all the registered plugins
        from netzob.Common.Plugins.NetzobPlugin import NetzobPlugin
        from netzob.Common.Plugins.ClusteringPlugin import ClusteringPlugin
        clusteringPlugins = NetzobPlugin.getLoadedPlugins(ClusteringPlugin)
        for clusteringPlugin in clusteringPlugins:
            defaults.append(clusteringPlugin.getAlgorithmClass())

        return defaults

    __algorithm_name__ = abstractproperty()
    __algorithm_description = abstractproperty()

    def __init__(self, id):
        self.logger = logging.getLogger(__name__)
        self.id = id

    def getID(self):
        return self.id

    def getName(self):
        """Returns the name of the clustering algorithm"""
        return self.__algorithm_name__

    def getDescription(self):
        """Returns the description of clustering algorithm"""
        return self.__algorithm_description

    ## TO BE IMPLEMENTED BY CHILDREN ##

    @abstractmethod
    def execute(self, symbols):
        """Execute the clustering algorithm on the provided symbols.
        @param symbols : list of L{netzob.Common.Symbol} to cluster
        @return a list of new L{netzob.Common.Symbol}"""
        self.logger.warning("This method must be defined by the inherited class")
        return []

    @abstractmethod
    def getConfigurationController(self):
        """This method will be executed to show the user some customization panels
        of the algorithm.
        @returns None or the controller of a configuration class"""

        return None

    @abstractmethod
    def getConfigurationParameters(self):
        """This method allow to export to those who wants (e.g. the xml serialization and co.)
        the current configuration of the algorithm.
        @result a dictionnary which map the parameter id with its value in string format"""

        return dict()

    @abstractmethod
    def setConfigurationParameters(self, parameters):
        """This method is executed by external classes (e.g. the workspace loaded and co.)
        which wants to provide parameters values to algorithm. The developper is responsible for
        parsing the provided dictionnary and to save the parameters in its attributes.
        @param parameters: a dictionnary which map the parameter if with their values represented in string format"""

        pass
