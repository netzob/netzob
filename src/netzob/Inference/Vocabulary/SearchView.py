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
from gettext import gettext as _
import logging
from gi.repository import Gtk
import gi
import uuid
gi.require_version('Gtk', '3.0')

#+----------------------------------------------
#| Local Imports
#+----------------------------------------------
from netzob.Inference.Vocabulary.Searcher import Searcher
from netzob.Common.Type.Format import Format


#+----------------------------------------------
#| SearchView:
#|     Class dedicated to host the search view
#+----------------------------------------------
class SearchView(object):

    #+----------------------------------------------
    #| Constructor:
    #+----------------------------------------------
    def __init__(self, project, messageViewGenerator, symbolViewGenerator):
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Modelization.SearchView.py')
        self.project = project
        self.messageViewGenerator = messageViewGenerator
        self.symbolViewGenerator = symbolViewGenerator

    def getPanel(self):
        # Create the main panel
        self.panel = Gtk.Table(rows=3, columns=3, homogeneous=False)
        self.panel.show()

        # Create the header (first row) with the search form
        # Search entry
        self.searchEntry = Gtk.Entry()
        self.searchEntry.show()

        # Combo to select the type of the input
        self.typeCombo = Gtk.ComboBoxText.new_with_entry()
        self.typeCombo.show()
        self.typeStore = Gtk.ListStore(str)
        self.typeCombo.set_model(self.typeStore)
        self.typeCombo.get_model().append([Format.STRING])
        self.typeCombo.get_model().append([Format.HEX])
        self.typeCombo.get_model().append([Format.BINARY])
        self.typeCombo.get_model().append([Format.OCTAL])
        self.typeCombo.get_model().append([Format.DECIMAL])
        self.typeCombo.get_model().append([Format.IP])

        # Search button
        searchButton = Gtk.Button(_("Search"))
        searchButton.show()
        searchButton.connect("clicked", self.prepareSearchingOperation)

        self.panel.attach(self.searchEntry, 0, 1, 0, 1, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)
        self.panel.attach(self.typeCombo, 1, 2, 0, 1, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)
        self.panel.attach(searchButton, 2, 3, 0, 1, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)

        return self.panel

    def prepareSearchingOperation(self, button):
        searchedPattern = self.searchEntry.get_text()
        if len(searchedPattern) == 0:
            self.log.info(_("Do not start the searching process since no pattern was provided by the user"))
            return

        typeOfPattern = self.typeCombo.get_active_text()
        if len(typeOfPattern) == 0:
            self.log.info(_("Do not start the searching process since no type was provided by the user"))
            return

        self.log.debug(_("User searches for {0} of type {1}".format(searchedPattern, typeOfPattern)))
        self.search(searchedPattern, typeOfPattern)

    def search(self, pattern, typeOfPattern):

        # Initialize the searcher
        searcher = Searcher(self.project)

        # First we generate the different researched data
        searchedData = []
        if typeOfPattern == Format.IP:
            searchedData.extend(searcher.getSearchedDataForIP(pattern))
        if typeOfPattern == Format.BINARY:
            searchedData.extend(searcher.getSearchedDataForBinary(pattern))
        if typeOfPattern == Format.OCTAL:
            searchedData.extend(searcher.getSearchedDataForOctal(pattern))
        if typeOfPattern == Format.DECIMAL:
            searchedData.extend(searcher.getSearchedDataForDecimal(pattern))
        if typeOfPattern == Format.HEX:
            searchedData.extend(searcher.getSearchedDataForHexadecimal(pattern))
        if typeOfPattern == Format.STRING:
            searchedData.extend(searcher.getSearchedDataForString(pattern))

        if len(searchedData) == 0:
            self.log.warn(_("No data to search after were computed."))
            return

        self.log.debug(_("The following data will be searched for:"))
        for data in searchedData:
            self.log.info(" - " + str(data))

        # Then we search them in the list of messages included in the vocabulary
        searchTasks = searcher.search(searchedData)
        self.log.info(_("A number of {0} results found!").format(str(len(searchTasks))))

        # Colorize the segments
        self.colorizeResults(searchTasks)

        # Display the dedicated view
        self.updateView(searchTasks)

    def colorizeResults(self, searchTasks):
        colorizedSymbols = []
        for task in searchTasks:
            for result in task.getResults():
                for (start, end) in result.getSegments():
                    function = TextColorFunction(uuid.uuid4(), "Search", start, start + end + 1, "#DD0000")
                    message = result.getMessage()
                    message.addVisualizationFunction(function)
                    # colorize the associated symbol
                    symbol = self.project.getVocabulary().getSymbolWhichContainsMessage(message)
                    if not symbol in colorizedSymbols:
                        symbol.addVisualizationFunction(TextColorFunction(uuid.uuid4(), "Search", None, None, "#DD0000"))
                        colorizedSymbols.append(symbol)
#                    message.highlightSegment(start, end)
        # We update the different views
        self.messageViewGenerator.updateDefault()
        self.symbolViewGenerator.default()

    def updateView(self, tasks):

        self.tree = Gtk.TreeView()
        colResult = Gtk.TreeViewColumn()
        colResult.set_title(_("Search results"))

        cell = Gtk.CellRendererText()
        colResult.pack_start(cell, True)
        colResult.add_attribute(cell, "text", 0)

        treestore = Gtk.TreeStore(str)

        foundSymbols = dict()
        foundMessages = dict()

        for task in tasks:
            for result in task.getResults():
                # retrieve the symbol associated with the message
                symbol = self.project.getVocabulary().getSymbolWhichContainsMessage(result.getMessage())

                # Display the tree item for the symbol
                treeItemSymbol = None
                if str(symbol.getID()) in foundSymbols.keys():
                    treeItemSymbol = foundSymbols[str(symbol.getID())]
                else:
                    treeItemSymbol = treestore.append(None, [symbol.getName()])
                    foundSymbols[str(symbol.getID())] = treeItemSymbol

                # Display the tree item for the message
                treeItemMessage = None
                if str(result.getMessage().getID()) in foundMessages.keys():
                    treeItemMessage = foundMessages[str(result.getMessage().getID())]
                else:
                    treeItemMessage = treestore.append(treeItemSymbol, [result.getMessage().getID()])
                    foundMessages[str(result.getMessage().getID())] = treeItemMessage
                # Add the result
                treestore.append(treeItemMessage, [str(result.getSegments())])

        self.tree.append_column(colResult)
        self.tree.set_model(treestore)
        self.tree.show()

        self.panel.attach(self.tree, 0, 3, 1, 2, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)
