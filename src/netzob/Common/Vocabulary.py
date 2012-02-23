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
#| Standard library imports
#+---------------------------------------------------------------------------+
import logging
import time
from lxml.etree import ElementTree
from lxml import etree
import uuid

#+---------------------------------------------------------------------------+
#| Local Imports
#+---------------------------------------------------------------------------+
from netzob.Common.Symbol import Symbol
from netzob.Inference.Vocabulary.Clusterer import Clusterer
from netzob.Common.ProjectConfiguration import ProjectConfiguration
from netzob.Common.Field import Field
from netzob.Common.MMSTD.Symbols.impl.EmptySymbol import EmptySymbol
from netzob.Inference.Vocabulary.Alignment.UPGMA import UPGMA


#+---------------------------------------------------------------------------+
#| Vocabulary:
#|     Class definition of the vocabulary
#+---------------------------------------------------------------------------+
class Vocabulary(object):

    #+-----------------------------------------------------------------------+
    #| Constructor
    #+-----------------------------------------------------------------------+
    def __init__(self):
        self.symbols = []

    def getAllMessages(self):
        messages = []
        for symbol in self.symbols:
            for msg in symbol.getMessages():
                messages.append(msg)
        return messages

    def getSymbolWhichContainsMessage(self, message):
        for symbol in self.symbols:
            for msg in symbol.getMessages():
                if msg.getID() == message.getID():
                    return symbol
        return None

    def getSymbols(self):
        return self.symbols

    def getSymbol(self, symbolID):
        for symbol in self.symbols:
            if symbol.getID() == symbolID:
                return symbol
        # Exceptions : if ID = 0, we return an EmptySymbol
        if symbolID == str(0) :
            return EmptySymbol()    
        
        return None

    def addSymbol(self, symbol):
        if not symbol in self.symbols:
            self.symbols.append(symbol)
        else:
            logging.warn("The symbol cannot be added in the vocabulary since it's already declared in.")

    def removeSymbol(self, symbol):
        self.symbols.remove(symbol)

    def getVariables(self):
        variables = []
        for symbol in self.symbols:
            for variable in symbol.getVariables():
                if not variable in variables:
                    variables.append(variable)
        return variables
    
    def getVariableByID(self, idVar):
        for symbol in self.symbols:
            for variable in symbol.getVariables():
                    if str(variable.getID()) == idVar:
                        return variable
        return None

    def estimateNeedlemanWunschNumberOfExecutionStep(self, project):
        # The alignment is proceeded as follows:
        # align and cluster each individual group
        # align and cluster the groups together
        # orphan reduction

        if project.getConfiguration().getVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_ORPHAN_REDUCTION):
            reductionStep = 1
        else:
            reductionStep = 0

        nbSteps = len(self.symbols) + 1 + reductionStep
        logging.debug("The number of estimated steps for Needleman is " + str(nbSteps))
        return nbSteps

    #+----------------------------------------------
    #| alignWithNeedlemanWunsh:
    #|  Align each messages of each symbol with the
    #|  Needleman Wunsh algorithm
    #+----------------------------------------------
    def alignWithNeedlemanWunsh(self, project, percentOfAlignmentProgessBar_cb):
        tmpSymbols = []
        t1 = time.time()
        fraction = 0.0
        step = 1 / self.estimateNeedlemanWunschNumberOfExecutionStep(project)
        
        # First we retrieve all the parameters of the CLUSTERING / ALIGNMENT
        defaultFormat = project.getConfiguration().getVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_GLOBAL_FORMAT)
        nbIteration = project.getConfiguration().getVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_NB_ITERATION)
        minEquivalence = project.getConfiguration().getVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_EQUIVALENCE_THRESHOLD)
        if project.getConfiguration().getVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_DO_INTERNAL_SLICK):
            doInternalSlick = 1
        else:
            doInternalSlick = 0
        
        
        # We try to cluster each symbol
        for symbol in self.symbols:
#            percentOfAlignmentProgessBar_cb(fraction, "Aligning symbol " + symbol.getName())
            clusteringSolution = UPGMA(project, [symbol], True, nbIteration, minEquivalence, doInternalSlick, defaultFormat, percentOfAlignmentProgessBar_cb)
            tmpSymbols.extend(clusteringSolution.executeClustering())
            fraction = fraction + step

        percentOfAlignmentProgessBar_cb(fraction, None)

        # Now that all the symbols are reorganized separately
        # we should consider merging them
     
        clusteringSolution = UPGMA(project, tmpSymbols, False, nbIteration, minEquivalence, doInternalSlick, defaultFormat, percentOfAlignmentProgessBar_cb)
        
        self.symbols = clusteringSolution.executeClustering()        
        
        logging.info("Time of parsing : " + str(time.time() - t1))


    #+----------------------------------------------
    #| alignWithDelimiter:
    #|  Align each message of each symbol with a specific delimiter
    #+----------------------------------------------
    def forcePartitioning(self, configuration, aFormat, delimiter):
        for symbol in self.symbols:
            symbol.forcePartitioning(configuration, aFormat, delimiter)

    #+----------------------------------------------
    #| simplePartitioning:
    #|  Do message partitioning according to column variation
    #+----------------------------------------------
    def simplePartitioning(self, configuration, unitSize):
        for symbol in self.symbols:
            symbol.simplePartitioning(configuration, unitSize)

    def save(self, root, namespace_project, namespace_common):
        xmlVocabulary = etree.SubElement(root, "{" + namespace_project + "}vocabulary")
        xmlSymbols = etree.SubElement(xmlVocabulary, "{" + namespace_project + "}symbols")
        for symbol in self.symbols:
            symbol.save(xmlSymbols, namespace_project, namespace_common)

    @staticmethod
    def loadVocabulary(xmlRoot, namespace, namespace_common, version, project):
        vocabulary = Vocabulary()

        if version == "0.1":
            # parse all the symbols which are declared in the vocabulary
            for xmlSymbol in xmlRoot.findall("{" + namespace + "}symbols/{" + namespace + "}symbol"):
                symbol = Symbol.loadSymbol(xmlSymbol, namespace, namespace_common, version, project)
                print "load voca : = " + str(symbol)
                if symbol != None:
                    print "-->adding it"
                    vocabulary.addSymbol(symbol)
        return vocabulary
