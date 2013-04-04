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
from netzob.Common.C_Extensions.WrapperArgsFactory import WrapperArgsFactory

#+---------------------------------------------------------------------------+
#| C Imports
#+---------------------------------------------------------------------------+
from netzob import _libNeedleman


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
        self.logger = logging.getLogger('netzob.Inference.Vocabulary.NeedlemanAndWunsch.py')

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

        if self.cb_status is not None:
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
            self.logger.debug("The field '" + field.getName() + "' is empty. No alignment needed")
            field.setRegex("(.{,})")
        else:
            if self.isFinish():
                return

            # We execute the alignment
            (alignment, semanticTags, score) = self.alignData(field.getCells(), field.getSemanticTags())

            if self.isFinish():
                return

            field.setAlignment(alignment)
            self.logger.debug("Alignment: {0}".format(alignment))

            # We update the regex based on the results
            try:
                if self.isFinish():
                    return
                self.buildRegexFromAlignment(field, alignment, semanticTags)

            except NetzobException, e:
                self.logger.warn("Partitionnement error: {0}".format(e))
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
    def alignData(self, data, semanticTokens):
        toSend = []
        for i in range(0, len(data)):
            toSend.append((data[i], semanticTokens[i]))

        wrapper = WrapperArgsFactory("_libNeedleman.alignMessages")
        wrapper.typeList[wrapper.function](toSend)

        debug = False
        (score1, score2, score3, regex, mask, semanticTags) = _libNeedleman.alignMessages(self.doInternalSlick, self.cb_executionStatus, debug, wrapper)
        scores = (score1, score2, score3)

        if self.isFinish():
            return

        alignment = TypeConvertor.deserializeAlignment(regex, mask, self.unitSize)
        semanticTags = TypeConvertor.deserializeSemanticTags(semanticTags, self.unitSize)

        self.logger.debug("Computed Alignment = {0}".format(alignment))

        alignment = self.smoothAlignment(alignment)
        self.logger.debug("Smoothed Alignment = {0}".format(alignment))
        return (alignment, semanticTags, scores)

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
    def buildRegexFromAlignment(self, field, align, semanticTags):
        # Build regex from alignment
        i = 0
        start = 0
        regex = []
        found = False
        currentTag = None

        # STEP 1 : Create a field separation
        # based on static and dynamic fields
        for i, val in enumerate(align):
            tag = semanticTags[i]
            if currentTag is None:
                currentTag = tag

            if self.isFinish():
                return

            if (val == "-"):
                if (found is False):
                    start = i
                    found = True
            else:
                if (found is True):
                    found = False
                    nbTiret = i - start
                    regex.append(".{," + str(nbTiret) + "}")
                    regex.append(val)
                else:
                    if len(regex) == 0:
                        regex.append(val)
                    else:
                        regex[-1] += val

        if (found is True):
            nbTiret = i - start + 1
            regex.append(".{," + str(nbTiret) + "}")

        # We have a computed the 'simple' regex,
        # and represent it using the field representation
        iField = 0
        step1Fields = []
        for regexElt in regex:
            if self.isFinish():
                return
            if regexElt == "":
                pass
            innerField = Field("Field " + str(iField), "(" + regexElt + ")", field.getSymbol())
            step1Fields.append(innerField)
            field.addLocalField(innerField)

            # Use the default protocol type for representation
            field.setFormat(self.defaultFormat)
            iField = iField + 1
        if len(field.getSymbol().getExtendedFields()) >= 100:
            raise NetzobException("This Python version only supports 100 named groups in regex (found {0})".format(len(field.getSymbol().getExtendedFields())))

        # STEP 2 : Split fields given the semantic tokens
        totalIndex = 0

        # Starts to consider semantic tags
        step2Fields = dict()

        startByteCurrentField = 0
        for iField, step1Field in enumerate(step1Fields):
            step2Fields[step1Field] = []

            lengthField = 0
            # Compute the size of the current field given its regex
            if step1Field.isStatic():
                lengthField = len(step1Field.getRegex()) - 2
            else:
                tmp = step1Field.getRegex().split(',')[1]
                lengthField = int(tmp[:len(tmp) - 2])

            # Split the current field if a modification of the semantic tag can be found
            sizeCurrentField = 0
            tagCurrentField = None
            startLastSubField = 0
            iSubField = 0
            for currentByteInCurrentField in range(0, lengthField):
                tagCurrentByte = semanticTags[startByteCurrentField + currentByteInCurrentField]

                if tagCurrentField != tagCurrentByte:
                    if sizeCurrentField > 0:
                        sizeCurrentField += 1
                        if not step1Field.isStatic():
                            # create a sub field dynamic
                            regex = "(.{," + str(sizeCurrentField) + "}):" + str(tagCurrentField)
                        else:
                            regex = "({0}):{1}".format(step1Field.getRegex()[1 + startLastSubField:1 + startLastSubField + sizeCurrentField], tagCurrentField)
                        step2Fields[step1Field].append(Field("{0}_{1}".format(step1Field.getName(), iSubField), regex, step1Field.getSymbol()))
                        startLastSubField = startLastSubField + sizeCurrentField
                        sizeCurrentField = 0
                    tagCurrentField = tagCurrentByte
                else:
                    sizeCurrentField += 1

            if sizeCurrentField > 0:
                if not step1Field.isStatic():
                    # create a sub field dynamic
                    sizeCurrentField += 1
                    regex = "(.{," + str(sizeCurrentField) + "}):" + tagCurrentByte
                else:
                    regex = "({0}):{1}".format(step1Field.getRegex()[1 + startLastSubField:sizeCurrentField + 2], tagCurrentByte)
                step2Fields[step1Field].append(Field("{0}_{1}".format(step1Field.getName(), iSubField), regex, step1Field.getSymbol()))
            startByteCurrentField += lengthField

        # STEP 3 : Apply semantic field partitionning computed in previous step
        # and create a nice regex
        steps3Fields = []
        for f1 in step1Fields:
            f2 = step2Fields[f1]
            if len(f2) == 1:
                steps3Fields.append(f1)
            else:
                for f in f2:
                    tmpSplit = f.getRegex().split(':')
                    tag = tmpSplit[1]
                    if tag != "None":
                        # get all the possible values in f1 of data under specified tag
                        semanticTagsForField = f1.getSemanticTagsByMessage()
                        possibleValues = []
                        for message, semanticTagsInMessage in semanticTagsForField.items():
                            currentValue = []
                            for localPosition in sorted(semanticTagsInMessage.iterkeys()):
                                tagValue = semanticTagsInMessage[localPosition]
                                if tagValue == tag:
                                    currentValue.append(message.getStringData()[localPosition])
                            possibleValues.append(''.join(currentValue))
                        newRegex = '|'.join(possibleValues)
                        newRegex = "({0})".format(newRegex)
                        f.setRegex(newRegex)
                    else:
                        f.setRegex(tmpSplit[0])
                    steps3Fields.append(f)

        field.removeLocalFields()
        for f in steps3Fields:
            field.addLocalField(f)

        # Clean created fields (remove fields that produce only empty cells)
        field.removeEmptyFields(self.cb_status)

        # Rename the fields
        iField = 0
        for field in field.getSymbol().getExtendedFields():
            field.setName("F{0}".format(iField))
            iField += 1

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
                self.logger.debug("Symbol {0} [{1}] wont be aligned".format(str(symbol.getName()), str(symbol.getID())))
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
        self.logger.info("Time of clustering: {0}".format(str(t2 - t1)))

    def isFinish(self):
        return self.flagStop

    def stop(self):
        self.flagStop = True
        if self.clusteringSolution is not None:
            self.logger.debug("Close the clustering solution")
            self.clusteringSolution.stop()

    def getNewSymbols(self):
        return self.newSymbols
