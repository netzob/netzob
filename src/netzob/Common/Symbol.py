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
from netzob.Common.Field import Field
from netzob.Common.ProjectConfiguration import ProjectConfiguration
from netzob.Common.Type.TypeIdentifier import TypeIdentifier
from netzob.Common.Type.TypeConvertor import TypeConvertor
from netzob.Common.Type.UnitSize import UnitSize
from netzob.Common.Type.Format import Format
from netzob.Common.Type.Sign import Sign
from netzob.Common.Type.Endianess import Endianess
from netzob.Common.NetzobException import NetzobException
from netzob.Common.MMSTD.Dictionary.Variables.AggregateVariable import AggregateVariable
from netzob.Common.MMSTD.Symbols.AbstractSymbol import AbstractSymbol


NAMESPACE = "http://www.netzob.org/"

# TODO: Note: this is probably useless, as it is already specified in Project.py
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
    def __init__(self, id, name, project, pattern=[], minEqu=0):
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
        self.encodingFilters = []
        self.visualizationFilters = []
        self.pattern = pattern
        self.minEqu = minEqu

        # Interpretation attributes
        self.format = Format.HEX
        self.unitSize = UnitSize.NONE
        self.sign = Sign.UNSIGNED
        self.endianess = Endianess.BIG

        # Clean the symbol
        aFormat = project.getConfiguration().getVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_GLOBAL_FORMAT)
        field = Field.createDefaultField()
        field.setFormat(aFormat)
        self.addField(field)

    def addVisualizationFilter(self, filter):
        self.visualizationFilters.append(filter)

    def cleanVisualizationFilters(self):
        self.visualizationFilters = []

    def getVisualizationFilters(self):
        return self.visualizationFilters

    def removeVisualizationFilter(self, filter):
        self.visualizationFilters.remove(filter)

    def addEncodingFilter(self, filter):
        self.encodingFilters.append(filter)

    def removeEncodingFilter(self, filter):
        if filter in self.encodingFilters:
            self.encodingFilters.remove(filter)

    def getEncodingFilters(self):
        filters = []
        for field in self.getFields():
            filters.extend(field.getEncodingFilters())
        filters.extend(self.encodingFilters)

    #+----------------------------------------------
    #| forcePartitioning:
    #|  Specify a delimiter for partitioning
    #+----------------------------------------------
    def forcePartitioning(self, projectConfiguration, aFormat, rawDelimiter):
        self.alignmentType = "delimiter"
        self.rawDelimiter = rawDelimiter
        self.cleanFields()

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
        self.cleanFields()

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

        # Apply unitSize
        if unitSize != UnitSize.NONE:
            unitSize = UnitSize.getSizeInBits(unitSize)
            nbLetters = unitSize / 4
            tmpResultString = ""
            tmpResultMask = ""
            for i in range(0, len(resultString), nbLetters):
                tmpText = resultString[i:i + nbLetters]
                if tmpText.count("-") >= 1:
                    for j in range(len(tmpText)):
                        tmpResultString += "-"
                        tmpResultMask += "1"
                else:
                    tmpResultString += tmpText
                    for j in range(len(tmpText)):
                        tmpResultMask += "0"
            resultString = tmpResultString
            resultMask = tmpResultMask

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
            if resultMask[it] == "1":  # The current column is dynamic
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
                cells = self.getCellsByField(field)
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
    #| getCellsByField:
    #|  Return all the messages parts which are in
    #|  the specified field
    #+----------------------------------------------
    def getCellsByField(self, field):
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
        if iField == len(self.fields) - 1:
            return 0

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
        return 1

    #+----------------------------------------------
    #| splitField:
    #|  Split a field in two fields
    #|  return False if the split does not occure, else True
    #+----------------------------------------------
    def splitField(self, field, split_position, split_align):
        if split_position == 0:
            return False

        # Find the static/dynamic cols
        cells = self.getCellsByField(field)
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
            if split_align == "left":
                # The size is fixed
                regex1 = "(.{" + str(lenDyn1) + "})"
            else:
                regex1 = "(.{," + str(lenDyn1) + "})"
        if isStatic2:
            regex2 = ref2
        else:
            if split_align == "right":
                # The size is fixed
                regex2 = "(.{" + str(lenDyn2) + "})"
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

#    #+----------------------------------------------
#    #| dataCarving:
#    #|  try to find semantic elements in each field
#    #+----------------------------------------------
#    def dataCarving(self):
#        if len(self.fields) == 0:
#            return None
#
#        vbox = gtk.VBox(False, spacing=5)
#        vbox.show()
#        hbox = gtk.HPaned()
#        hbox.show()
#        # Treeview containing potential data carving results  ## ListStore format:
#        # int: iField
#        # str: data type (url, ip, email, etc.)
#        store = gtk.ListStore(int, str)
#        treeviewRes = gtk.TreeView(store)
#        cell = gtk.CellRendererText()
#        column = gtk.TreeViewColumn('Column')
#        column.pack_start(cell, True)
#        column.set_attributes(cell, text=0)
#        treeviewRes.append_column(column)
#        column = gtk.TreeViewColumn('Data type found')
#        column.pack_start(cell, True)
#        column.set_attributes(cell, text=1)
#        treeviewRes.append_column(column)
#        treeviewRes.set_size_request(200, 300)
#        treeviewRes.show()
#        scroll = gtk.ScrolledWindow()
#        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
#        scroll.show()
#        scroll.add(treeviewRes)
#        hbox.add(scroll)
#
#        ## Algo : for each column, and then for each cell, try to carve data
#        typer = TypeIdentifier()
#
#        ## TODO: put this things in a dedicated class
#        infoCarvers = {
#            'url': re.compile("((http:\/\/|https:\/\/)?(www\.)?(([a-z0-9\-]){2,}\.){1,4}([a-z]){2,6}(\/([a-z\-_\/\.0-9#:?+%=&;,])*)?)"),
#            'email': re.compile("[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,4}"),
#            'ip': re.compile("(((?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?))")
#            }
#
#        for field in self.getFields():
#            for (carver, regex) in infoCarvers.items():
#                matchElts = 0
#                for cell in self.getCellsByField(field):
#                    for match in regex.finditer(TypeConvertor.netzobRawToString(cell)):
#                        matchElts += 1
#                if matchElts > 0:
#                    store.append([field.getIndex(), carver])
#
#        # Preview of matching fields in a treeview  ## ListStore format:
#        # str: data
#        treeview = gtk.TreeView(gtk.ListStore(str))
#        cell = gtk.CellRendererText()
#        column = gtk.TreeViewColumn('Data')
#        column.pack_start(cell, True)
#        column.set_attributes(cell, markup=0)
#        treeview.append_column(column)
#        treeview.set_size_request(700, 300)
#        treeview.show()
#        scroll = gtk.ScrolledWindow()
#        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
#        scroll.show()
#        scroll.add(treeview)
#        hbox.add(scroll)
#        vbox.pack_start(hbox, True, True, 0)
#
#        # Apply button
#        but = gtk.Button(label="Apply data type on column")
#        but.show()
#        self.butDataCarvingHandle = None
#        treeviewRes.connect("cursor-changed", self.dataCarvingResultSelected_cb, treeview, but, infoCarvers)
#        vbox.pack_start(but, False, False, 0)
#
#        return vbox
#        # TODO : use hachoir to retrieve subfiles
#        #    lines = os.popen("/usr/bin/hachoir-subfile " + target).readline()

    #+----------------------------------------------
    #| applyDataType_cb:
    #|  Called when user wants to apply a data type to a field
    #+----------------------------------------------
    def applyDataType_cb(self, button, iField, dataType):
        self.getFieldByIndex(iField).setDescription(dataType)
#
#    #+----------------------------------------------
#    #| dataCarvingResultSelected_cb:
#    #|  Callback when clicking on a data carving result.
#    #|  It shows a preview of the carved data
#    #+----------------------------------------------
#    def dataCarvingResultSelected_cb(self, treeview, treeviewTarget, but, infoCarvers):
#        typer = TypeIdentifier()
#        treeviewTarget.get_model().clear()
#        (model, it) = treeview.get_selection().get_selected()
#        if(it):
#            if(model.iter_is_valid(it)):
#                fieldIndex = model.get_value(it, 0)
#                dataType = model.get_value(it, 1)
#                treeviewTarget.get_column(0).set_title("Field " + str(fieldIndex))
#                if self.butDataCarvingHandle != None:
#                    but.disconnect(self.butDataCarvingHandle)
#                self.butDataCarvingHandle = but.connect("clicked", self.applyDataType_cb, fieldIndex, dataType)
#                for cell in self.getCellsByField(self.getFieldByIndex(fieldIndex)):
#                    cell = glib.markup_escape_text(TypeConvertor.netzobRawToString(cell))
#                    segments = []
#                    for match in infoCarvers[dataType].finditer(cell):
#                        if match == None:
#                            treeviewTarget.get_model().append([cell])
#                        segments.append((match.start(0), match.end(0)))
#
#                    segments.reverse()  # We start from the end to avoid shifting
#                    for (start, end) in segments:
#                        cell = cell[:end] + "</span>" + cell[end:]
#                        cell = cell[:start] + '<span foreground="red" font_family="monospace">' + cell[start:]
#                    treeviewTarget.get_model().append([cell])

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
                for cell in self.getCellsByField(field):
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
                cells = self.getCellsByField(field)
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
                for cell in self.getCellsByField(field):
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
            if not field.isStatic():
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

    def addField(self, field, index=None):
        if index == None:
            self.fields.append(field)
        else:
            self.fields.insert(index, field)

        realIndex = self.fields.index(field)
        field.setIndex(realIndex)
        return realIndex

    def cleanFields(self):
        while len(self.fields) != 0:
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

        # Interpretation attributes
        if self.getFormat() != None:
            xmlSymbolFormat = etree.SubElement(xmlSymbol, "{" + namespace_project + "}format")
            xmlSymbolFormat.text = str(self.getFormat())

        if self.getUnitSize() != None:
            xmlSymbolUnitSize = etree.SubElement(xmlSymbol, "{" + namespace_project + "}unitsize")
            xmlSymbolUnitSize.text = str(self.getUnitSize())

        if self.getSign() != None:
            xmlSymbolSign = etree.SubElement(xmlSymbol, "{" + namespace_project + "}sign")
            xmlSymbolSign.text = str(self.getSign())

        if self.getEndianess() != None:
            xmlSymbolEndianess = etree.SubElement(xmlSymbol, "{" + namespace_project + "}endianess")
            xmlSymbolEndianess.text = str(self.getEndianess())

        # Save the message references
        xmlMessages = etree.SubElement(xmlSymbol, "{" + namespace_project + "}messages-ref")
        for message in self.messages:
            xmlMessage = etree.SubElement(xmlMessages, "{" + namespace_common + "}message-ref")
            xmlMessage.set("id", str(message.getID()))
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

        # Register the namespace
        etree.register_namespace('netzob', PROJECT_NAMESPACE)
        etree.register_namespace('netzob-common', COMMON_NAMESPACE)

        # create the file
        root = etree.Element("{" + NAMESPACE + "}netzob")
        root.set("project", str(self.getProject().getName()))

        self.save(root, PROJECT_NAMESPACE, COMMON_NAMESPACE)

        tree = ElementTree(root)
        result = etree.tostring(tree, pretty_print=True)
        return result

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
            result += field.getEncodedVersionOfTheRegex()

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
        self.cleanFields()

        # Create a single field
        field = Field.createDefaultField()
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

    def getPattern(self):
        return self.pattern

    def getPatternString(self):
        return str(self.pattern[0]) + ";" + str([str(i) for i in self.pattern[1]])

    def getMinEqu(self):
        return self.minEqu

    def getFormat(self):
        return self.format

    def getUnitSize(self):
        return self.unitSize

    def getSign(self):
        return self.sign

    def getEndianess(self):
        return self.endianess

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

    def setFormat(self, aFormat):
        self.format = aFormat
        for field in self.getFields():
            field.setFormat(aFormat)

    def setUnitSize(self, unitSize):
        self.unitSize = unitSize
        for field in self.getFields():
            field.setUnitSize(unitSize)

    def setSign(self, sign):
        self.sign = sign
        for field in self.getFields():
            field.setSign(sign)

    def setEndianess(self, endianess):
        self.endianess = endianess
        for field in self.getFields():
            field.setEndianess(endianess)

    def __str__(self):
        return str(self.getName())

    def __repr__(self):
        return str(self.getName())

    def __cmp__(self, other):
        if other == None:
            return 1
        try:
            if self.getID() == other.getID():
                return 0
            else:
                return 1
        except:
            self.log.warn("Tried to compare a Symbol with " + str(other))
            return 1

    #+----------------------------------------------
    #| Static methods
    #+----------------------------------------------
    @staticmethod
    def loadSymbol(xmlRoot, namespace_project, namespace_common, version, project, poolOfMessages):
        if version == "0.1":
            nameSymbol = xmlRoot.get("name")
            idSymbol = xmlRoot.get("id")
            alignmentSymbol = xmlRoot.get("alignment", None)
            scoreSymbol = float(xmlRoot.get("score", "0"))
            alignmentType = xmlRoot.get("alignmentType")
            rawDelimiter = xmlRoot.get("rawDelimiter")

            symbol = Symbol(idSymbol, nameSymbol, project)
            symbol.cleanFields()
            symbol.setAlignment(alignmentSymbol)
            symbol.setScore(scoreSymbol)
            symbol.setAlignmentType(alignmentType)
            symbol.setRawDelimiter(rawDelimiter)

            # Interpretation attributes
            if xmlRoot.find("{" + namespace_project + "}format") != None:
                symbol_format = xmlRoot.find("{" + namespace_project + "}format").text
                symbol.setFormat(symbol_format)

            if xmlRoot.find("{" + namespace_project + "}unitsize") != None:
                symbol_unitsize = xmlRoot.find("{" + namespace_project + "}unitsize").text
                symbol.setUnitSize(symbol_unitsize)

            if xmlRoot.find("{" + namespace_project + "}sign") != None:
                symbol_sign = xmlRoot.find("{" + namespace_project + "}sign").text
                symbol.setSign(symbol_sign)

            if xmlRoot.find("{" + namespace_project + "}endianess") != None:
                symbol_endianess = xmlRoot.find("{" + namespace_project + "}endianess").text
                symbol.setEndianess(symbol_endianess)

            # we parse the messages
            if xmlRoot.find("{" + namespace_project + "}messages-ref") != None:
                xmlMessages = xmlRoot.find("{" + namespace_project + "}messages-ref")
                for xmlMessage in xmlMessages.findall("{" + namespace_common + "}message-ref"):
                    id = xmlMessage.get("id")
                    message = poolOfMessages.getMessageByID(id)
                    if message != None:
                        message.setSymbol(symbol)
                        symbol.addMessage(message)

            # we parse the fields
            if xmlRoot.find("{" + namespace_project + "}fields") != None:
                xmlFields = xmlRoot.find("{" + namespace_project + "}fields")
                for xmlField in xmlFields.findall("{" + namespace_project + "}field"):
                    field = Field.loadFromXML(xmlField, namespace_project, version)
                    if field != None:
                        symbol.addField(field)

            return symbol
        return None
