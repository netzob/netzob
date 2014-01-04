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
import rpy2.robjects as robjects
import tempfile
import os
import subprocess
import shutil
import uuid

#+---------------------------------------------------------------------------+
#| Local Imports
#+---------------------------------------------------------------------------+
from ASAPClusteringConfigurationController import ASAPClusteringConfigurationController
from netzob.Inference.Vocabulary.Clustering.AbstractClusteringAlgorithm import AbstractClusteringAlgorithm
from netzob.Common.ResourcesConfiguration import ResourcesConfiguration
from netzob.Common.Type.TypeConvertor import TypeConvertor
from netzob.Common.Symbol import Symbol


#+---------------------------------------------------------------------------+
#| ASAPClustering
#+---------------------------------------------------------------------------+
class ASAPClustering(AbstractClusteringAlgorithm):

    __algorithm_name__ = "ASAP"
    __algorithm_description = """Matrix factorization \eqn{A = B C} with strictly positiv matrices \eqn{B, C}
  which minimize the reconstruction error \eqn{\|A - B C\|}. This
  duplicate-aware version of the non-negtive matrix factorization (NMF)
  is based on the Alternating Least Square
  approach and exploits the duplicate information to speed up the calculation."""

    CLUSTERING_THRESHOLD = "clustering_threshold"

    @staticmethod
    def getDefaultClusteringThreshold():
        return 0.2

    def __init__(self):
        super(ASAPClustering, self).__init__("asap")
        self.clusteringThreshold = ASAPClustering.getDefaultClusteringThreshold()

    def execute(self, symbols):
        """Execute the clustering"""
        self.log = logging.getLogger(__name__)

        if symbols is None or len(symbols) < 1:
            self.log.debug("No symbol provided")
            return []

        # Retrieve all the messages to cluster
        messages = []
        for symbol in symbols:
            messages.extend(symbol.getMessages())

        """ Steps of the algorithm
        Step 1 : Create a specific alphabet based on provided messages
        Step 2 : Matrix factorization
        Step 3 : Construction of communication template"""
        self.log.warning("Create an alphabet based on provided messages")

        # Step 1 :
        # Generate the raw files for sally
        # Generate the sally config file
        # Execute sally : sally -c asap.cfg asap.raw asap.sally
        # Clean the sally output file using the PRISMA file : libs/PRISMA/inst/extdata/sallyPreprocessing.py
        # Load the data in PRISMA with R source code loadPrismaData()

        sallyRawFile = self.generateSallyRawFile(messages)
        self.log.debug("Sally raw file created at {0}".format(sallyRawFile))

        sallyConfigFile = self.generateSallyConfigFile()
        self.log.debug("Sally config file created at {0}".format(sallyConfigFile))

        sallyOutputFile = "{0}.output".format(sallyRawFile)
        sallyPath = "sally"

        # Execute Sally
        sallyCommand = "{0} -c {1} {2} {3}".format(sallyPath, sallyConfigFile, sallyRawFile, sallyOutputFile)
        self.log.debug("Execute Sally : {0}".format(sallyCommand))
        result = subprocess.call(sallyCommand, shell=True)

        # Execute preprocessing script to convert sally results to compliant PRISMA format
        fSallyOutputFile = "{0}.fsally".format(sallyOutputFile)
        self.preprocessingSally(sallyOutputFile, fSallyOutputFile)
        self.log.debug("Execute RPrisma:")
        newSymbols = self.executeRPrisma(sallyOutputFile, messages, symbols)

        self.log.debug("Cleaning temporary files...")
        # Remove temporary files
        os.remove(sallyRawFile)
        os.remove(sallyConfigFile)
        os.remove(sallyOutputFile)
        os.remove(fSallyOutputFile)

        return newSymbols

    def executeRPrisma(self, fsallyFilePath, messages, currentSymbols):
        """Execute R code of PRISMA given the fsallyFilePath. Because the R
        function loadPrismaData append 'fsally' to the filename, the parameter should be the filename without its extensions"""

        self.log.debug("Execute RPrima with threshold: {0}".format(self.getClusteringThreshold()))

        currentProject = currentSymbols[0].getProject()

        netzobPrismaLoader = self.getNetzobPrismaLoaderSource()
        # load the source code in R
        robjects.r(netzobPrismaLoader)
        # Retrieve the function
        executePrisma = robjects.r['executePrisma']
        result = executePrisma(fsallyFilePath)

        # Parse obtained results and put everything in a
        # big dict() (cf. clusters)
        nbCluster = int(result.ncol)
        clusterNames = result.colnames

        symbols = []

        # Create all the symbols
        for iCluster in range(0, nbCluster):
            symbols.append(Symbol(uuid.uuid4(), clusterNames[iCluster], currentProject))

        # Attach every message to its cluster > symbol
        for iMessage, message in enumerate(messages):
            maxCluster = None
            maxValue = -1
            for iCluster in range(0, nbCluster):
                score = result.rx(iMessage + 1, iCluster + 1)[0]
                if score > maxValue:
                    maxValue = score
                    maxCluster = iCluster
            if maxCluster is not None:
                symbols[maxCluster].addMessage(message)

        return symbols

    def getFileContent(self, filePath):
        """Reads and retrieves the content of a file
        which path is provided in argument"""
        content = None
        try:
            # open the file and retrieve its content
            fileHandle = open(filePath, 'r')
            content = fileHandle.read()
            fileHandle.close()
        except Exception, e:
            self.log.warning("An error occured which prevented to retrieve the content of file {0} : {1}".format(filePath, e))

        return content

    def getNetzobPrismaLoaderSource(self):
        """Retrieves and returns the content of the ASAP wrapper
        in R"""
        wrapperPrismaSourcePath = os.path.join(ResourcesConfiguration.getPluginsStaticResources(), "ASAPClustering", "libs", "netzob_wrapper_prisma.r")
        return self.getFileContent(wrapperPrismaSourcePath)

    def preprocessingSally(self, sallyInFilename, sallyOutFilename):
        """Execute the PRISMA preprocessing script
        on the sally output file to clean it from
        useless informations which would slower R parsing"""
        sallyIn = file(sallyInFilename)
        sallyOut = file(sallyOutFilename, 'w')
        # skip first line
        sallyIn.readline()
        allNgrams = {}
        count = 0
        for l in sallyIn:
            count += 1
            if count % 1000 == 0:
                print(count)
            info = l.split(" ")
            if info[0] == "":
                curNgrams = []
            else:
                curNgrams = [ngramInfo.split(":")[1] for ngramInfo in info[0].split(",")]
                allNgrams.update(allNgrams.fromkeys(curNgrams))
            sallyOut.write("%s\n" % " ".join(curNgrams))
        sallyOut.write("%s\n" % " ".join(allNgrams.keys()))
        sallyOut.close()
        sallyIn.close()

    def generateSallyRawFile(self, messages):
        """Create a temporary Sally compliant file with all the provided messages
        to align"""
        (sallyRawFile, sallyRawFileName) = tempfile.mkstemp(suffix='netzob_sally')
        for message in messages:
            os.write(sallyRawFile, TypeConvertor.netzobRawToString(message.getStringData()) + '\n')
        os.close(sallyRawFile)
        return sallyRawFileName

    def generateSallyConfigFile(self):
        (sallyConfigFile, sallyConfigFilename) = tempfile.mkstemp(suffix='netzob_sally.cfg')
        sallyDefaultPath = os.path.join(ResourcesConfiguration.getPluginsStaticResources(), "ASAPClustering", "defaults", "sally.cfg")
        # copy the default config file
        shutil.copyfile(sallyDefaultPath, sallyConfigFilename)
        return sallyConfigFilename

    def getConfigurationParameters(self):
        parameters = dict()
        parameters[ASAPClustering.CLUSTERING_THRESHOLD] = self.clusteringThreshold
        print "set clustering threshold : !! {0}".format(self.clusteringThreshold)
        return parameters

    def setConfigurationParameters(self, parameters):
        try:
            self.clusteringThreshold = float(parameters[ASAPClustering.CLUSTERING_THRESHOLD])
            print "set clustering threshold : {0}".format(self.clusteringThreshold)
        except:
            pass

    def getConfigurationController(self):
        """Create the controller which allows the configuration of the algorithm"""
        controller = ASAPClusteringConfigurationController(self)
        return controller

    def getClusteringThreshold(self):
        return self.clusteringThreshold

    def setClusteringThreshold(self, value):
        self.clusteringThreshold = value
