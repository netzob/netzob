# -*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|          01001110 01100101 01110100 01111010 01101111 01100010            |
#|                                                                           |
#|               Netzob : Inferring communication protocols                  |
#+---------------------------------------------------------------------------+
#| Copyright (C) 2011 AMOSSYS                                                |
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
#| Standard library imports                                                  |
#+---------------------------------------------------------------------------+
from gettext import gettext as _
import logging
import os
import zlib
import subprocess
import uuid
import tempfile
import shutil
import numpy

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+
from gi.repository import Gtk

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Plugins.RelationsIdentifier.AbstractRelationsIdentifierController import AbstractRelationsIdentifierController
from MINERelationsView import MINERelationsView
from netzob.Common.Type.TypeConvertor import TypeConvertor
from RelationsMakerController import RelationsMakerController
from minepy import MINE


class MINERelationsController(AbstractRelationsIdentifierController):
    """MINERelationsController:
            A controller liking the MINE exporter and its view in the netzob GUI.
    """

    def __init__(self, netzob, plugin):
        """Constructor of MINERelationsController:

                @type netzob: MINEExporterPlugin
                @param netzob: the plugin instance
        """
        self.netzob = netzob
        self.plugin = plugin
        self.selectedSymbols = self.getVocabularyController().symbolController.getCheckedSymbolList()
        self.view = MINERelationsView(self, plugin, self.selectedSymbols)
        super(MINERelationsController, self).__init__(netzob, plugin, self.view)

    def run(self):
        """run:
            Show the plugin view.
        """
        self.update()

    def update(self):
        self.view.show()

    def getPanel(self):
        """getPanel:

                @rtype: netzob_plugins.
                @return: the plugin view.
        """
        return self.view

    def cancelButton_clicked_cb(self, widget):
        self.view.destroy()

    def print_mine_stats(self, mine):
        print "MIC", mine.mic()
        print "MAS", mine.mas()
        print "MEV", mine.mev()
        print "MCN (eps=0)", mine.mcn(0)
        print "MCN (eps=1-MIC)", mine.mcn_general()

    def startButton_clicked_cb(self, widget):
        """exportButton_clicked_cb:
            Callback executed when the user clicks on the export button"""

        attributeValuesPerSymbols = self.generateAttributeValues()

        # For each symbol, we write in a temp file the CSV
        # execute the MINE relation finder and parse its results
        results = dict()
        resXX = []
        mine = MINE(alpha=0.6, c=15)
        for symbolName in attributeValuesPerSymbols.keys():
            (symbol, attributeValues_headers, attributeValues) = attributeValuesPerSymbols[symbolName]

            print attributeValues

            # MINE computation
            i = -1
            for values_x in attributeValues[:-1]:
                i += 1
                resYY = []
                j = -1
                for values_y in attributeValues[i+1:]:
                    j += 1
                    mine.compute_score(numpy.array(values_x), numpy.array(values_y))
                    resYY.append((round(mine.mic(), 2), attributeValues_headers[i][:2], symbol.getFieldByID(attributeValues_headers[i][2:]).getName(), attributeValues_headers[j][:2], symbol.getFieldByID(attributeValues_headers[j][2:]).getName()))
                    print "----------"
                    print attributeValues_headers[i]
                    print attributeValues_headers[j]
                    print symbol.getFieldByID(attributeValues_headers[i][2:]).getName()
                    print symbol.getFieldByID(attributeValues_headers[j][2:]).getName()
                    #self.print_mine_stats(mine)
                resXX.append(resYY)
        print attributeValues_headers
        for elt in resXX:
            print elt
            # Parse results
#            tmpResults = self.parseResult(contentOutputFile, symbol)
#            results[symbol.getName()] = tmpResults

        self.view.destroy()

        # # Start the relation maker controller
        # controller = RelationsMakerController(self.getPlugin(), self, results)
        # controller.run()

    def parseResult(self, content, symbol):
        results = []
        lines = content.split('\n')

        for i_line in range(1, len(lines)):
            line = lines[i_line]
            if len(line) > 0:
                cols = line.split(',')
                if len(cols) > 3:
                    startRel = cols[0]
                    endRel = cols[1]
                    score = cols[2]

                    (startField, startTypeField) = self.extractFieldFromRelation(startRel, symbol)
                    (endField, endTypeField) = self.extractFieldFromRelation(endRel, symbol)

                    typeRelation = "Unknown"
                    if (startTypeField == "v" and endTypeField == "s") or (startTypeField == "s" and endTypeField == "v"):
                        typeRelation = "SizeRelation"
                    elif (startTypeField == endTypeField) and startTypeField == "v":
                        typeRelation = "DataRelation"

                    filter = False
                    if typeRelation == "DataRelation":
                        if startField.getID() == endField.getID():
                            filter = True

                    if float(score) < 0.75:
                        filter = True

                    if not filter:
                        idRelation = uuid.uuid4()
                        results.append((typeRelation, startField, startTypeField, endField, endTypeField, score, idRelation))
        return results

    def extractFieldFromRelation(self, strRel, symbol):
        """extractFieldFromRelation:
        Parse the format 'type:Field name' and returns the three
        elements"""

        field = None
        t = None

        tab = strRel.split(':')
        t = tab[0]
        fieldID = tab[1]

        if t == "crc32":
            field = symbol.getField()
        else:
            if '[' in fieldID:
                indexOf = fieldID.index('[')
                fieldID = fieldID[:indexOf]

            field = symbol.getFieldByID(fieldID)

        return (field, t)

    def generateAttributeValues(self):
        attributeValuesPerSymbols = dict()
        for symbol in self.selectedSymbols:
            (attributeValues_headers, attributeValues) = self.generateAttributeValuesForSymbol(symbol)
            attributeValuesPerSymbols[symbol.getName()] = (symbol, attributeValues_headers, attributeValues)
        return attributeValuesPerSymbols

    def generateAttributeValuesForSymbol(self, symbol):
        # First we compute the possible list of payloads
        lines = []
        line_header = []

        # Compute the table of values
        values = dict()
        fields = symbol.getExtendedFields()
        for field in fields:
            values[field] = field.getCells()

        # First we generate lines and header for fields values
        for field in values.keys():
            line_header.append("v:{0}".format(field.getID()))
            dataValues = self.generateDataValues(values[field])
            lines.append(dataValues)

        # First we generate lines and header for fields values
        for field in values.keys():
            line_header.append("s:{0}".format(field.getID()))
            sizeValues = self.generateSizeValues(values[field])
            lines.append(sizeValues)

        # # Now we generate values for fields sizes
        # (multipleSize_Header, multipleSize_lines) = self.generateSizeFieldFromBeginingOfField(symbol)
        # line_header.extend(multipleSize_Header)
        # for i_line in range(0, len(lines)):
        #     lines[i_line] = lines[i_line] + "," + multipleSize_lines[i_line]

        # # Now we generate values for CRC32
        # (crc32Header, crc32Lines) = self.generateCRC32(symbol)
        # line_header.extend(crc32Header)
        # for i_line in range(0, len(lines)):
        #     line = lines[i_line]
        #     lines[i_line] = line + "," + crc32Lines[i_line]

        return (line_header, lines)

    def generateDataValues(self, cellsData):
        result = []
        for data in cellsData:
            result.append(int(data, 16))
        return result

    def generateSizeValues(self, cellsData):
        result = []
        for data in cellsData:
            result.append(len(data))
        return result

    def generateCRC32(self, symbol):
        header = []
        lines = []
        header.append("crc32:")
        messages = symbol.getMessages()
        for message in messages:
            line = []
            data = message.getStringData()
            rawContent = TypeConvertor.netzobRawToPythonRaw(data)
            valCrc32 = zlib.crc32(rawContent) & 0xFFFFFFFFL
            line.append(str(valCrc32))
            lines.append(",".join(line))
        return (header, lines)

    def generateSizeFieldFromBeginingOfField(self, symbol):
        header = []
        lines = []
        cells = dict()
        fields = symbol.getExtendedFields()
        for field in fields:
            if not field.isStatic():
                header.append("v:{0}[2]".format(field.getID()))
                cells[field] = field.getCells()

        for i_msg in range(0, len(symbol.getMessages())):
            line = []
            for field in cells.keys():
                entry = cells[field][i_msg]
                for k in range(2, 3, 2):
                    if len(entry) > k:
                        line.append(TypeConvertor.netzobRawToDecimal(entry[:k]))
                    else:
                        line.append(TypeConvertor.netzobRawToDecimal(entry))

            lines.append(",".join(line))

        print lines

        return (header, lines)

    def generateFieldValuesLines(self, cells):
        header = []
        lines = []

        nbMessage = len(cells[cells.keys()[0]])

        for field in cells.keys():
            header.append("v:{0}".format(field.getID()))
            header.append("s:{0}".format(field.getID()))

        for i_msg in range(0, nbMessage):
            line = []
            for field in cells.keys():
                entry = cells[field][i_msg]
                line.extend(self.generateCSVForData(entry))
            lines.append(",".join(line))
        return (header, lines)

    def generateCSVForData(self, data):
        result = []
        result.append(TypeConvertor.netzobRawToDecimal(data))
        result.append(len(data))
        return result
