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
#| File contributors :                                                       |
#|       - Georges Bossert <georges.bossert (a) supelec.fr>                  |
#|       - Frédéric Guihéry <frederic.guihery (a) amossys.fr>                |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Global Imports
#+---------------------------------------------------------------------------+
import logging
import time
from gettext import gettext as _
import uuid

#+---------------------------------------------------------------------------+
#| Local Imports
#+---------------------------------------------------------------------------+
from netzob.Common.Type.TypeConvertor import TypeConvertor
from netzob.Common.Field import Field
from netzob.Common.Symbol import Symbol
from netzob.Common.ProjectConfiguration import ProjectConfiguration
from netzob.Common.NetzobException import NetzobException

#+---------------------------------------------------------------------------+
#| C Imports
#+---------------------------------------------------------------------------+
from netzob import _libNeedleman
from netzob import _libInterface


#+---------------------------------------------------------------------------+
#| NeedlemanAndWunsch:
#|     Supports the use of N&W alignment in Netzob
#+---------------------------------------------------------------------------+
class NeedlemanAndWunsch(object):

    def __init__(self, unitSize, project, doUpgma, cb_status=None):
        self.cb_status = cb_status
        self.project = project
        self.unitSize = unitSize
        self.scores = {}
        self.absoluteStage = None
        self.statusRatio = None
        self.statusRatioOffset = None
        self.flagStop = False
        self.clusteringSolution = None
        self.doUpgma = doUpgma
        self.newSymbols = []

        # Then we retrieve all the parameters of the CLUSTERING / ALIGNMENT
        self.defaultFormat = self.project.getConfiguration().getVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_GLOBAL_FORMAT)
        self.nbIteration = self.project.getConfiguration().getVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_NB_ITERATION)
        self.minEquivalence = self.project.getConfiguration().getVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_EQUIVALENCE_THRESHOLD)
        self.doInternalSlick = self.project.getConfiguration().getVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_DO_INTERNAL_SLICK)
        self.doOrphanReduction = self.project.getConfiguration().getVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_ORPHAN_REDUCTION)

    #+-----------------------------------------------------------------------+
    #| cb_executionStatus
    #|     Callback function called by the C extension to provide info on status
    #| @param donePercent a float between 0 and 100 included
    #| @param currentMessage a str which represents the current alignment status
    #+-----------------------------------------------------------------------+
    def cb_executionStatus(self, stage, donePercent, currentMessage):
        if self.absoluteStage is not None:
            stage = self.absoluteStage

        totalPercent = donePercent
        if self.statusRatio is not None:
            totalPercent = totalPercent / self.statusRatio
            if self.statusRatioOffset is not None:
                totalPercent = totalPercent + 100 / self.statusRatio * self.statusRatioOffset

        if self.cb_status is None:
            print "[Alignment status] " + str(totalPercent) + "% " + currentMessage
        else:
            self.cb_status(stage, totalPercent, currentMessage)

    #+-----------------------------------------------------------------------+
    #| alignField
    #|     Default alignment of messages declared in a Symbol/Field
    #| @param the symbol
    #+-----------------------------------------------------------------------+
    def alignField(self, field):
        messages = field.getMessages()
        field.resetPartitioning()
        field.removeLocalFields()
        if messages is None or len(messages) == 0:
            logging.debug("The field '" + field.getName() + "' is empty. No alignment needed")
            field.setRegex("(.{,})")
        else:
            if self.isFinish():
                return

            # We execute the alignment
            (alignment, score) = self.alignData(field.getCells())

            if self.isFinish():
                return

            field.setAlignment(alignment)
            logging.debug("Alignment: {0}".format(alignment))

            # We update the regex based on the results
            try:
                if self.isFinish():
                    return
                self.buildRegexFromAlignment(field, alignment)

            except NetzobException, e:
                logging.warn("Partitionnement error: {0}".format(e))
                field.resetPartitioning()

            # Last loop to detect fixed-sized dynamic fields
            for innerField in field.getLocalFields():
                innerField.fixRegex()

    #+-----------------------------------------------------------------------+
    #| alignData
    #|     Default alignment of messages
    #| @param messages a list of AbstractMessages
    #| @returns (alignment, score)
    #+-----------------------------------------------------------------------+
    def alignData(self, data):
        # First we serialize the two messages
        (serialValues, format) = TypeConvertor.serializeValues(data, self.unitSize)

        debug = False
        (score1, score2, score3, regex, mask) = _libNeedleman.alignMessages(self.doInternalSlick, len(data), format, serialValues, self.cb_executionStatus, debug)
        scores = (score1, score2, score3)

        if self.isFinish():
            return

        alignment = self.deserializeAlignment(regex, mask)
        alignment = self.smoothAlignment(alignment)
        return (alignment, scores)

    #+-----------------------------------------------------------------------+
    #| deserializeAlignment
    #|     Transforms the C extension results in a python readable way
    #| @param regex the C returned regex
    #| @param mask the C returned mask
    #| @returns the python alignment
    #+-----------------------------------------------------------------------+
    def deserializeAlignment(self, regex, mask):
        align = ""
        i = 0
        for c in mask:
            if c != '\x02':
                if c == '\x01':
                    if self.unitSize == 8:
                        align += "--"
                    elif self.unitSize == 4:
                        align += "-"
                    else:
                        logging.warn("Deserializing at " + str(self.unitSize) + " unit size not yet implemented")
                else:
                    if self.unitSize == 8:
                        align += regex[i:i + 1].encode("hex")
                    elif self.unitSize == 4:
                        align += regex[i:i + 1].encode("hex")[1:]
                    else:
                        logging.warn("Deserializing at " + str(self.unitSize) + " unit size not yet implemented")
            i += 1
        return align

    #+-----------------------------------------------------------------------+
    #| smoothAlignment:
    #|     Try to smooth the given alignment
    #| @param alignment The sequence alignment result
    #| @returns The smoothed alignment
    #+-----------------------------------------------------------------------+
    def smoothAlignment(self, alignment):
        result = ""
        nbLetters = self.unitSize / 4
        for i in range(0, len(alignment), nbLetters):
            tmpText = alignment[i:i + nbLetters]
            if tmpText.count("-") >= 1:
                for j in range(len(tmpText)):
                    result += "-"
            else:
                result += tmpText
        return result

    #+-----------------------------------------------------------------------+
    #| buildRegexFromAlignment
    #|     Transform the alignment in a regular expression
    #| @param field the associated field
    #| @param align the given alignment
    #+-----------------------------------------------------------------------+
    def buildRegexFromAlignment(self, field, align):
        # Build regex from alignment
        i = 0
        start = 0
        regex = []
        found = False
        for i in range(len(align)):

            if self.isFinish():
                return

            if (align[i] == "-"):
                if (found is False):
                    start = i
                    found = True
            else:
                if (found is True):
                    found = False
                    nbTiret = i - start
                    regex.append(".{," + str(nbTiret) + "}")
                    regex.append(align[i])
                else:
                    if len(regex) == 0:
                        regex.append(align[i])
                    else:
                        regex[-1] += align[i]
        if (found is True):
            nbTiret = i - start + 1
            regex.append(".{," + str(nbTiret) + "}")

        iField = 0
        logging.debug("REGEX " + str(regex))
        for regexElt in regex:
            if self.isFinish():
                return
            if regexElt == "":
                pass
            innerField = Field("Field " + str(iField), "(" + regexElt + ")", field.getSymbol())
            field.addField(innerField)

            # Use the default protocol type for representation
            field.setFormat(self.defaultFormat)
            iField = iField + 1
        if len(field.getSymbol().getExtendedFields()) >= 100:
            raise NetzobException("This Python version only supports 100 named groups in regex (found {0})".format(len(field.getSymbol().getExtendedFields())))

        # Clean created fields (remove fields that produce only empty cells)
        field.removeEmptyFields(self.cb_status)

    #+----------------------------------------------
    #| alignFields:
    #|  Align each messages of each symbol with the
    #|  Needleman Wunsh algorithm
    #+----------------------------------------------
    def alignFields(self, fields):
        # If we apply basic alignment per field
        if self.doUpgma is False:
            for field in fields:
                self.alignField(field)
            return

        # Else we apply UPGMA
        from netzob.Inference.Vocabulary.Alignment.UPGMA import UPGMA
        self.newSymbols = []
        preResults = []

        # First we add in results, the symbols which wont be aligned
        for symbol in self.project.getVocabulary().getSymbols():
            found = False
            for field in fields:
                if str(symbol.getID()) == str(field.getSymbol().getID()):
                    found = True
            if not found:
                logging.debug("Symbol {0} [{1}] wont be aligned".format(str(symbol.getName()), str(symbol.getID())))
                preResults.append(symbol)

        # Create a symbol for each message
        tmpSymbols = []
        i_field = 1
        for field in fields:
            for m in field.getMessages():
                tmpSymbol = Symbol(str(uuid.uuid4()), "Symbol-" + str(i_field), self.project)
                tmpField = Field("Field-" + str(i_field), "(.{,})", tmpSymbol)
                tmpSymbol.addMessage(m)
                tmpSymbol.setField(tmpField)
                tmpSymbols.append(tmpSymbol)
                i_field += 1

        self.clusteringSolution = UPGMA(self.project, tmpSymbols, self.unitSize, self.cb_executionStatus)
        t1 = time.time()
        self.newSymbols = self.clusteringSolution.executeClustering()

        if self.isFinish():
            return

        # We optionally handle orphans
        if self.doOrphanReduction:
            self.newSymbols = self.clusteringSolution.executeOrphanReduction()
        t2 = time.time()

        self.newSymbols.extend(preResults)
        logging.info("Time of clustering: {0}".format(str(t2 - t1)))

    def isFinish(self):
        return self.flagStop

    def stop(self):
        self.flagStop = True
        if self.clusteringSolution is not None:
            logging.debug("Close the clustering solution")
            self.clusteringSolution.stop()

    def getNewSymbols(self):
        return self.newSymbols

    #+-----------------------------------------------------------------------+
    #| alignTwoMessages
    #|     Default alignment of two messages
    #| @param message1 the first message to align
    #| @param message2 the second message to align
    #| @returns (alignment, score)
    #+-----------------------------------------------------------------------+
    def alignTwoMessages(self, message1, message2):
        # First we serialize the two messages
        (serialMessages, format) = TypeConvertor.serializeMessages([message1, message2], self.unitSize)

        debug = False
        (score1, score2, score3, regex, mask) = _libNeedleman.alignTwoMessages(self.doInternalSlick, format, serialMessages, debug)
        scores = (score1, score2, score3)
        alignment = self.deserializeAlignment(regex, mask)
        return (scores, alignment)

    #+-----------------------------------------------------------------------+
    #| deserializeMessages
    #|     Useless (functionally) function created for testing purposes
    #| @param messages a list of AbstractMessages
    #| @returns number Of Deserialized Messages
    #+-----------------------------------------------------------------------+
    def deserializeMessages(self, messages):
        # First we serialize the messages
        (serialMessages, format) = TypeConvertor.serializeMessages(messages, self.unitSize)
        debug = False
        return _libInterface.deserializeMessages(len(messages), format, serialMessages, debug)
