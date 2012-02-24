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
import gtk
from operator import attrgetter
import re
import glib
import struct
from lxml.etree import ElementTree
from lxml import etree
#import pyasn1.codec.der.decoder
#from pyasn1.error import PyAsn1Error
#from pyasn1.error import SubstrateUnderrunError

#+---------------------------------------------------------------------------+
#| Local Imports
#+---------------------------------------------------------------------------+
from netzob.Common.Models.Factories.AbstractMessageFactory import AbstractMessageFactory
from netzob.Common.Field import Field
from netzob.Common.ProjectConfiguration import ProjectConfiguration
from netzob.Common.Type.TypeIdentifier import TypeIdentifier
from netzob.Common.Type.TypeConvertor import TypeConvertor
from netzob.Common.NetzobException import NetzobException
from netzob.Common.MMSTD.Dictionary.Variables.AggregateVariable import AggregateVariable
from netzob.Common.MMSTD.Symbols.AbstractSymbol import AbstractSymbol

#+----------------------------------------------
#| C Imports
#+----------------------------------------------
import libNeedleman

NAMESPACE = "http://www.netzob.org/"

# Note: this is probably useless, as it is already specified in Project.py
PROJECT_NAMESPACE = "http://www.netzob.org/project"
COMMON_NAMESPACE = "http://www.netzob.org/common"

#+---------------------------------------------------------------------------+
#| Symbol:
#|     Class definition of a symbol
#+---------------------------------------------------------------------------+
class Symbol(AbstractSymbol):

    #+-----------------------------------------------------------------------+
    #| Constructor
    #+-----------------------------------------------------------------------+
    def __init__(self, id, name, project):
        AbstractSymbol.__init__(self, "Symbol")
        self.id = id
        self.name = name
        self.alignment = ""
        self.score = 0.0
        self.messages = []
        self.fields = []
        self.alignmentType = "regex"
        self.rawDelimiter = ""
        self.project = project

#    #+----------------------------------------------
#    #| buildRegexAndAlignment : compute regex and
#    #| self.alignment from the binary strings computed
#    #| in the C Needleman library
#    #+----------------------------------------------
#    def buildRegexAndAlignment(self, projectConfiguration):
#        self.alignmentType = "regex"
#        self.rawDelimiter = ""
#        # Use the default protocol type for representation
#        aFormat = projectConfiguration.getVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_GLOBAL_FORMAT)
#
#        self.fields = []
#
#        # If only one message (easy)
#        if len(self.getMessages()) == 1:
#            field = Field("Field 0", 0, self.getMessages()[0].getStringData())
#            field.setFormat(aFormat)
#            self.addField(field)
#            return
#
#        # If more messages, we align them
#        # Serialize the messages before sending them to the C library
#        (serialMessages, format) = TypeConvertor.serializeMessages(self.getMessages())
#        
#        maxLeftReducedStringData = 0
#        maxRightReducedStringData = 0
#        maxReducedSize = 0
#        for m in self.getMessages():
#            if m.getLeftReductionFactor() > maxLeftReducedStringData:
#                maxLeftReducedStringData = m.getLeftReductionFactor()
#            if m.getRightReductionFactor() > maxRightReducedStringData:
#                maxRightReducedStringData = m.getRightReductionFactor()
#            if m.getReducedSize() > maxReducedSize:
#                maxReducedSize = m.getReducedSize()
#
#        if projectConfiguration.getVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_DO_INTERNAL_SLICK):
#            doInternalSlick = 1
#        else:
#            doInternalSlick = 0
#
#        # Align sequences in C library
#        logging.debug("Alignment with : ")
#        logging.debug("internal slick = " + str(doInternalSlick))
#        logging.debug("len messages : " + str(len(self.getMessages())))
#        logging.debug("format = " + format)
#        logging.debug("serial = " + serialMessages)
#        
#        (score, aRegex, aMask) = libNeedleman.alignSequences(doInternalSlick, len(self.getMessages()), format, serialMessages)
#        
#        self.setScore(score)
#
#        # Build alignment C library result
#        align = ""
#        i = 0
#        for c in aMask:
#            if c != '\x02':
#                if c == '\x01':
#                    align += "--"
#                else:
#                    align += aRegex[i:i + 1].encode("hex")
#            i += 1
#
#        if maxLeftReducedStringData > 0:
#            logging.warning("add on the left part adding a bit of --")
#            for i in range(0, maxReducedSize):
#                align = "--" + align
#        if maxRightReducedStringData > 0:
#            logging.warning("add on the right part adding a bit of --")
#            for i in range(0, maxReducedSize):
#                align = align + "--"
#
#        self.setAlignment(align)
#        # Initialized the self.fields structure based on alignement
#        self.buildRegexFromAlignment(align, projectConfiguration)

#    def buildRegexFromAlignment(self, align, projectConfiguration):
#        # Build regex from alignment
#        i = 0
#        start = 0
#        regex = []
#        found = False
#        for i in range(len(align)):
#            if (align[i] == "-"):
#                if (found == False):
#                    start = i
#                    found = True
#            else:
#                if (found == True):
#                    found = False
#                    nbTiret = i - start
#                    regex.append("(.{," + str(nbTiret) + "})")
#                    regex.append(align[i])
#                else:
#                    if len(regex) == 0:
#                        regex.append(align[i])
#                    else:
#                        regex[-1] += align[i]
#        if (found == True):
#            nbTiret = i - start
#            regex.append("(.{," + str(nbTiret) + "})")
#
#        # Use the default protocol type for representation
#        aFormat = projectConfiguration.getVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_GLOBAL_FORMAT)
#
#        iField = 0
#        for regexElt in regex:
#            field = Field("Field " + str(iField), iField, regexElt)
#            field.setFormat(aFormat)
#            self.addField(field)
#            iField = iField + 1
#
#        # We look for useless fields
#        doLoop = True
#        # We loop until we don't pop any field
#        while doLoop == True:
#            doLoop = False
#            for field in self.getFields():
#                # We try to see if this field produces only empty values when applied on messages
#                messagesValuesByField = self.getMessagesValuesByField(field)
#                messagesValuesByField = "".join(messagesValuesByField)
#                if messagesValuesByField == "":
#                    self.getFields().pop(field.getIndex())  # We remove this useless field
#                    # Adpat index of the following fields, before breaking
#                    for fieldNext in self.getFields():
#                        if fieldNext.getIndex() > field.getIndex():
#                            fieldNext.setIndex(fieldNext.getIndex() - 1)
#                    doLoop = True
#                    break

    #+----------------------------------------------
    #| forcePartitioning:
    #|  Specify a delimiter for partitioning
    #+----------------------------------------------
    def forcePartitioning(self, projectConfiguration, aFormat, rawDelimiter):
        self.alignmentType = "delimiter"
        self.rawDelimiter = rawDelimiter
        self.setFields([])

        minNbSplit = 999999
        maxNbSplit = -1
        for message in self.getMessages():
            tmpStr = message.getStringData().split(rawDelimiter)
            minNbSplit = min(minNbSplit,
                             len(tmpStr))
            maxNbSplit = max(maxNbSplit,
                             len(tmpStr))
        if minNbSplit <= 1:  # If the delimiter does not create splitted fields
            field = Field("Name", 0, "(.{,})")
            field.setFormat(aFormat)
            field.setColor("blue")
            self.addField(field)
            return

        # Else, we add (maxNbSplit + maxNbSplit - 1) fields
        iField = -1
        for i in range(maxNbSplit):
            iField += 1
            field = Field("Name", iField, "(.{,})")
            field.setFormat(aFormat)
            field.setColor("blue")
            self.addField(field)
            iField += 1
            field = Field("__sep__", iField, self.getRawDelimiter())
            field.setFormat(aFormat)
            field.setColor("black")
            self.addField(field)
        self.popField()

    #+----------------------------------------------
    #| simplePartitioning:
    #|  Do message partitioning according to column variation
    #+----------------------------------------------
    def simplePartitioning(self, projectConfiguration, unitSize):
        self.alignmentType = "regex"
        self.rawDelimiter = ""
        self.setFields([])

        # Retrieve the biggest message
        maxLen = 0
        for message in self.getMessages():
            curLen = len(message.getStringData())
            if curLen > maxLen:
                maxLen = curLen

        # Try to see if the column is static or variable
        resultString = ""
        resultMask = ""
        # Loop until maxLen
        for it in range(maxLen):
            ref = ""
            isDifferent = False
            # Loop through each cells of the column
            for message in self.getMessages():
                try:
                    tmp = message.getStringData()[it]
                    if ref == "":
                        ref = tmp
                    if ref != tmp:
                        isDifferent = True
                        break
                except IndexError:
                    isDifferent = True
                    pass

            if isDifferent:
                resultString += "-"
                resultMask += "1"
            else:
                resultString += ref
                resultMask += "0"

        ## Build of the fields
        currentStaticField = ""
        if resultMask[0] == "1":  # The first column is dynamic
            isLastDyn = True
        else:
            currentStaticField += resultString[0]
            isLastDyn = False

        nbElements = 1
        iField = -1
        for it in range(1, len(resultMask)):
            if resultMask[it] == "1": # The current column is dynamic
                if isLastDyn:
                    nbElements += 1
                else:
                    # We change the field
                    iField += 1
                    field = Field("Name", iField, currentStaticField)
                    field.setColor("black")
                    self.addField(field)
                    # We start a new field
                    currentStaticField = ""
                    nbElements = 1
                isLastDyn = True
            else:  # The current column is static
                if isLastDyn:  # We change the field
                    iField += 1
                    field = Field("Name", iField, "(.{," + str(nbElements) + "})")
                    field.setColor("blue")
                    self.addField(field)
                    # We start a new field
                    currentStaticField = resultString[it]
                    nbElements = 1
                else:
                    currentStaticField += resultString[it]
                    nbElements += 1
                isLastDyn = False

        # We add the last field
        iField += 1
        if resultMask[-1] == "1":  # If the last column is dynamic
            field = Field("Name", iField, "(.{," + str(nbElements) + "})")
            field.setColor("blue")
        else:
            field = Field("Name", iField, currentStaticField)
            field.setColor("black")
        self.addField(field)

    #+----------------------------------------------
    #| freezePartitioning:
    #|   
    #+----------------------------------------------
    def freezePartitioning(self):
        for field in self.getFields():
            tmpRegex = field.getRegex()
            if field.isStatic():
                continue
            elif field.isRegexOnlyDynamic():
                cells = self.getMessagesValuesByField(field)
                if len(cells) != len(self.getMessages()):
                    # There exists empty cells
                    continue
                min = 999999
                max = 0
                for cell in cells:
                    if len(cell) > max:
                        max = len(cell)
                    if len(cell) < min:
                        min = len(cell)
                if min == max:
                    field.setRegex("(.{" + str(min) + "})")
                else:
                    field.setRegex("(.{" + str(min) + "," + str(max) + "})")
            else:
                # TODO: handle complex regex
                continue

    #+----------------------------------------------
    #| getMessageByID:
    #|  Return the message which ID is provided
    #+----------------------------------------------
    def getMessageByID(self, messageID):
        for message in self.messages:
            if str(message.getID()) == str(messageID):
                return message

        return None

    #+----------------------------------------------
    #| getFieldByIndex:
    #|  Return the field with specified index
    #+----------------------------------------------
    def getFieldByIndex(self, index):
        return self.fields[index]

    #+----------------------------------------------
    #| getMessagesValuesByField:
    #|  Return all the messages parts which are in
    #|  the specified field
    #+----------------------------------------------
    def getMessagesValuesByField(self, field):
        # First we verify the field exists in the symbol
        if not field in self.fields:
            logging.warn("The computing field is not part of the current symbol")
            return []

        res = []
        for message in self.getMessages():
            messageTable = message.applyAlignment()
            messageElt = messageTable[field.getIndex()]
            res.append(messageElt)
#            if len(messageElt) > 0:
#                res.append(messageElt)
#            else:
#                res.append(None)
        return res

    #+----------------------------------------------
    #| getUniqValuesByField:
    #|  Return all the uniq cells of a field
    #+----------------------------------------------
    def getUniqValuesByField(self, field):
        # First we verify the field exists in the symbol
        if not field in self.fields:
            logging.warn("The computing field is not part of the current symbol")
            return []

        res = []
        for message in self.getMessages():
            messageTable = message.applyAlignment()
            messageElt = messageTable[field.getIndex()]
            if len(messageElt) > 0 and not messageElt in res:
                res.append(messageElt)
        return res

    #+----------------------------------------------
    #| concatFields:
    #|  Concatenate two fields starting from iField
    #+----------------------------------------------
    def concatFields(self, iField):
        field1 = None
        field2 = None
        for field in self.fields:
            if field.getIndex() == iField:
                field1 = field
            elif field.getIndex() == iField + 1:
                field2 = field
        # Build the merged regex
        newRegex = ""
        if field1.getRegex() == "":
            newRegex = field2.getRegex()
        if field2.getRegex() == "":
            newRegex = field1.getRegex()

        if field1.getRegex()[0] == "(" and field2.getRegex()[0] != "(":  # Dyn + Static fields
            newRegex = field1.getRegex()[:-1] + field2.getRegex() + ")"

        if field1.getRegex()[0] != "(" and field2.getRegex()[0] == "(":  # Static + Dyn fields
            newRegex = "(" + field1.getRegex() + field2.getRegex()[1:]

        if field1.getRegex()[0] == "(" and field2.getRegex()[0] == "(":  # Dyn + Dyn fields
            newRegex = field1.getRegex()[:-1] + field2.getRegex()[1:]

        if field1.getRegex()[0] != "(" and field2.getRegex()[0] != "(":  # Static + Static fields (should not happen...)
            newRegex = field1.getRegex() + field2.getRegex()

        # Default representation is BINARY
        new_name = field1.getName() + "+" + field2.getName()
        # Creation of the new Field
        newField = Field(new_name, field1.getIndex(), newRegex)

        self.fields.remove(field1)
        self.fields.remove(field2)

        # Update the index of the fields placed after it
        for field in self.fields:
            if field.getIndex() > newField.getIndex():
                field.setIndex(field.getIndex() - 1)
        self.fields.append(newField)
        # sort fields by their index
        self.fields = sorted(self.fields, key=attrgetter('index'), reverse=False)

    #+----------------------------------------------
    #| splitField:
    #|  Split a field in two fields
    #|  return False if the split does not occure, else True
    #+----------------------------------------------
    def splitField(self, field, split_position):
        if not (split_position > 0):
            return False

        # Find the static/dynamic cols
        cells = self.getMessagesValuesByField(field)
        ref1 = cells[0][:split_position]
        ref2 = cells[0][split_position:]
        isStatic1 = True
        isStatic2 = True
        lenDyn1 = len(cells[0][:split_position])
        lenDyn2 = len(cells[0][split_position:])
        for m in cells[1:]:
            if m[:split_position] != ref1:
                isStatic1 = False
                if len(m[:split_position]) > lenDyn1:
                    lenDyn1 = len(m[:split_position])
            if m[split_position:] != ref2:
                isStatic2 = False
                if len(m[split_position:]) > lenDyn2:
                    lenDyn2 = len(m[split_position:])

        # Build the new sub-regex
        if isStatic1:
            regex1 = ref1
        else:
            regex1 = "(.{," + str(lenDyn1) + "})"
        if isStatic2:
            regex2 = ref2
        else:
            regex2 = "(.{," + str(lenDyn2) + "})"

        if regex1 == "":
            return False
        if regex2 == "":
            return False

        new_format = field.getFormat()
        new_encapsulationLevel = field.getEncapsulationLevel()

        # We Build the two new fields
        field1 = Field("(1/2)" + field.getName(), field.getIndex(), regex1)
        field1.setEncapsulationLevel(new_encapsulationLevel)
        field1.setFormat(new_format)
        field1.setColor(field.getColor())
        if field.getDescription() != None and len(field.getDescription()) > 0:
            field1.setDescription("(1/2) " + field.getDescription())
        field2 = Field("(2/2) " + field.getName(), field.getIndex() + 1, regex2)
        field2.setEncapsulationLevel(new_encapsulationLevel)
        field2.setFormat(new_format)
        field2.setColor(field.getColor())
        if field.getDescription() != None and len(field.getDescription()) > 0:
            field2.setDescription("(2/2) " + field.getDescription())

        # Remove the truncated one
        self.fields.remove(field)

        # Modify index to adapt
        for field in self.getFields():
            if field.getIndex() > field1.getIndex():
                field.setIndex(field.getIndex() + 1)

        self.fields.append(field1)
        self.fields.append(field2)
        # sort fields by their index
        self.fields = sorted(self.fields, key=attrgetter('index'), reverse=False)

        return True

    #+-----------------------------------------------------------------------+
    #| getPossibleTypesForAField:
    #|     Retrieve all the possible types for a field
    #+-----------------------------------------------------------------------+
    def getPossibleTypesForAField(self, field):
        # first we verify the field exists in the symbol
        if not field in self.fields:
            logging.warn("The computing field is not part of the current symbol")
            return []

        # Retrieve all the part of the messages which are in the given field
        cells = self.getUniqValuesByField(field)
        typeIdentifier = TypeIdentifier()
        return typeIdentifier.getTypes(cells)

    #+-----------------------------------------------------------------------+
    #| getStyledPossibleTypesForAField:
    #|     Retrieve all the possibles types for a field and we colorize
    #|     the selected one we an HTML RED SPAN
    #+-----------------------------------------------------------------------+
    def getStyledPossibleTypesForAField(self, field):
        tmpTypes = self.getPossibleTypesForAField(field)
        for i in range(len(tmpTypes)):
            if tmpTypes[i] == field.getFormat():
                tmpTypes[i] = "<span foreground=\"red\">" + field.getFormat() + "</span>"
        return ", ".join(tmpTypes)

    #+----------------------------------------------
    #| dataCarving:
    #|  try to find semantic elements in each field
    #+----------------------------------------------
    def dataCarving(self):
        if len(self.fields) == 0:
            return None

        vbox = gtk.VBox(False, spacing=5)
        vbox.show()
        hbox = gtk.HPaned()
        hbox.show()
        # Treeview containing potential data carving results  ## ListStore format:
        # int: iField
        # str: data type (url, ip, email, etc.)
        store = gtk.ListStore(int, str)
        treeviewRes = gtk.TreeView(store)
        cell = gtk.CellRendererText()
        column = gtk.TreeViewColumn('Column')
        column.pack_start(cell, True)
        column.set_attributes(cell, text=0)
        treeviewRes.append_column(column)
        column = gtk.TreeViewColumn('Data type found')
        column.pack_start(cell, True)
        column.set_attributes(cell, text=1)
        treeviewRes.append_column(column)
        treeviewRes.set_size_request(200, 300)
        treeviewRes.show()
        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scroll.show()
        scroll.add(treeviewRes)
        hbox.add(scroll)

        ## Algo : for each column, and then for each cell, try to carve data
        typer = TypeIdentifier()

        ## TODO: put this things in a dedicated class
        infoCarvers = {
            'url': re.compile("((http:\/\/|https:\/\/)?(www\.)?(([a-z0-9\-]){2,}\.){1,4}([a-z]){2,6}(\/([a-z\-_\/\.0-9#:?+%=&;,])*)?)"),
            'email': re.compile("[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,4}"),
            'ip': re.compile("(((?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?))")
            }

        for field in self.getFields():
            for (carver, regex) in infoCarvers.items():
                matchElts = 0
                for cell in self.getMessagesValuesByField(field):
                    for match in regex.finditer(TypeConvertor.netzobRawToString(cell)):
                        matchElts += 1
                if matchElts > 0:
                    store.append([field.getIndex(), carver])

        # Preview of matching fields in a treeview  ## ListStore format:
        # str: data
        treeview = gtk.TreeView(gtk.ListStore(str))
        cell = gtk.CellRendererText()
        column = gtk.TreeViewColumn('Data')
        column.pack_start(cell, True)
        column.set_attributes(cell, markup=0)
        treeview.append_column(column)
        treeview.set_size_request(700, 300)
        treeview.show()
        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scroll.show()
        scroll.add(treeview)
        hbox.add(scroll)
        vbox.pack_start(hbox, True, True, 0)

        # Apply button
        but = gtk.Button(label="Apply data type on column")
        but.show()
        self.butDataCarvingHandle = None
        treeviewRes.connect("cursor-changed", self.dataCarvingResultSelected_cb, treeview, but, infoCarvers)
        vbox.pack_start(but, False, False, 0)

        return vbox
        # TODO : use hachoir to retrieve subfiles
        #    lines = os.popen("/usr/bin/hachoir-subfile " + target).readline()

    #+----------------------------------------------
    #| findSizeFields:
    #|   Try to find the size fields
    #+----------------------------------------------
    def findSizeFields(self, store):
        if len(self.fields) <= 1:
            return None
        iField = 0
        # We cover each field for a potential size field
        for field in self.getFields():
            if field.isStatic():  # Means the element is static, so we assume it's not a good candidate
                iField += 1
                continue
            cellsSize = self.getMessagesValuesByField(field)
            j = 0
            # We cover each field and aggregate them for a potential payload
            while j < len(self.getFields()):
                # Initialize the aggregate of messages from fieldJ to fieldK
                aggregateCellsData = []
                for l in range(len(cellsSize)):
                    aggregateCellsData.append("")

                # Fill the aggregate of messages and try to compare its length with the current expected length
                k = j
                while k < len(self.getFields()):
                    if k != j:
                        for l in range(len(cellsSize)):
                            aggregateCellsData[l] += self.getMessagesValuesByField(self.getFieldByIndex(k))[l]

                    # We try to aggregate the successive right sub-parts of j if it's a static column (TODO: handle dynamic column / TODO: handle left subparts of the K column)
                    if self.getFieldByIndex(j).isStatic():
                        lenJ = len(self.getFieldByIndex(j).getRegex())
                        stop = 0
                    else:
                        lenJ = 2
                        stop = 0
                    for m in range(lenJ, stop, -2):
                        for n in [4, 0, 1]:  # loop over different possible encoding of size field
                            res = True
                            for l in range(len(cellsSize)):
                                if self.getFieldByIndex(j).isStatic():
                                    targetData = self.getFieldByIndex(j).getRegex()[lenJ - m:] + aggregateCellsData[l]
                                else:
                                    targetData = self.getMessagesValuesByField(self.getFieldByIndex(k))[l] + aggregateCellsData[l]

                                # Handle big and little endian for size field of 1, 2 and 4 octets length
                                rawMsgSize = TypeConvertor.netzobRawToPythonRaw(cellsSize[l][:n * 2])
                                if len(rawMsgSize) == 1:
                                    expectedSizeType = "B"
                                elif len(rawMsgSize) == 2:
                                    expectedSizeType = "H"
                                elif len(rawMsgSize) == 4:
                                    expectedSizeType = "I"
                                else:  # Do not consider size field with len > 4
                                    res = False
                                    break
                                (expectedSizeLE,) = struct.unpack("<" + expectedSizeType, rawMsgSize)
                                (expectedSizeBE,) = struct.unpack(">" + expectedSizeType, rawMsgSize)
                                if (expectedSizeLE != len(targetData) / 2) and (expectedSizeBE != len(targetData) / 2):
                                    res = False
                                    break
                            if res:
                                if self.getFieldByIndex(j).isStatic():  # Means the regex j element is static and a sub-part is concerned
                                    store.append([self.id, iField, n * 2, j, lenJ - m, k, -1, "Found potential size field (col " + str(iField) + "[:" + str(n * 2) + "]) for an aggregation of data field (col " + str(j) + "[" + str(lenJ - m) + ":] to col " + str(k) + ")"])
                                else:
                                    store.append([self.id, iField, n * 2, j, -1, k, -1, "Found potential size field (col " + str(iField) + "[:" + str(n * 2) + "]) for an aggregation of data field (col " + str(j) + " to col " + str(k) + ")"])
                                break
                    k += 1
                j += 1
            iField += 1

    #+----------------------------------------------
    #| applyDataType_cb:
    #|  Called when user wants to apply a data type to a field
    #+----------------------------------------------
    def applyDataType_cb(self, button, iField, dataType):
        self.getFieldByIndex(iField).setDescription(dataType)

    #+----------------------------------------------
    #| dataCarvingResultSelected_cb:
    #|  Callback when clicking on a data carving result.
    #|  It shows a preview of the carved data
    #+----------------------------------------------
    def dataCarvingResultSelected_cb(self, treeview, treeviewTarget, but, infoCarvers):
        typer = TypeIdentifier()
        treeviewTarget.get_model().clear()
        (model, it) = treeview.get_selection().get_selected()
        if(it):
            if(model.iter_is_valid(it)):
                fieldIndex = model.get_value(it, 0)
                dataType = model.get_value(it, 1)
                treeviewTarget.get_column(0).set_title("Field " + str(fieldIndex))
                if self.butDataCarvingHandle != None:
                    but.disconnect(self.butDataCarvingHandle)
                self.butDataCarvingHandle = but.connect("clicked", self.applyDataType_cb, fieldIndex, dataType)
                for cell in self.getMessagesValuesByField(self.getFieldByIndex(fieldIndex)):
                    cell = glib.markup_escape_text(TypeConvertor.netzobRawToString(cell))
                    segments = []
                    for match in infoCarvers[dataType].finditer(cell):
                        if match == None:
                            treeviewTarget.get_model().append([cell])
                        segments.append((match.start(0), match.end(0)))

                    segments.reverse()  # We start from the end to avoid shifting
                    for (start, end) in segments:
                        cell = cell[:end] + "</span>" + cell[end:]
                        cell = cell[:start] + '<span foreground="red" font_family="monospace">' + cell[start:]
                    treeviewTarget.get_model().append([cell])

    #+----------------------------------------------
    #| findASN1Fields:
    #|  try to find ASN.1 fields
    #+----------------------------------------------
    def findASN1Fields(self, project):
        if len(self.fields) == 0:
            return None

        vbox = gtk.VBox(False, spacing=5)
        vbox.show()
        hbox = gtk.HPaned()
        hbox.show()
        # Treeview containing ASN.1 results  ## ListStore format:
        # int: iField
        # str: env. dependancy name (ip, os, username, etc.)
        # str: type
        # str: env. dependancy value (127.0.0.1, Linux, john, etc.)
        store = gtk.ListStore(int, str, str, str)
        treeviewRes = gtk.TreeView(store)
        cell = gtk.CellRendererText()
        column = gtk.TreeViewColumn('Column')
        column.pack_start(cell, True)
        column.set_attributes(cell, text=0)
        treeviewRes.append_column(column)
        column = gtk.TreeViewColumn('Results')
        column.pack_start(cell, True)
        column.set_attributes(cell, text=1)
        treeviewRes.append_column(column)
        treeviewRes.set_size_request(250, 300)
        treeviewRes.show()
        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scroll.show()
        scroll.add(treeviewRes)
        hbox.add(scroll)

        ## Algo : for each message, try to decode ASN.1 data

        for message in self.getMessages():
#            tmpStr = TypeConvertor.netzobRawToBinary(message.getStringData())
            tmpStr = message.getStringData()

            for end in range(1, len(tmpStr)):
                for start in range(0, end):
                    try:
                        res = pyasn1.codec.der.decoder.decode(tmpStr[start:end])
                    except SubstrateUnderrunError:
                        continue
                    except PyAsn1Error:
                        continue
                    except IndexError:
                        print "IndexError: " + repr(tmpStr[start:end])
                        continue
                    except:
                        print "NOK"
                        continue
#                    print "PAN: " + repr(res)
#                        store.append([field.getIndex(), envDependency.getName(), envDependency.getType(), envDependency.getValue()])

        # Preview of matching fields in a treeview  ## ListStore format:
        # str: data
        treeview = gtk.TreeView(gtk.ListStore(str))
        cell = gtk.CellRendererText()
        column = gtk.TreeViewColumn('Data')
        column.pack_start(cell, True)
        column.set_attributes(cell, markup=0)
        treeview.append_column(column)
        treeview.set_size_request(700, 300)
        treeview.show()
        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scroll.show()
        scroll.add(treeview)
        hbox.add(scroll)
        vbox.pack_start(hbox, True, True, 0)

        # Apply button
        but = gtk.Button(label="Apply data type on column")
        but.show()
        self.butDataCarvingHandle = None
        treeviewRes.connect("cursor-changed", self.ASN1ResultSelected_cb, treeview, but)
        vbox.pack_start(but, False, False, 0)

        return vbox

    #+----------------------------------------------
    #| ASN1ResultSelected_cb:
    #|  Callback when clicking on a environmental dependency result.
    #+----------------------------------------------
    def ASN1ResultSelected_cb(self, treeview, treeviewTarget, but):
        treeviewTarget.get_model().clear()
        (model, it) = treeview.get_selection().get_selected()
        if(it):
            if(model.iter_is_valid(it)):
                fieldIndex = model.get_value(it, 0)
                field = self.getFieldByIndex(fieldIndex)
                envName = model.get_value(it, 1)
                envType = model.get_value(it, 2)
                envValue = model.get_value(it, 3)
                treeviewTarget.get_column(0).set_title("Field " + str(field.getIndex()))
                if self.butDataCarvingHandle != None:
                    but.disconnect(self.butDataCarvingHandle)
                self.butDataCarvingHandle = but.connect("clicked", self.applyDependency_cb, field, envName)
                for cell in self.getMessagesValuesByField(field):
                    cell = glib.markup_escape_text(TypeConvertor.netzobRawToString(cell))
                    pattern = re.compile(envValue, re.IGNORECASE)
                    cell = pattern.sub('<span foreground="red" font_family="monospace">' + envValue + "</span>", cell)
                    treeviewTarget.get_model().append([cell])

    #+----------------------------------------------
    #| applyDependency_cb:
    #|  Called when user wants to apply a dependency to a field
    #+----------------------------------------------
    def applyDependency_cb(self, button, field, envName):
        field.setDescription(envName)
        pass

    #+----------------------------------------------
    #| envDependencies:
    #|  try to find environmental dependencies
    #+----------------------------------------------
    def envDependencies(self, project):
        if len(self.fields) == 0:
            return None

        vbox = gtk.VBox(False, spacing=5)
        vbox.show()
        hbox = gtk.HPaned()
        hbox.show()
        # Treeview containing potential data carving results  ## ListStore format:
        #   int: iField
        #   str: env. dependancy name (ip, os, username, etc.)
        #   str: type
        #   str: env. dependancy value (127.0.0.1, Linux, john, etc.)
        store = gtk.ListStore(int, str, str, str)
        treeviewRes = gtk.TreeView(store)
        cell = gtk.CellRendererText()
        column = gtk.TreeViewColumn('Column')
        column.pack_start(cell, True)
        column.set_attributes(cell, text=0)
        treeviewRes.append_column(column)
        column = gtk.TreeViewColumn('Env. dependancy')
        column.pack_start(cell, True)
        column.set_attributes(cell, text=1)
        treeviewRes.append_column(column)
        treeviewRes.set_size_request(250, 300)
        treeviewRes.show()
        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scroll.show()
        scroll.add(treeviewRes)
        hbox.add(scroll)

        # TODO: look in all possible formats

        ## Algo : for each field, and then for each value, try to find dependencies
        # First step: look for captured env. dependencies
        for field in self.getFields():
            cells = []
            try:
                cells = self.getMessagesValuesByField(field)
            except NetzobException, e:
                logging.warning("ERROR: " + str(e.value))
                break

            for envDependency in project.getConfiguration().getVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_ENVIRONMENTAL_DEPENDENCIES):
                if envDependency.getValue() == "":
                    break
                matchElts = 0
                for cell in cells:
                    matchElts += TypeConvertor.encodeNetzobRawToGivenType(cell, envDependency.getType()).count(str(envDependency.getValue()))
                if matchElts > 0:
                    store.append([field.getIndex(), envDependency.getName(), envDependency.getType(), envDependency.getValue()])

        # Second step: look for captured message properties
        for message in self.getMessages():
            iField = 0
            messageTable = message.applyAlignment()
            for cell in messageTable:
                for prop in message.getProperties():
                    name = prop[0]
                    aType = prop[1]
                    value = prop[2]
                    if value == "" or name == "Data":
                        break
                    matchElts = str(TypeConvertor.encodeNetzobRawToGivenType(cell, aType)).count(str(value))
                    if matchElts > 0:
                        store.append([iField, name, aType, value])
                iField += 1

        # Preview of matching fields in a treeview
        ## ListStore format:
        # str: data
        treeview = gtk.TreeView(gtk.ListStore(str))
        cell = gtk.CellRendererText()
        column = gtk.TreeViewColumn('Data')
        column.pack_start(cell, True)
        column.set_attributes(cell, markup=0)
        treeview.append_column(column)
        treeview.set_size_request(700, 300)
        treeview.show()
        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scroll.show()
        scroll.add(treeview)
        hbox.add(scroll)
        vbox.pack_start(hbox, True, True, 0)

        # Apply button
        but = gtk.Button(label="Apply data type on column")
        but.show()
        self.butDataCarvingHandle = None
        treeviewRes.connect("cursor-changed", self.envDependenciesResultSelected_cb, treeview, but)
        vbox.pack_start(but, False, False, 0)

        return vbox

    #+----------------------------------------------
    #| envDependenciesResultSelected_cb:
    #|  Callback when clicking on a environmental dependency result.
    #+----------------------------------------------
    def envDependenciesResultSelected_cb(self, treeview, treeviewTarget, but):
        treeviewTarget.get_model().clear()
        (model, it) = treeview.get_selection().get_selected()
        if(it):
            if(model.iter_is_valid(it)):
                fieldIndex = model.get_value(it, 0)
                field = self.getFieldByIndex(fieldIndex)
                envName = model.get_value(it, 1)
                envType = model.get_value(it, 2)
                envValue = model.get_value(it, 3)
                treeviewTarget.get_column(0).set_title("Field " + str(field.getIndex()))
                if self.butDataCarvingHandle != None:
                    but.disconnect(self.butDataCarvingHandle)
                self.butDataCarvingHandle = but.connect("clicked", self.applyDependency_cb, field, envName)
                for cell in self.getMessagesValuesByField(field):
                    cell = glib.markup_escape_text(TypeConvertor.encodeNetzobRawToGivenType(cell, envType))
                    pattern = re.compile(envValue, re.IGNORECASE)
                    cell = pattern.sub('<span foreground="red" font_family="monospace">' + envValue + "</span>", cell)
                    treeviewTarget.get_model().append([cell])

    

    #+----------------------------------------------
    #| getVariables:
    #|  Extract from the fields definitions the included variables
    #+----------------------------------------------
    def getVariables(self):
        result = []
        for field in self.getFields():
            if not field.isStatic() :
                if field.getVariable() != None:
                    result.append(field.getVariable())
        return result

    #+----------------------------------------------
    #| removeMessage : remove any ref to the given
    #| message and recompute regex and score
    #+----------------------------------------------
    def removeMessage(self, message):
        self.messages.remove(message)

    def addMessage(self, message):
        for msg in self.messages:
            if msg.getID() == message.getID():
                return
        message.setSymbol(self)
        self.messages.append(message)

    def addField(self, field):
        self.fields.append(field)
        
    def cleanFields(self):
        while len(self.fields) != 0 :
            self.fields.pop()

    def popField(self, index=None):
        if index == None:
            self.fields.pop()
        else:
            self.fields.pop(index)

    def save(self, root, namespace_project, namespace_common):
        xmlSymbol = etree.SubElement(root, "{" + namespace_project + "}symbol")
        xmlSymbol.set("alignment", str(self.getAlignment()))
        xmlSymbol.set("id", str(self.getID()))
        xmlSymbol.set("name", str(self.getName()))
        xmlSymbol.set("score", str(self.getScore()))
        xmlSymbol.set("alignmentType", str(self.getAlignmentType()))
        xmlSymbol.set("rawDelimiter", str(self.getRawDelimiter()))

        # Save the messages
        xmlMessages = etree.SubElement(xmlSymbol, "{" + namespace_project + "}messages")
        for message in self.messages:
            AbstractMessageFactory.save(message, xmlMessages, namespace_project, namespace_common)
        # Save the fields
        xmlFields = etree.SubElement(xmlSymbol, "{" + namespace_project + "}fields")
        for field in self.getFields():
            field.save(xmlFields, namespace_project)

    #+----------------------------------------------
    #| getXMLDefinition:
    #|   Returns the XML description of the symbol
    #|   @return a string containing the xml def.
    #+----------------------------------------------
    def getXMLDefinition(self):
        # Register the namespace (2 way depending of the version)
        try:
            etree.register_namespace('netzob', PROJECT_NAMESPACE)
            etree.register_namespace('netzob-common', COMMON_NAMESPACE)
        except AttributeError:
            etree._namespace_map[PROJECT_NAMESPACE] = 'netzob'
            etree._namespace_map[COMMON_NAMESPACE] = 'netzob-common'

        # create the file
        root = etree.Element("{" + NAMESPACE + "}netzob")
        root.set("project", str(self.getProject().getName()))

        self.save(root, PROJECT_NAMESPACE, COMMON_NAMESPACE)

        tree = ElementTree(root)
        result = etree.tostring(tree, pretty_print=True)
        return result
#
#        self.format = Format.HEX
#        self.unitSize = UnitSize.NONE
#        self.sign = Sign.UNSIGNED
#        self.endianess = Endianess.BIG

    #+----------------------------------------------
    #| getTextDefinition:
    #|   Returns the text description of the symbol
    #|   @return a string containing the text definition
    #+----------------------------------------------
    def getTextDefinition(self):
        result = ""
        for field in self.getFields():
            # We exclude separator fields
            if self.getAlignmentType() == "delimiter":
                if field.isStatic():
                    continue

            # Layer depth
            for i in range(field.getEncapsulationLevel()):
                result += "  "

            # Name
            result += field.getName()

            # Description
            if field.getDescription() != None and field.getDescription() != "":
                result += " (" + field.getDescription() + ") "
            result += " : "
            result += "\t"

            # Value
            result += field.getRegex()

            result += "\n"
        return result

    #+----------------------------------------------
    #| getScapyDissector:
    #|   @return a string containing the scapy dissector of the symbol
    #+----------------------------------------------
    def getScapyDissector(self):
        self.refineRegexes()  # In order to force the calculation of each field limits
        s = ""
        s += "class " + self.getName() + "(Packet):\n"
        s += "    name = \"" + self.getName() + "\"\n"
        s += "    fields_desc = [\n"

        for field in self.getFields():
            if self.field.isStatic():
                s += "                    StrFixedLenField(\"" + field.getName() + "\", " + field.getEncodedVersionOfTheRegex() + ")\n"
            else:  # Variable field of fixed size
                s += "                    StrFixedLenField(\"" + field.getName() + "\", None)\n"
            ## If this is a variable field  # TODO
                # StrLenField("the_varfield", "the_default_value", length_from = lambda pkt: pkt.the_lenfield)
        s += "                 ]\n"

        ## Bind current layer with the underlying one  # TODO
        # bind_layers(TCP, HTTP, sport=80)
        # bind_layers(TCP, HTTP, dport=80)
        return s

    #+----------------------------------------------
    #| slickRegex:
    #|  try to make smooth the regex, by deleting tiny static
    #|  sequences that are between big dynamic sequences
    #+----------------------------------------------
    def slickRegex(self, project):
        if self.getAlignmentType() == "delimiter":
            logging.warn("SlickRegex(): only applicable to a symbol with dynamic alignment")
            return

        # Use the default protocol type for representation
        aFormat = project.getConfiguration().getVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_GLOBAL_FORMAT)

        res = False
        i = 1
        nbFields = len(self.getFields())
        while i < nbFields - 1:
            aField = self.getFieldByIndex(i)
            if aField.isStatic():
                if len(aField.getRegex()) <= 2:  # Means a potential negligeable element that can be merged with its neighbours
                    precField = self.getFieldByIndex(i - 1)
                    if precField.isRegexOnlyDynamic():
                        nextField = self.getFieldByIndex(i + 1)
                        if nextField.isRegexOnlyDynamic():
                            res = True
                            minSize = len(aField.getRegex())
                            maxSize = len(aField.getRegex())

                            # Build the new field
                            regex = re.compile(".*{(\d*),(\d*)}.*")

                            # Get the minSize/maxSize of precField
                            m = regex.match(precField.getRegex())
                            if m.group(1) != "":
                                minSize += int(m.group(1))
                            if m.group(2) != "":
                                maxSize += int(m.group(2))

                            # Get the minSize/maxSize of nextField
                            m = regex.match(nextField.getRegex())
                            if m.group(1) != "":
                                minSize += int(m.group(1))
                            if m.group(2) != "":
                                maxSize += int(m.group(2))

                            minSize = str(minSize)
                            maxSize = str(maxSize)

                            aField.setIndex(precField.getIndex())
                            aField.setRegex("(.{" + minSize + "," + maxSize + "})")
                            aField.setFormat(aFormat)

                            # Delete the old ones
                            self.fields.remove(nextField)
                            self.fields.remove(precField)

                            # Update the index of the fields placed after the new one
                            for field in self.fields:
                                if field.getIndex() > aField.getIndex():
                                    field.setIndex(field.getIndex() - 2)
                            # Sort fields by their index
                            self.fields = sorted(self.fields, key=attrgetter('index'), reverse=False)
                            break  # Just do it one time to avoid conflicts in self.fields structure
            i += 1

        if res:
            self.slickRegex(project)  # Try to loop until no more merges are done
            logging.debug("The regex has been slicked")

    #+----------------------------------------------
    #| resetPartitioning:
    #|   Reset the current partitioning
    #+----------------------------------------------
    def resetPartitioning(self, project):
        aFormat = project.getConfiguration().getVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_GLOBAL_FORMAT)

        # Reset values
        self.alignmentType = "regex"
        self.rawDelimiter = ""
        self.fields = []

        # Create a single field
        field = Field("Field 0", 0, "(.{,})")
        field.setFormat(aFormat)
        self.addField(field)

    def getValueToSend(self, inverse, vocabulary, memory):
        result = self.getRoot().getValueToSend(inverse, vocabulary, memory)
        return result

    def getRoot(self):
        # We create an aggregate of all the fields
        rootSymbol = AggregateVariable(self.getID(), self.getName(), None)
        for field in self.getFields():
            if field.getVariable() == None:
                variable = field.getDefaultVariable(self)
            else:
                variable = field.getVariable()
            rootSymbol.addChild(variable)
        return rootSymbol

    #+----------------------------------------------
    #| GETTERS
    #+----------------------------------------------
    def getID(self):
        return self.id

    def getMessages(self):
        return self.messages

    def getScore(self):
        return self.score

    def getName(self):
        return self.name

    def getFields(self):
        self.fields = sorted(self.fields, key=attrgetter('index'), reverse=False)
        return self.fields

    def getAlignment(self):
        return self.alignment.strip()

    def getAlignmentType(self):
        return self.alignmentType

    def getRawDelimiter(self):
        return self.rawDelimiter

    def getProject(self):
        return self.project

    #+----------------------------------------------
    #| SETTERS
    #+----------------------------------------------
    def setFields(self, fields):
        self.fields = fields

    def setAlignment(self, alignment):
        self.alignment = alignment

    def setScore(self, score):
        self.score = score

    def setName(self, name):
        self.name = name

    def setAlignmentType(self, aType):
        self.alignmentType = aType

    def setRawDelimiter(self, rawDelimiter):
        self.rawDelimiter = rawDelimiter
        
    def __str__(self):
        return str(self.getName())

    def __repr__(self):
        return str(self.getName())
    
    def __cmp__(self, other):
        if other == None:
            return 1
        try :
            if self.getID() == other.getID():
                return 0
            else:
                return 1
        except  :
            self.log.warn("Tried to compare a Symbol with " + str(other))
            return 1


    #+----------------------------------------------
    #| Static methods
    #+----------------------------------------------
    @staticmethod
    def loadSymbol(xmlRoot, namespace, namespace_common, version, project):

        if version == "0.1":
            nameSymbol = xmlRoot.get("name")
            idSymbol = xmlRoot.get("id")
            alignmentSymbol = xmlRoot.get("alignment", None)
            scoreSymbol = float(xmlRoot.get("score", "0"))
            alignmentType = xmlRoot.get("alignmentType")
            rawDelimiter = xmlRoot.get("rawDelimiter")

            symbol = Symbol(idSymbol, nameSymbol, project)
            symbol.setAlignment(alignmentSymbol)
            symbol.setScore(scoreSymbol)
            symbol.setAlignmentType(alignmentType)
            symbol.setRawDelimiter(rawDelimiter)

            # we parse the messages
            if xmlRoot.find("{" + namespace + "}messages") != None:
                xmlMessages = xmlRoot.find("{" + namespace + "}messages")
                for xmlMessage in xmlMessages.findall("{" + namespace_common + "}message"):
                    message = AbstractMessageFactory.loadFromXML(xmlMessage, namespace_common, version)
                    if message != None:
                        message.setSymbol(symbol)
                        symbol.addMessage(message)

            # we parse the fields
            if xmlRoot.find("{" + namespace + "}fields") != None:
                xmlFields = xmlRoot.find("{" + namespace + "}fields")
                for xmlField in xmlFields.findall("{" + namespace + "}field"):
                    field = Field.loadFromXML(xmlField, namespace, version)
                    if field != None:
                        symbol.addField(field)
            
            
                
            return symbol
        return None
