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
from gi.repository import Gtk, Gdk
from gi.repository import Pango
import gi
from gi.repository import GObject
from netzob.UI.Vocabulary.Controllers.OptionalPanelsController import OptionalPanelsController
gi.require_version('Gtk', '3.0')
import logging
import copy
import os
import uuid

#+----------------------------------------------
#| Local Imports
#+----------------------------------------------
from netzob.UI.NetzobWidgets import NetzobLabel, NetzobButton, NetzobFrame, NetzobComboBoxEntry, \
    NetzobProgressBar, NetzobErrorMessage, NetzobInfoMessage
from netzob.Common.Threads.Tasks.ThreadedTask import ThreadedTask, TaskError
from netzob.Common.Threads.Job import Job
from netzob.Common.Type.TypeConvertor import TypeConvertor
from netzob.Common.Symbol import Symbol
from netzob.Common.ProjectConfiguration import ProjectConfiguration
from netzob.Common.Models.RawMessage import RawMessage
from netzob.Common.MMSTD.Dictionary.Variables.DataVariable import DataVariable
from netzob.Common.MMSTD.Dictionary.Variables.AlternateVariable import AlternateVariable
from netzob.Common.Type.Format import Format
from netzob.Common.Type.UnitSize import UnitSize
from netzob.Common.Type.Sign import Sign
from netzob.Common.Type.Endianess import Endianess
from netzob.Inference.Vocabulary.SearchView import SearchView
from netzob.UI.Vocabulary.Views.VocabularyView import VocabularyView
from netzob.UI.Vocabulary.Views.MessagesDistributionView import MessagesDistributionView
from netzob.UI.Vocabulary.Controllers.TreeSymbolController import TreeSymbolController
from netzob.UI.Vocabulary.Controllers.TreeMessageController import TreeMessageController
from netzob.UI.Vocabulary.Controllers.TreeTypeStructureController import TreeTypeStructureController
from netzob.UI.Vocabulary.Controllers.TreePropertiesController import TreePropertiesController
from netzob.UI.Vocabulary.Controllers.TreeSearchController import TreeSearchController
from netzob.UI.Vocabulary.Controllers.SequenceAlignmentController import SequenceAlignmentController
from netzob.UI.Vocabulary.Controllers.ForcePartitioningController import ForcePartitioningController
from netzob.UI.Vocabulary.Controllers.SimplePartitioningController import SimplePartitioningController
from netzob.UI.Vocabulary.Controllers.SmoothPartitioningController import SmoothPartitioningController
from netzob.UI.Vocabulary.Controllers.ResetPartitioningController import ResetPartitioningController
from netzob.UI.Vocabulary.Controllers.FindSizeFieldsController import FindSizeFieldsController
from netzob.Inference.Vocabulary.Alignment.NeedlemanAndWunsch import NeedlemanAndWunsch
from netzob.Inference.Vocabulary.Searcher import Searcher

from netzob.Inference.Vocabulary.DataCarver import DataCarver


#+----------------------------------------------
#| VocabularyController:
#|     GUI for vocabulary inference
#+----------------------------------------------
class VocabularyController:

    #+----------------------------------------------
    #| Called when user select a new trace
    #+----------------------------------------------
    def new(self):
        self.treeMessageController.clear()
        self.treeSymbolController.clear()
        self.optionalPanelsController.clear()

        # Update the combo for choosing the format
        possible_choices = Format.getSupportedFormats()
        global_format = self.netzob.getCurrentProject().getConfiguration().getVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_GLOBAL_FORMAT)
        self.view.comboDisplayFormat.disconnect(self.comboDisplayFormat_handler)
        self.view.comboDisplayFormat.set_model(Gtk.ListStore(str))  # Clear the list
        for i in range(len(possible_choices)):
            self.view.comboDisplayFormat.append_text(possible_choices[i])
            if possible_choices[i] == global_format:
                self.view.comboDisplayFormat.set_active(i)
        self.comboDisplayFormat_handler = self.view.comboDisplayFormat.connect("changed", self.updateDisplayFormat)

        # Update the combo for choosing the unit size
        possible_choices = [UnitSize.NONE, UnitSize.BITS4, UnitSize.BITS8, UnitSize.BITS16, UnitSize.BITS32, UnitSize.BITS64]
        global_unitsize = self.netzob.getCurrentProject().getConfiguration().getVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_GLOBAL_UNITSIZE)
        self.view.comboDisplayUnitSize.disconnect(self.comboDisplayUnitSize_handler)
        self.view.comboDisplayUnitSize.set_model(Gtk.ListStore(str))  # Clear the list

        activeUnitSizefound = False
        for i in range(len(possible_choices)):
            self.view.comboDisplayUnitSize.append_text(possible_choices[i])
            if possible_choices[i] == global_unitsize:
                self.view.comboDisplayUnitSize.set_active(i)
                activeUnitSizefound = True
        if not activeUnitSizefound:
            self.view.comboDisplayUnitSize.set_active(0)
        self.comboDisplayUnitSize_handler = self.view.comboDisplayUnitSize.connect("changed", self.updateDisplayUnitSize)

        # Update the combo for choosing the displayed sign
        possible_choices = [Sign.SIGNED, Sign.UNSIGNED]
        global_sign = self.netzob.getCurrentProject().getConfiguration().getVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_GLOBAL_SIGN)
        self.view.comboDisplaySign.disconnect(self.comboDisplaySign_handler)
        self.view.comboDisplaySign.set_model(Gtk.ListStore(str))  # Clear the list
        for i in range(len(possible_choices)):
            self.view.comboDisplaySign.append_text(possible_choices[i])
            if possible_choices[i] == global_sign:
                self.view.comboDisplaySign.set_active(i)
        self.comboDisplaySign_handler = self.view.comboDisplaySign.connect("changed", self.updateDisplaySign)

        # Update the combo for choosing the displayed endianess
        possible_choices = [Endianess.BIG, Endianess.LITTLE]
        global_endianess = self.netzob.getCurrentProject().getConfiguration().getVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_GLOBAL_ENDIANESS)
        self.view.comboDisplayEndianess.disconnect(self.comboDisplayEndianess_handler)
        self.view.comboDisplayEndianess.set_model(Gtk.ListStore(str))  # Clear the list
        for i in range(len(possible_choices)):
            self.view.comboDisplayEndianess.append_text(possible_choices[i])
            if possible_choices[i] == global_endianess:
                self.view.comboDisplayEndianess.set_active(i)
        self.comboDisplayEndianess_handler = self.view.comboDisplayEndianess.connect("changed", self.updateDisplayEndianess)

    def update(self):
        self.treeMessageController.update()
        self.treeSymbolController.update()
        self.optionalPanelsController.update()
        self.treePropertiesController.update()
        self.treeSearchController.update()
        self.treeTypeStructureController.update()

    def clear(self):
        self.treeMessageController.clear()
        self.treeSymbolController.clear()
        self.optionalPanelsController.clear()

    def kill(self):
        pass

    def save(self, aFile):
        pass

    #+----------------------------------------------
    #| Constructor:
    #| @param netzob: the netzob main class
    #+----------------------------------------------
    def __init__(self, netzob):
        self.netzob = netzob
        self.log = logging.getLogger('netzob.UI.Vocabulary.Controllers.VocabularyController.py')

        ## Main views
        # Messages view
        self.treeMessageController = TreeMessageController(self.netzob, self)
        # Symbols view
        self.treeSymbolController = TreeSymbolController(self.netzob, self)

        ## Optional panels
        self.optionalPanelsController = OptionalPanelsController(self.netzob, self)

        # Symbol definition view
        self.treeTypeStructureController = TreeTypeStructureController(self.netzob, self)
        self.optionalPanelsController.registerOptionalPanel(self.treeTypeStructureController)
        # Search view
        self.treeSearchController = TreeSearchController(self.netzob, self)
        self.optionalPanelsController.registerOptionalPanel(self.treeSearchController)
        # Properties view
        self.treePropertiesController = TreePropertiesController(self.netzob, self)
        self.optionalPanelsController.registerOptionalPanel(self.treePropertiesController)

        self.view = VocabularyView(self.netzob, self)
        self.initCallbacks()

    def initCallbacks(self):
        self.view.butSeqAlignment.connect("clicked", self.sequenceAlignmentOnAllSymbols_cb)
        self.view.butForcePartitioning.connect("clicked", self.forcePartitioningOnAllSymbols_cb)
        self.view.butSimplePartitioning.connect("clicked", self.simplePartitioningOnAllSymbols_cb)
        self.view.butSmoothPartitioning.connect("clicked", self.smoothPartitioningOnAllSymbols_cb)
        self.view.butResetPartitioning.connect("clicked", self.resetPartitioningOnAllSymbols_cb)
        self.view.butFreezePartitioning.connect("clicked", self.freezePartitioning_cb)
        self.view.butMessagesDistribution.connect("clicked", self.messagesDistribution_cb)
        self.view.butDataCarving.connect("clicked", self.dataCarving_cb)
        self.view.butFindSizeFields.connect("clicked", self.findSizeFields_cb)
        self.view.butEnvDependencies.connect("clicked", self.env_dependencies_cb)
        self.comboDisplayFormat_handler = self.view.comboDisplayFormat.connect("changed", self.updateDisplayFormat)
        self.comboDisplayUnitSize_handler = self.view.comboDisplayUnitSize.connect("changed", self.updateDisplayUnitSize)
        self.comboDisplaySign_handler = self.view.comboDisplaySign.connect("changed", self.updateDisplaySign)
        self.comboDisplayEndianess_handler = self.view.comboDisplayEndianess.connect("changed", self.updateDisplayEndianess)
        self.view.butSearch.connect("clicked", self.search_cb)

    #+----------------------------------------------
    #| Called when user wants to modify the format displayed
    #+----------------------------------------------
    def updateDisplayFormat(self, combo):
        # Sanity checks
        if self.netzob.getCurrentProject() is None:
            NetzobErrorMessage(_("No project selected."))
            return

        # Set the format choice as default
        aFormat = combo.get_active_text()
        configuration = self.netzob.getCurrentProject().getConfiguration()
        configuration.setVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_GLOBAL_FORMAT, aFormat)

        # Apply choice on each symbol
        for symbol in self.netzob.getCurrentProject().getVocabulary().getSymbols():
            symbol.setFormat(aFormat)
        self.update()

    #+----------------------------------------------
    #| Called when user wants to modify the unit size displayed
    #+----------------------------------------------
    def updateDisplayUnitSize(self, combo):
        # Sanity checks
        if self.netzob.getCurrentProject() is None:
            NetzobErrorMessage(_("No project selected."))
            return

        # Set the unitSize choice as default
        unitSize = combo.get_active_text()
        configuration = self.netzob.getCurrentProject().getConfiguration()
        configuration.setVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_GLOBAL_UNITSIZE, unitSize)

        # Apply choice on selected symbol
        for symbol in self.netzob.getCurrentProject().getVocabulary().getSymbols():
            symbol.setUnitSize(unitSize)
        self.update()

    #+----------------------------------------------
    #| Called when user wants to modify the sign displayed
    #+----------------------------------------------
    def updateDisplaySign(self, combo):
        # Sanity checks
        if self.netzob.getCurrentProject() is None:
            NetzobErrorMessage(_("No project selected."))
            return

        # Set the sign choice as default
        sign = combo.get_active_text()
        configuration = self.netzob.getCurrentProject().getConfiguration()
        configuration.setVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_GLOBAL_SIGN, sign)

        # Apply choice on each symbol
        for symbol in self.netzob.getCurrentProject().getVocabulary().getSymbols():
            symbol.setSign(sign)
        self.update()

    #+----------------------------------------------
    #| Called when user wants to modify the endianess displayed
    #+----------------------------------------------
    def updateDisplayEndianess(self, combo):
        # Sanity checks
        if self.netzob.getCurrentProject() is None:
            NetzobErrorMessage(_("No project selected."))
            return

        # Set the endianess choice as default
        endianess = combo.get_active_text()
        configuration = self.netzob.getCurrentProject().getConfiguration()
        configuration.setVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_GLOBAL_ENDIANESS, endianess)

        # Apply choice on selected symbol
        for symbol in self.netzob.getCurrentProject().getVocabulary().getSymbols():
            symbol.setEndianess(endianess)
        self.update()

    def sequenceAlignmentOnAllSymbols_cb(self, widget):
        # Sanity checks
        if self.netzob.getCurrentProject() is None:
            NetzobErrorMessage(_("No project selected."))
            return
        # Retrieve all the symbols
        project = self.netzob.getCurrentProject()
        symbols = project.getVocabulary().getSymbols()
        # Execute the process of alignment (show the gui...)
        sequenceAlignment = SequenceAlignmentController(self.netzob, self)
        sequenceAlignment.sequenceAlignment(symbols)

    def forcePartitioningOnAllSymbols_cb(self, widget):
        # Sanity checks
        if self.netzob.getCurrentProject() is None:
            NetzobErrorMessage(_("No project selected."))
            return
        # Retrieve all the symbols
        project = self.netzob.getCurrentProject()
        symbols = project.getVocabulary().getSymbols()
        # Execute the process of alignment (show the gui...)
        forcePartitioning = ForcePartitioningController(self.netzob, self)
        forcePartitioning.forcePartitioning(symbols)

    def simplePartitioningOnAllSymbols_cb(self, widget):
        # Sanity checks
        if self.netzob.getCurrentProject() is None:
            NetzobErrorMessage(_("No project selected."))
            return
        # Retrieve all the symbols
        project = self.netzob.getCurrentProject()
        symbols = project.getVocabulary().getSymbols()
        # Execute the process of alignment (show the gui...)
        simplePartitioning = SimplePartitioningController(self.netzob, self)
        simplePartitioning.simplePartitioning(symbols)

    def smoothPartitioningOnAllSymbols_cb(self, widget):
        # Sanity checks
        if self.netzob.getCurrentProject() is None:
            NetzobErrorMessage(_("No project selected."))
            return
        # Retrieve all the symbols
        project = self.netzob.getCurrentProject()
        symbols = project.getVocabulary().getSymbols()
        # Execute the process of alignment (show the gui...)
        smoothPartitioning = SmoothPartitioningController(self.netzob, self)
        smoothPartitioning.smoothPartitioning(symbols)

    def resetPartitioningOnAllSymbols_cb(self, widget):
        # Sanity checks
        if self.netzob.getCurrentProject() is None:
            NetzobErrorMessage(_("No project selected."))
            return
        # Retrieve all the symbols
        project = self.netzob.getCurrentProject()
        symbols = project.getVocabulary().getSymbols()
        # Add all the messages in a uniq symbol
        for symbol in symbols[1:]:
            for message in symbol.getMessages():
                symbols[0].addMessage(message)
        vocabulary = self.netzob.getCurrentProject().getVocabulary()
        vocabulary.setSymbols([symbols[0]])
        self.treeSymbolController.selectedSymbol = vocabulary.getSymbols()[0]
        resetPartitioning = ResetPartitioningController(self.netzob, self)
        resetPartitioning.resetPartitioning(vocabulary.getSymbols())
        self.update()

    #+----------------------------------------------
    #| Called when user wants to freeze partitioning (at the regex level)
    #+----------------------------------------------
    def freezePartitioning_cb(self, button):
        # Sanity checks
        if self.netzob.getCurrentProject() is None:
            NetzobErrorMessage(_("No project selected."))
            return
        if self.treeSymbolController.selectedSymbol is None:
            NetzobErrorMessage(_("No symbol selected."))
            return

        self.treeSymbolController.selectedSymbol.freezePartitioning()
        self.update()
        NetzobInfoMessage(_("Freezing done."))

    #+----------------------------------------------
    #| Called when user wants to execute data carving
    #+----------------------------------------------
    def dataCarving_cb(self, button):
        # Sanity checks
        if self.netzob.getCurrentProject() is None:
            NetzobErrorMessage(_("No project selected."))
            return
        if self.treeSymbolController.selectedSymbol is None:
            NetzobErrorMessage(_("No symbol selected."))
            return

        self.log.info(_("Execute Data Carving on symbol ${0}").format(self.treeSymbolController.selectedSymbol.getName()))
        self.executeDataCarving(self.treeSymbolController.selectedSymbol)

        # Active the messages and the search view
        self.netzob.getCurrentProject().getConfiguration().setVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_DISPLAY_MESSAGES, True)
        self.netzob.getCurrentProject().getConfiguration().setVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_DISPLAY_SEARCH, True)
        self.netzob.getMenu().setDisplaySearchViewActiveStatus(True)
        # We update the different views
        self.update()

    def executeDataCarving(self, symbol):
        # Initialize the searcher
        carver = DataCarver(self.netzob.getCurrentProject())

        # Execute it
        searchTasks = carver.execute(symbol)

        # Give the results to the dedicated view
        for task in searchTasks:
            self.treeSearchController.update(task)
#
#        box = self.treeSymbolController.selectedSymbol.dataCarving()
#        if box is not None:
#            NetzobErrorMessage("No data found in messages and fields.")
#        else:
#            dialog = Gtk.Dialog(title="Data carving results", flags=0, buttons=None)
#            dialog.vbox.pack_start(box, True, True, 0)
#            dialog.show()

    #+----------------------------------------------
    #| Called when user wants to search data in messages
    #+----------------------------------------------
    def search_cb(self, button):
        # Sanity checks
        if self.netzob.getCurrentProject() is None:
            NetzobErrorMessage(_("No project selected."))
            return
        # HUM HUM, not very nice I know !!!! TODO
        self.prepareSearch(self.view.searchEntry.get_text(), self.view.typeCombo.get_active_text())

    def prepareSearch(self, searchedPattern, typeOfPattern):
        if len(searchedPattern) == 0:
            NetzobErrorMessage(_("Do not start the searching process since no pattern has been provided"))
            return

        if len(typeOfPattern) == 0:
            NetzobErrorMessage(_("Do not start the searching process since no type has been provided"))
            return

        self.log.debug(_("User searches for {0} of type {1}").format(searchedPattern, typeOfPattern))
        self.search(searchedPattern, typeOfPattern)

        # Active the messages and the search view
        self.netzob.getCurrentProject().getConfiguration().setVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_DISPLAY_MESSAGES, True)
        self.netzob.getCurrentProject().getConfiguration().setVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_DISPLAY_SEARCH, True)
        self.netzob.getMenu().setDisplaySearchViewActiveStatus(True)
        # We update the different views
        self.update()

    def prepareSearchInSymbol(self, searchedPattern, typeOfPattern, symbol):
        if len(searchedPattern) == 0:
            NetzobErrorMessage(_("Do not start the searching process since no pattern has been provided"))
            return

        if len(typeOfPattern) == 0:
            NetzobErrorMessage(_("Do not start the searching process since no type has been provided"))
            return

        self.log.debug(_("User searches for {0} of type {1} in symbol {2}").format(searchedPattern, typeOfPattern, str(symbol.getName())))

        self.search(searchedPattern, typeOfPattern, "Symbol", symbol)

        # Active the messages and the search view
        self.netzob.getCurrentProject().getConfiguration().setVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_DISPLAY_MESSAGES, True)
        self.netzob.getCurrentProject().getConfiguration().setVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_DISPLAY_SEARCH, True)
        self.netzob.getMenu().setDisplaySearchViewActiveStatus(True)
        # We update the different views
        self.update()

    def search(self, pattern, typeOfPattern, type=None, inclusion=None):
        # Initialize the searcher
        searcher = Searcher(self.netzob.getCurrentProject())

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
            self.log.debug(" - " + str(data))

        # Then we search them in the list of messages included in the vocabulary
        if type is None:
            searchTasks = searcher.search(searchedData)
        elif type == "Symbol" and inclusion is not None:
            searchTasks = searcher.searchInSymbol(searchedData, inclusion)

        # Give the results to the dedicated view
        self.treeSearchController.update(searchTasks)

    #+----------------------------------------------
    #| Called when user wants to find the potential size fields
    #+----------------------------------------------
    def findSizeFields_cb(self, button):
        # Sanity checks
        if self.netzob.getCurrentProject() is None:
            NetzobErrorMessage(_("No project selected."))
            return
        if self.treeSymbolController.selectedSymbol is None:
            NetzobErrorMessage(_("No symbol selected."))
            return

        findSizeFields = FindSizeFieldsController(self.netzob, self)
        findSizeFields.findSizeFields()

    #+----------------------------------------------
    #| Called when user wants to identifies environment dependencies
    #+----------------------------------------------
    def env_dependencies_cb(self, button):
        # Sanity checks
        if self.netzob.getCurrentProject() is None:
            NetzobErrorMessage(_("No project selected."))
            return

        # Initialize the searcher
        searcher = Searcher(self.netzob.getCurrentProject())

        # Display the search view
        self.netzob.getMenu().setDisplaySearchViewActiveStatus(True)
        self.update()

        # Generate the different researched data based on message properties
        for symbol in self.netzob.getCurrentProject().getVocabulary().getSymbols():
            for message in symbol.getMessages():
                for property in message.getProperties():
                    (propertyName, propertyType, propertyValue) = property
                    if propertyType == Format.STRING:
                        searchTasks = searcher.searchInMessage(searcher.getSearchedDataForString(str(propertyValue)), message)
                        self.treeSearchController.update(searchTasks)
                    elif propertyType == Format.IP:
                        searchTasks = searcher.searchInMessage(searcher.getSearchedDataForIP(str(propertyValue)), message)
                        self.treeSearchController.update(searchTasks)
                    elif propertyType == Format.DECIMAL:
                        searchTasks = searcher.searchInMessage(searcher.getSearchedDataForDecimal(str(propertyValue)), message)
                        self.treeSearchController.update(searchTasks)

    #+----------------------------------------------
    #| Called when user wants to see the distribution of a symbol of messages
    #+----------------------------------------------
    def messagesDistribution_cb(self, but):
        # Sanity checks
        if self.netzob.getCurrentProject() is None:
            NetzobErrorMessage(_("No project selected."))
            return
        if self.treeSymbolController.selectedSymbol is None:
            NetzobErrorMessage(_("No symbol selected."))
            return

        messagesDistribution = MessagesDistributionView(self.treeSymbolController.selectedSymbol)
        messagesDistribution.buildDistributionView()

    #+----------------------------------------------
    #| Called when user wants to find ASN.1 fields
    #+----------------------------------------------
    def findASN1Fields_cb(self, button):
        # Sanity checks
        if self.netzob.getCurrentProject() is None:
            NetzobErrorMessage(_("No project selected."))
            return
        if self.treeSymbolController.selectedSymbol is None:
            NetzobErrorMessage(_("No symbol selected."))
            return

        box = self.treeSymbolController.selectedSymbol.findASN1Fields(self.netzob.getCurrentProject())
        if box is None:
            NetzobErrorMessage(_("No ASN.1 field found."))
        else:  # Show the results
            dialog = Gtk.Dialog(title=_("Find ASN.1 fields"), flags=0, buttons=None)
            dialog.vbox.pack_start(box, True, True, 0)
            dialog.show()

    def getPanel(self):
        return self.view.panel
