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

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+
from gi.repository import Gtk

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Plugins.Exporters.AbstractExporterController import AbstractExporterController
from MINERelationsView import MINERelationsView
from netzob.Common.Type.TypeConvertor import TypeConvertor
from RelationsMakerController import RelationsMakerController


class MINERelationsController(AbstractExporterController):
    """MINERelationsController:
            A controller liking the MINE exporter and its view in the netzob GUI.
    """

    JAR_PATH = "/home/gbt/Developpements/GITRepositories/netzob-resources/documentations/features/size_field_detection/MINE/MINE.jar"
    JAVA_PATH = "/usr/bin/java"

    def __init__(self, netzob, plugin):
        """Constructor of PeachExportController:

                @type netzob: MINEExporterPlugin
                @param netzob: the plugin instance
        """
        super(MINERelationsController, self).__init__(netzob, plugin)
        self.plugin = plugin
        self.view = MINERelationsView(self, plugin)

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

    def exportButton_clicked_cb(self, widget):
        """exportButton_clicked_cb:
            Callback executed when the user clicks on the export button"""

        selectedOutputDirectory = self.view.getSelectedOutputDirectory()
        if selectedOutputDirectory is None or not os.path.isdir(selectedOutputDirectory):
            logging.warning("Select an output directory ({0} is not valid)".format(selectedOutputDirectory))
            return

        csvSymbol = self.generateCSVs()
        if csvSymbol is None:
            logging.warning("Impossible to generate CSV.")
            return

        results = dict()
        for symbolName in csvSymbol.keys():
            (symbol, csv) = csvSymbol[symbolName]
            inputfilename = "MINE_{0}.csv".format(symbol.getName())
            csvPath = os.path.join(selectedOutputDirectory, inputfilename)
            f = open(csvPath, "w")
            f.write(csv)
            f.close()

            # Execute the JAR
            command = """{0} -jar {1} "{2}" -allPairs cv=0.7""".format(MINERelationsController.JAVA_PATH, MINERelationsController.JAR_PATH, csvPath)
            print "Executing command : {0}".format(command)
            subprocess.call(command, shell=True)

            # Parse results
            outputFile = "{0},allpairs,cv=0.7,B=n^0.6,Results.csv".format(inputfilename)
            pathOutputFile = os.path.join(selectedOutputDirectory, outputFile)
            f = open(pathOutputFile)
            contentOutputFile = f.read()
            f.close()

            tmpResults = self.parseResult(contentOutputFile, symbol)
            results[symbol.getName()] = tmpResults

        self.view.destroy()

        # Start the relation maker controller
        controller = RelationsMakerController(self.getPlugin(), self, results)
        controller.run()

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

    def generateCSVs(self):
        project = self.getCurrentProject()
        if project is None:
            return None

        symbols = self.getCurrentProject().getVocabulary().getSymbols()
        csvSymbol = dict()
        for symbol in symbols:
            csvSymbol[symbol.getName()] = (symbol, self.generateCSVForSymbol(symbol))
        return csvSymbol

    def generateCSVForSymbol(self, symbol):
        # First we compute the possible list of payloads
        mode = "short"

        lines = []
        line_header = []

        # Compute the table of values
        values = dict()
        fields = symbol.getExtendedFields()
        for field in fields:
                values[field] = field.getCells()

        # First we generate lines and header for fields values
        (field_line_header, field_lines) = self.generateFieldValuesLines(values)
        line_header.extend(field_line_header)
        lines.extend(field_lines)

        # Now we generate values for fields sizes
        (multipleSize_Header, multipleSize_lines) = self.generateSizeFieldFromBeginingOfField(symbol)
        line_header.extend(multipleSize_Header)
        for i_line in range(0, len(lines)):
            lines[i_line] = lines[i_line] + "," + multipleSize_lines[i_line]

        # Now we generate values for fields sizes
        (crc32Header, crc32Lines) = self.generateCRC32(symbol)
        line_header.extend(crc32Header)
        for i_line in range(0, len(lines)):
            line = lines[i_line]
            lines[i_line] = line + "," + crc32Lines[i_line]

        result = []
        result.append(','.join(line_header))
        result.extend(lines)

        return "\n".join(result)

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
        result.append(str(TypeConvertor.netzobRawToDecimal(data)))
        result.append(str(len(data)))
        return result

    def cancelButton_clicked_cb(self, widget):
        self.view.destroy()
