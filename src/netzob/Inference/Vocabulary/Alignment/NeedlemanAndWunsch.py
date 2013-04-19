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

            # We update the regex based on the results
            try:
                if self.isFinish():
                    return
                self.buildRegexFromAlignment(field, alignment, semanticTags)

            except NetzobException, e:
                self.logger.warn("Partitionnement error: {0}".format(e))
                field.resetPartitioning()

    #+-----------------------------------------------------------------------+
    #| alignData
    #|     Default alignment of messages
    #| @param messages a list of AbstractMessages
    #| @returns (alignment, score)
    #+-----------------------------------------------------------------------+
    def alignData(self, data, semanticTokens):
        toSend = []

        for i in range(0, len(data)):
            toSend.append((''.join(data[i]), semanticTokens[i]))

        wrapper = WrapperArgsFactory("_libNeedleman.alignMessages")
        wrapper.typeList[wrapper.function](toSend)

        debug = False
        (score1, score2, score3, regex, mask, semanticTags) = _libNeedleman.alignMessages(self.doInternalSlick, self.cb_executionStatus, debug, wrapper)
        scores = (score1, score2, score3)

        if self.isFinish():
            return

        alignment = TypeConvertor.deserializeAlignment(regex, mask, self.unitSize)
        semanticTags = TypeConvertor.deserializeSemanticTags(semanticTags, self.unitSize)

        alignment = self.smoothAlignment(alignment)
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
        """buildRegexFromAlignment:
        This methods creates a regex based on the computed alignment
        by the Needleman&Wunsch algorithm and the attached semantic tags.
        @param field : the field for which it creates the regex (and the sub fields)
        @param align : the string representing the common alignment between messages of the symbol.
        @param semanticTags : the list of tags attached to each half-bytes of the provided alignment."""

        DEBUG_MODE = False

        # First we clean the field
        field.removeLocalFields()

        # Create fields following the alignment
        self.splitFieldFollowingAlignment(field, align)

        if DEBUG_MODE:
            # Verify the computed 'simple' alignment is valid regarding messages
            logging.debug("\n {0}".format(field.getCells()))

        self.createSubFieldsFollowingSemanticTags(field, align, semanticTags)

        if DEBUG_MODE:
            # Verify the computed 'simple' alignment is valid regarding messages
            logging.debug("\n {0}".format(field.getCells()))

    def createSubFieldsFollowingSemanticTags(self, rootField, align, semanticTags):
        """createSubFieldsFollowingSemanticTags:
        In this method, we search for subfields which would be created because of
        semantic boundaries."""

        originalFields = rootField.getExtendedFields()

        if len(originalFields) == 1 and rootField == originalFields[0]:
            # We are dealing with a specific field
            logging.debug("Analyze sub fields for {0}".format(rootField.getRegex()))
            if rootField.isStatic():
                self.createSubFieldsForAStaticField(rootField, align, semanticTags)
            else:
                self.createSubFieldsForADynamicField(rootField, align, semanticTags)

            for f in rootField.getLocalFields():
                logging.debug("\t {0} : {1}".format(f.getName(), f.getRegex()))

        else:
            # We are dealing with multiple fields, lets split them
            currentIndex = 0

            for field in originalFields:
                regexField = field.getRegex()

                # Retrieve the size of the current field
                if field.isStatic():
                    lengthField = len(regexField) - 2
                else:
                    tmp = regexField.split(',')[1]
                    lengthField = int(tmp[:len(tmp) - 2])

                # Find semantic tags related to the current section
                sectionSemanticTags = dict((k, semanticTags[k]) for k in xrange(currentIndex, currentIndex + lengthField))

                # reccursive call
                logging.debug("Working on field : {0}".format(field.getName()))
                self.createSubFieldsFollowingSemanticTags(field, align[currentIndex:currentIndex + lengthField], sectionSemanticTags)

                currentIndex += lengthField

    def createSubFieldsForAStaticField(self, field, align, semanticTags):
        """createSubFieldsForAStaticField:
        Analyzes the static field provided and create sub fields following
        the provided semantic tags."""
        logging.debug("Create subfields for static field {0} : {1}".format(field.getName(), align))

        if len(field.getLocalFields()) > 0:
            logging.warning("Impossible to create sub fields for this field since its not cleaned")
            return

        subFields = []

        currentTag = None
        currentTagLength = 0

        for index, tag in semanticTags.iteritems():
            if tag != currentTag:
                # Create a sub field
                subFieldValue = align[index - currentTagLength:index]
                if len(subFieldValue) > 0:
                    subFields.append(subFieldValue)
                currentTagLength = 0
            currentTag = tag
            currentTagLength += 1
        if currentTagLength > 0:
            subFieldValue = align[-currentTagLength:]
            if len(subFieldValue) > 0:
                subFields.append(subFieldValue)

        if len(subFields) > 1:
            for iSubField, subFieldValue in enumerate(subFields):
                subField = Field("{0}_{1}".format(field.getName(), iSubField), "({0})".format(subFieldValue), field.getSymbol())
                field.addLocalField(subField)

    def createSubFieldsForADynamicField(self, field, align, semanticTags):
        """createSubFieldsForADynamicField:
        Analyzes the dynamic field provided and create sub fields following
        the provided semantic tags."""

        logging.debug("Create subfields for dynamic field {0} : {1}".format(field.getName(), field.getRegex()))

        if len(field.getLocalFields()) > 0:
            logging.warn("Impossible to create sub fields for this field since its not cleaned")
            return

        subFields = []

        currentTag = None
        currentTagLength = 0

        semanticTagsForEachMessage = field.getSemanticTagsByMessage()

        for index, tag in semanticTags.iteritems():
            if tag != currentTag:
                # Create a sub field
                if currentTagLength > 0:
                    values = self.getFieldValuesWithTag(field, semanticTagsForEachMessage, currentTag)
                    subFields.append((currentTag, values))
                currentTagLength = 0
            currentTag = tag
            currentTagLength += 1
        if currentTagLength > 0:
            values = self.getFieldValuesWithTag(field, semanticTagsForEachMessage, currentTag)
            subFields.append((currentTag, values))

        for iSubField, (tag, values) in enumerate(subFields):
            if len(values) > 0:
                if tag == "None":
                    minValue = None
                    maxValue = None
                    for v in values:
                        if minValue is None or len(v) < minValue:
                            minValue = len(v)
                        if maxValue is None or len(v) > maxValue:
                            maxValue = len(v)
                    subField = Field("{0}_{1}".format(field.getName(), iSubField), "(.{" + str(minValue) + "," + str(maxValue) + "})", field.getSymbol())

                    field.addLocalField(subField)
                else:
                    # create regex based on unique values
                    newRegex = '|'.join(list(set(values)))
                    newRegex = "({0})".format(newRegex)
                    subField = Field("{0}_{1}".format(field.getName(), iSubField), newRegex, field.getSymbol())
                    field.addLocalField(subField)

    def getFieldValuesWithTag(self, field, semanticTagsForEachMessage, tag):
        values = []

        # Retrieve value of each message in current field tagged with requested tag
        for message, tagsInMessage in semanticTagsForEachMessage.iteritems():
            initial = None
            end = None

            for tagIndex in sorted(tagsInMessage.keys()):
                tagName = tagsInMessage[tagIndex]
                if initial is None and tagName == tag:
                    initial = tagIndex
                elif initial is not None and tagName != tag:
                    end = tagIndex
                    break

            if initial is not None and end is None:
                end = sorted(tagsInMessage.keys())[-1] + 1
            if initial is not None and end is not None:
                values.append(message.getStringData()[initial:end])

                for i in range(initial, end):
                    del tagsInMessage[i]

        if "" not in values and len(semanticTagsForEachMessage.keys()) > len(values):
            values.append("")

        return values

    def splitFieldFollowingAlignment(self, field, align):
        # Build regex from alignment
        i = 0
        start = 0
        regex = []
        found = False

        # STEP 1 : Create a field separation
        # based on static and dynamic fields
        logging.debug("Step 1 : Create field separation based on static and dynamic data")
        for i, val in enumerate(align):
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
        logging.debug("Computed regex : {0}".format(regex))

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
