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

#+----------------------------------------------
#| Global Imports
#+----------------------------------------------
import gobject
import logging
import uuid

#+----------------------------------------------
#| Local Imports
#+----------------------------------------------
from netzob.Common.Symbol import Symbol
from netzob.Common.ProjectConfiguration import ProjectConfiguration
from netzob.Common.Type.TypeConvertor import TypeConvertor
from netzob.Common.Type.TypeIdentifier import TypeIdentifier

#+----------------------------------------------
#| C Imports
#+----------------------------------------------
import libNeedleman


#+----------------------------------------------
#| Clusterer:
#|     Reorganize a set of symbols
#+----------------------------------------------
class Clusterer(object):

    def __init__(self, project, symbols, explodeSymbols=False):
        self.configuration = project.getConfiguration()

        self.symbols = []
        self.project = project

        # Create logger with the given configuration
        self.log = logging.getLogger('netzob.Modelization.Clusterer.py')

        if explodeSymbols == False:
            self.symbols = symbols
            self.log.debug("A number of {0} already aligned symbols will be clustered.".format(str(len(symbols))))
        else:
            # Create a symbol for each message
            self.symbols = []
            for symbol in symbols:
                for m in symbol.getMessages():
                    tmpSymbol = Symbol(str(uuid.uuid4()), "Symbol", self.getProject())
                    tmpSymbol.addMessage(m)
                    self.symbols.append(tmpSymbol)
                    self.log.debug("A number of {0} messages will be clustered.".format(tmpSymbol.getID()))

    #+----------------------------------------------
    #| retrieveMaxIJ:
    #|   given a list of symbols, it computes the
    #|   the possible two symbols which can be merged
    #| @return (i,j,max) (i,j) path in the matrix of
    #|                   the symbols to merge
    #|                    max score of the two symbols
    #+----------------------------------------------
    def retrieveEffectiveMaxIJ(self):
        self.log.debug("Computing the associated matrix")
        # Serialize the symbols before feeding the C library
        if self.configuration.getVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_DO_INTERNAL_SLICK):
            doInternalSlick = 1
        else:
            doInternalSlick = 0
        
        # Serialize the symbols
        (serialSymbols, formatSymbols) = TypeConvertor.serializeSymbols(self.symbols)
        
        # Execute the Clustering part in C :) (thx fgy)
        (i_max, j_max, maxScore) = libNeedleman.getMatrix(doInternalSlick, len(self.symbols), formatSymbols, serialSymbols)
        return (i_max, j_max, maxScore)
            
            
#        serialSymbols = ""
#        format = ""
#
#        for symbol in self.symbols:
#            if symbol.getAlignment() != "":  # If we already computed the alignement of the symbol, then use it
#                format += "1" + "G"
#                messageTmp = ""
#                alignmentTmp = ""
#                for i in range(0, len(symbol.getAlignment()), 2):
#                    if symbol.getAlignment()[i:i + 2] == "--":
#                        messageTmp += "\xff"
#                        alignmentTmp += "\x01"
#                    else:
#                        messageTmp += TypeConvertor.netzobRawToPythonRaw(symbol.getAlignment()[i:i + 2])
#                        alignmentTmp += "\x00"
#                format += str(len(symbol.getAlignment()) / 2) + "M"
#                serialSymbols += messageTmp
#                serialSymbols += alignmentTmp
#                
#            else:
#                format += str(len(symbol.getMessages())) + "G"
#                for m in symbol.getMessages():
#                    format += str(len(m.getReducedStringData()) / 2) + "M"
#                    serialSymbols += TypeConvertor.netzobRawToPythonRaw(m.getReducedStringData())  # The message
##                    print m.getReducedStringData()
#                    serialSymbols += "".join(['\x00' for x in range(len(m.getReducedStringData()) / 2)])  # The alignement == "\x00" * len(the message), the first time
##                    print "".join(['\x00' for x in range(len(m.getReducedStringData()) / 2)]).encode("hex")

        

    def retrieveMaxIJ(self):
        return self.retrieveEffectiveMaxIJ()

    def mergeSymbols(self):
        self.mergeEffectiveSymbols()

    def mergeEffectiveSymbols(self):
        # retrieves the following parameters from the configuration file
        nbIteration = self.configuration.getVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_NB_ITERATION)
        min_equivalence = self.configuration.getVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_EQUIVALENCE_THRESHOLD)
        self.log.debug("Re-Organize the symbols (nbIteration={0}, min_equivalence={1})".format(nbIteration, min_equivalence))

        gobject.idle_add(self.resetProgressBar)
        progressionStep = 1.0 / nbIteration
        for iteration in range(0, nbIteration):
            self.log.debug("Iteration {0} started...".format(str(iteration)))
            # Create the score matrix for each symbol
            (i_maximum, j_maximum, maximum) = self.retrieveEffectiveMaxIJ()

            """
            ## Just for debug purpose
            for symbol in self.symbols:
                symbol.buildRegexAndAlignment()
                compiledRegex = re.compile("".join(symbol.getRegex()))
                for message in symbol.getMessages():
#                    print message.getStringData()
                    data = message.getStringData()
                    m = compiledRegex.match(data)
                    if m == None:
                        print "".join(symbol.getRegex())
                        print message.getStringData()
                        print "PAN"
                    else:
                        pass
            """

            gobject.idle_add(self.doProgressBarStep, progressionStep)
            self.log.debug("Searching for the maximum of equivalence.")
            if (maximum >= min_equivalence):
                self.log.info("Merge the column/line {0} with the column/line {1} ; score = {2}".format(str(i_maximum), str(j_maximum), str(maximum)))
                self.mergeEffectiveRowCol(i_maximum, j_maximum)
            else:
                self.log.info("Stopping the clustering operation since the maximum found is {0} (<{1})".format(str(maximum), str(min_equivalence)))
                break

        # Compute the regex/alignment of each symbol
        gobject.idle_add(self.resetProgressBar)
        if len(self.symbols) == 0:
            progressionStep = 1.0
        else:
            progressionStep = 1.0 / len(self.symbols)
        for g in self.symbols:
            g.buildRegexAndAlignment(self.configuration)
            gobject.idle_add(self.doProgressBarStep, progressionStep)
        gobject.idle_add(self.resetProgressBar)

    #+----------------------------------------------
    #| mergeOrphanSymbols:
    #|   try to merge orphan symbols by progressively
    #|   reducing the taken into account size of msgs
    #+----------------------------------------------
    def mergeOrphanSymbols(self):
        self.log.debug("Merge the orphan symbols computed")

        leftReductionFactor = 0
        rightReductionFactor = 0
        currentReductionIsLeft = False
        increment = 10

        while leftReductionFactor < 80 and rightReductionFactor < 80:

            # First we retrieve the current orphans
            orphans = []
            tmp_symbols = []
            # extract orphans
            for symbol in self.symbols:
                if len(symbol.getMessages()) == 1:
                    orphans.append(symbol)
            # create a tmp symbols array where symbols will be added once computed
            for symbol in self.symbols:
                if len(symbol.getMessages()) > 1:
                    tmp_symbols.append(symbol)

            if len(orphans) <= 1:
                self.log.info("Number of orphan symbols : {0}. The orphan merging op. is finished !".format(len(orphans)))
                break

            self.symbols = orphans
            if currentReductionIsLeft:
                leftReductionFactor = leftReductionFactor + increment
                # Reduce the size of the messages by 50% from the left
                for orphan in self.symbols:
                    orphan.getMessages()[0].setLeftReductionFactor(leftReductionFactor)

                self.log.warning("Start to merge orphans reduced by {0}% from the left".format(str(leftReductionFactor)))
                self.mergeEffectiveSymbols()
                currentReductionIsLeft = False

            if not currentReductionIsLeft:
                rightReductionFactor = rightReductionFactor + increment
                # Reduce the size of the messages from the right
                for orphan in self.symbols:
                    orphan.getMessages()[0].setRightReductionFactor(rightReductionFactor)

                self.log.warning("Start to merge orphans reduced by {0}% from the right".format(str(rightReductionFactor)))
                self.mergeEffectiveSymbols()
                currentReductionIsLeft = True

            for orphan in self.symbols:
                tmp_symbols.append(orphan)
            self.symbols = tmp_symbols

        # Compute the regex/alignment of each symbol
        gobject.idle_add(self.resetProgressBar)
        progressionStep = 1.0 / len(self.symbols)
        for g in self.symbols:
            g.buildRegexAndAlignment()
            gobject.idle_add(self.doProgressBarStep, progressionStep)
        gobject.idle_add(self.resetProgressBar)

    #+----------------------------------------------
    #| mergeRowCol:
    #|   Merge the symbols i and j in the "symbols" structure
    #+----------------------------------------------
    def mergeEffectiveRowCol(self, i_maximum, j_maximum):
        # Extract symbols i and j
        if i_maximum > j_maximum:
            symbol1 = self.symbols.pop(i_maximum)
            symbol2 = self.symbols.pop(j_maximum)
        else:
            symbol1 = self.symbols.pop(j_maximum)
            symbol2 = self.symbols.pop(i_maximum)

        # Merge the symbols i and j
        messages = []
        messages.extend(symbol1.getMessages())
        messages.extend(symbol2.getMessages())

        newSymbol = Symbol(str(uuid.uuid4()), "Symbol", self.project)
        for message in messages:
            newSymbol.addMessage(message)

        # Append th new symbol to the "symbols" structure
        self.symbols.append(newSymbol)

    def mergeRowCol(self, i_maximum, j_maximum):
        self.mergeEffectiveRowCol(i_maximum, j_maximum)

    #+----------------------------------------------
    #| doProgressBarStep:
    #+----------------------------------------------
    def doProgressBarStep(self, step):
        pass
#        new_val = self.netzob.progressBar.get_fraction() + step
#        self.netzob.progressBar.set_fraction(new_val)

    #+----------------------------------------------
    #| resetProgressBar:
    #+----------------------------------------------
    def resetProgressBar(self):
        pass
#        self.netzob.progressBar.set_fraction(0)

    #+----------------------------------------------
    #| GETTER/SETTER:
    #+----------------------------------------------
    def getSymbols(self):
        return self.symbols

    def getProject(self):
        return self.project
