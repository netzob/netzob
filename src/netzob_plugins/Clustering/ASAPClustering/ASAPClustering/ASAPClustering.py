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
import rpy2.robjects as robjects
import tempfile
import os

#+---------------------------------------------------------------------------+
#| Local Imports
#+---------------------------------------------------------------------------+
from ASAPClusteringConfigurationController import ASAPClusteringConfigurationController
from netzob.Inference.Vocabulary.Clustering.AbstractClusteringAlgorithm import AbstractClusteringAlgorithm


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
        """ Steps of the algorithm
        Step 1 : Create a specific alphabet based on provided messages
        Step 2 : Matrix factorization
        Step 3 : Construction of communication template"""

        self.log.debug("Create an alphabet based on provided messages")

        # Step 1 :
        # Generate the raw files for sally
        # Generate the sally config file
        # Execute sally : sally -c asap.cfg asap.raw asap.sally
        # Clean the sally output file using the PRISMA file : libs/PRISMA/inst/extdata/sallyPreprocessing.py
        # Load the data in PRISMA with R source code loadPrismaData()

        sallyRawFile = self.generateSallyRawFile(symbols)
        self.log.debug("Sally raw file created at {0}".format(sallyRawFile))

        sallyConfigFile = self.generateSallyConfigFile()
        self.log.debug("Sally config file created at {0}".format(sallyConfigFile))

        # Remove temporary files
        os.remove(sallyRawFile)
        os.remove(sallyConfigFile)

        # self.log.debug("Execute a simple test R test")
        # pi = robjects.r['pi']
        # self.log.debug("PI = {0}".format(pi[0]))

    def generateSallyRawFile(self, symbols):
        (sallyRawFile, sallyRawFileName) = tempfile.mkstemp(suffix='netzob_sally')
        for symbol in symbols:
            for message in symbol.getMessages():
                os.write(sallyRawFile, message.getStringData() + '\n')
                print message.getStringData()
        os.close(sallyRawFile)
        return sallyRawFileName

    def generateSallyConfigFile(self):
        (sallyConfigFile, sallyConfigFilename) = tempfile.mkstemp(suffix='netzob_sally.cfg')
        return sallyConfigFilename

    def getConfigurationController(self):
        """Create the controller which allows the configuration of the algorithm"""
        controller = ASAPClusteringConfigurationController(self)
        return controller
