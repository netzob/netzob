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
from lxml import etree

#+---------------------------------------------------------------------------+
#| Local Imports
#+---------------------------------------------------------------------------+
from netzob.Inference.Vocabulary.Clustering.UPGMA.UPGMAClustering import UPGMAClustering
from netzob.Inference.Vocabulary.Clustering.Discoverer.DiscovererClustering import DiscovererClustering
from netzob.Inference.Vocabulary.Clustering.AbstractClusteringAlgorithm import AbstractClusteringAlgorithm


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
        originalProfile.setWritable(False)
        UPGMAAlgorithm = UPGMAClustering()
        originalProfile.addAlgorithm(UPGMAAlgorithm)
        defaults.append(originalProfile)

        # Discoverer
        discovererProfile = ClusteringProfile(_("Discoverer by W.Cui"), _("Cluster messages following their ASCII/Bin tokens as described in paper 'Discoverer: Automatic Protocol Reverse Engineering from Network Traces'"))
        discovererProfile.setWritable(False)
        DiscovererAlgorithm = DiscovererClustering()
        discovererProfile.addAlgorithm(DiscovererAlgorithm)
        defaults.append(discovererProfile)

        return defaults

    @staticmethod
    def loadFromXML(rootElement, namespace, version):
        nameProfile = rootElement.get("name")
        descriptionProfile = None
        descriptionXML = rootElement.find("{" + namespace + "}description")
        if descriptionXML is not None:
            descriptionProfile = descriptionXML.text

        profile = ClusteringProfile(nameProfile, descriptionProfile)

        # Parse algorithms
        algorithms = rootElement.find("{" + namespace + "}clusteringAlgorithms")
        if algorithms is not None:
            for algorithm in algorithms.findall("{" + namespace + "}clusteringAlgorithm"):
                algorithmID = algorithm.get("id")
                logging.debug("Algorithm '{0}' is referenced in profile.".format(algorithmID))
                parameters = dict()
                for parameter in algorithm.findall("{" + namespace + "}parameter"):
                    parameterName = parameter.get('name')
                    parameterValue = parameter.text
                    parameters[parameterName] = parameterValue

                classAlgorithm = AbstractClusteringAlgorithm.getClusteringAlgorithmClassByID(algorithmID)
                if classAlgorithm is not None:
                    # Create a new instance of the algorithm
                    instanceAlgorithm = classAlgorithm()
                    # Configure it with the parameters of the original algorithm
                    instanceAlgorithm.setConfigurationParameters(parameters)
                    profile.addAlgorithm(instanceAlgorithm)
                else:
                    logging.warning("Impossible to find the algorithm ({0}) required for clustering profile {1}".format(algorithmID, nameProfile))
        return profile

    def __init__(self, name, description=None):
        self.log = logging.getLogger(__name__)
        self.id = uuid.uuid4()
        self.name = name
        self.description = description
        self.algorithms = []
        self.writable = True

    def getID(self):
        return self.id

    def getName(self):
        return self.name

    def getDescription(self):
        return self.description

    def setDescription(self, description):
        self.description = description

    def getAlgorithms(self):
        return self.algorithms

    def isWritable(self):
        return self.writable

    def setWritable(self, value):
        self.writable = value

    def addAlgorithm(self, algorithm):
        self.algorithms.append(algorithm)

    def removeAlgorithm(self, algorithm):
        if algorithm in self.algorithms:
            self.algorithms.remove(algorithm)
        else:
            self.log.warning("Impossible to remove the unexisting provided algorithm ({0}) from the list of registered algorithms".format(algorithm.getID()))

    def execute(self, layers):
        tmp_layers = layers
        for algorithm in self.getAlgorithms():
            tmp_layers = algorithm.execute(tmp_layers)
        return tmp_layers

    def duplicate(self, profileName):
        """Duplicate the current profile in a new one. The new object
        will have no relations with the current one.
        @param profileName: the name of the profile to create
        @return a new L{netzob.Inference.Vocabulary.Clustering.ClusteringProfile} object"""

        newProfile = ClusteringProfile(profileName, self.getDescription())
        for algorithm in self.getAlgorithms():
            # Create a new instance of the algorithm
            duplicatedAlgorithm = algorithm.__class__()
            # Configure it with the parameters of the original algorithm
            duplicatedAlgorithm.setConfigurationParameters(algorithm.getConfigurationParameters())
            newProfile.addAlgorithm(duplicatedAlgorithm)
        return newProfile

    def save(self, parent, namespace):
        """Save in the XML tree the current clustering profile"""
        if not self.isWritable():
            self.log.debug("Can't save the clustering profile {0} because its not writable.".format(self.getName()))
            return

        xmlClusteringProfile = etree.SubElement(parent, "{" + namespace + "}clusteringProfile")
        xmlClusteringProfile.set("name", str(self.getName()))

        if self.getDescription() is not None:
            xmlCPDescription = etree.SubElement(xmlClusteringProfile, "{" + namespace + "}description")
            xmlCPDescription.text = str(self.getDescription())

        if len(self.getAlgorithms()) > 0:
            xmlCPAlgos = etree.SubElement(xmlClusteringProfile, "{" + namespace + "}clusteringAlgorithms")
            # Save the attached algorithms
            for algorithm in self.getAlgorithms():
                xmlCPAlgo = etree.SubElement(xmlCPAlgos, "{" + namespace + "}clusteringAlgorithm")
                xmlCPAlgo.set("id", str(algorithm.getID()))
                parameters = algorithm.getConfigurationParameters()
                if parameters is not None:
                    for paramKey in parameters.keys():
                        xmlCPAlgoParam = etree.SubElement(xmlCPAlgo, "{" + namespace + "}parameter")
                        xmlCPAlgoParam.set("name", str(paramKey))
                        xmlCPAlgoParam.text = str(parameters[paramKey])
