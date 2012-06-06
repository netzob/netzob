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
import gtk
import pango
import pygtk
import gobject
from netzob.Inference.Vocabulary.SizeFieldIdentifier import SizeFieldIdentifier
from netzob.Common.Filters.Mathematic.Base64Filter import Base64Filter
from netzob.Common.Filters.Mathematic.GZipFilter import GZipFilter
from netzob.Common.Filters.Mathematic.B22Filter import BZ2Filter
from netzob.Inference.Vocabulary.DataCarver import DataCarver
pygtk.require('2.0')
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
from netzob.Common.MMSTD.Dictionary.Variables.WordVariable import WordVariable
from netzob.Common.MMSTD.Dictionary.Variables.AlternateVariable import AlternateVariable
from netzob.Common.Type.Format import Format
from netzob.Common.Type.UnitSize import UnitSize
from netzob.Common.Type.Sign import Sign
from netzob.Common.Type.Endianess import Endianess
from netzob.Inference.Vocabulary.SearchView import SearchView
from netzob.Inference.Vocabulary.Entropy import Entropy
from netzob.Inference.Vocabulary.TreeViews.TreeSymbolGenerator import TreeSymbolGenerator
from netzob.Inference.Vocabulary.TreeViews.TreeMessageGenerator import TreeMessageGenerator
from netzob.Inference.Vocabulary.TreeViews.TreeTypeStructureGenerator import TreeTypeStructureGenerator
from netzob.Inference.Vocabulary.TreeViews.TreePropertiesGenerator import TreePropertiesGenerator
from netzob.Inference.Vocabulary.VariableView import VariableView
from netzob.Inference.Vocabulary.Alignment.NeedlemanAndWunsch import NeedlemanAndWunsch
from netzob.Inference.Vocabulary.TreeViews.TreeSearchGenerator import TreeSearchGenerator
from netzob.Inference.Vocabulary.Searcher import Searcher
from netzob.Inference.Vocabulary.OptionalViews import OptionalViews


#+----------------------------------------------
#| UImodelization:
#|     GUI for vocabulary inference
#+----------------------------------------------
class UImodelization:
    TARGET_TYPE_TEXT = 80
    TARGETS = [('text/plain', 0, TARGET_TYPE_TEXT)]

    #+----------------------------------------------
    #| Called when user select a new trace
    #+----------------------------------------------
    def new(self):
        # Update the combo for choosing the format
        possible_choices = Format.getSupportedFormats()
        global_format = self.netzob.getCurrentProject().getConfiguration().getVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_GLOBAL_FORMAT)
        self.comboDisplayFormat.disconnect(self.comboDisplayFormat_handler)
        self.comboDisplayFormat.set_model(gtk.ListStore(str))  # Clear the list
        for i in range(len(possible_choices)):
            self.comboDisplayFormat.append_text(possible_choices[i])
            if possible_choices[i] == global_format:
                self.comboDisplayFormat.set_active(i)
        self.comboDisplayFormat_handler = self.comboDisplayFormat.connect("changed", self.updateDisplayFormat)

        # Update the combo for choosing the unit size
        possible_choices = [UnitSize.NONE, UnitSize.BITS4, UnitSize.BITS8, UnitSize.BITS16, UnitSize.BITS32, UnitSize.BITS64]
        global_unitsize = self.netzob.getCurrentProject().getConfiguration().getVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_GLOBAL_UNITSIZE)
        self.comboDisplayUnitSize.disconnect(self.comboDisplayUnitSize_handler)
        self.comboDisplayUnitSize.set_model(gtk.ListStore(str))  # Clear the list

        activeUnitSizefound = False
        for i in range(len(possible_choices)):
            self.comboDisplayUnitSize.append_text(possible_choices[i])
            if possible_choices[i] == global_unitsize:
                self.comboDisplayUnitSize.set_active(i)
                activeUnitSizefound = True
        if not activeUnitSizefound:
            self.comboDisplayUnitSize.set_active(0)
        self.comboDisplayUnitSize_handler = self.comboDisplayUnitSize.connect("changed", self.updateDisplayUnitSize)

        # Update the combo for choosing the displayed sign
        possible_choices = [Sign.SIGNED, Sign.UNSIGNED]
        global_sign = self.netzob.getCurrentProject().getConfiguration().getVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_GLOBAL_SIGN)
        self.comboDisplaySign.disconnect(self.comboDisplaySign_handler)
        self.comboDisplaySign.set_model(gtk.ListStore(str))  # Clear the list
        for i in range(len(possible_choices)):
            self.comboDisplaySign.append_text(possible_choices[i])
            if possible_choices[i] == global_sign:
                self.comboDisplaySign.set_active(i)
        self.comboDisplaySign_handler = self.comboDisplaySign.connect("changed", self.updateDisplaySign)

        # Update the combo for choosing the displayed endianess
        possible_choices = [Endianess.BIG, Endianess.LITTLE]
        global_endianess = self.netzob.getCurrentProject().getConfiguration().getVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_GLOBAL_ENDIANESS)
        self.comboDisplayEndianess.disconnect(self.comboDisplayEndianess_handler)
        self.comboDisplayEndianess.set_model(gtk.ListStore(str))  # Clear the list
        for i in range(len(possible_choices)):
            self.comboDisplayEndianess.append_text(possible_choices[i])
            if possible_choices[i] == global_endianess:
                self.comboDisplayEndianess.set_active(i)
        self.comboDisplayEndianess_handler = self.comboDisplayEndianess.connect("changed", self.updateDisplayEndianess)

    def update(self):
        self.updateTreeStoreMessage()
        self.updateTreeStoreSearchView()
        self.updateTreeStoreSymbol()
        self.updateTreeStoreTypeStructure()
        self.updateTreeStoreProperties()
        self.optionalViews.update()

    def clear(self):
        self.selectedSymbol = None

    def kill(self):
        pass

    def save(self, aFile):
        pass

    #+----------------------------------------------
    #| Constructor:
    #| @param netzob: the netzob main class
    #+----------------------------------------------
    def __init__(self, netzob):
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Inference.Vocabulary.UImodelization.py')
        self.netzob = netzob
        self.selectedSymbol = None
        self.selectedMessage = None
        # Messages
        self.treeMessageGenerator = TreeMessageGenerator()
        self.treeMessageGenerator.initialization()
        # Symbols
        self.treeSymbolGenerator = TreeSymbolGenerator(self.netzob)
        self.treeSymbolGenerator.initialization()

        # Optional views
        self.optionalViews = OptionalViews()
        # Register its subviews
        # Symbol definition
        self.treeTypeStructureGenerator = TreeTypeStructureGenerator()
        self.treeTypeStructureGenerator.initialization()
        self.optionalViews.registerView(self.treeTypeStructureGenerator)
        # Search view
        self.treeSearchGenerator = TreeSearchGenerator(self.netzob)
        self.treeSearchGenerator.initialization()
        self.treeSearchGenerator.getTreeview().connect('button-press-event', self.button_press_on_search_results)
        self.optionalViews.registerView(self.treeSearchGenerator)
        # Properties view
        self.treePropertiesGenerator = TreePropertiesGenerator(self.netzob)
        self.treePropertiesGenerator.initialization()
        self.optionalViews.registerView(self.treePropertiesGenerator)

        # Definition of the Sequence Onglet
        # First we create an VBox which hosts the two main children
        self.panel = gtk.VBox(False, spacing=0)
        self.panel.show()
        self.defer_select = False

        #+----------------------------------------------
        #| TOP PART OF THE GUI : BUTTONS
        #+----------------------------------------------
        topPanel = gtk.HBox(False, spacing=2)
        topPanel.show()
        self.panel.pack_start(topPanel, False, False, 0)

        ## Message format inference
        frame = NetzobFrame("1 - Message format inference")
        topPanel.pack_start(frame, False, False, 0)
        table = gtk.Table(rows=5, columns=2, homogeneous=False)
        table.show()
        frame.add(table)

        # Widget for sequence alignment
        but = NetzobButton("Sequence alignment")
        but.set_tooltip_text("Automatically discover the best alignment of messages")
        but.connect("clicked", self.sequenceAlignmentOnAllSymbols)
#        but.show()
        table.attach(but, 0, 2, 0, 1, xoptions=gtk.FILL | gtk.EXPAND, yoptions=gtk.FILL, xpadding=2, ypadding=2)

        # Widget for forcing partitioning delimiter
        but = NetzobButton("Force partitioning")
        but.connect("clicked", self.forcePartitioningOnAllSymbols)
        but.set_tooltip_text("Set a delimiter to force partitioning")
        table.attach(but, 0, 2, 1, 2, xoptions=gtk.FILL | gtk.EXPAND, yoptions=gtk.FILL, xpadding=2, ypadding=2)

        # Widget for simple partitioning
        but = NetzobButton("Simple partitioning")
        but.connect("clicked", self.simplePartitioningOnAllSymbols)
        but.set_tooltip_text("In order to show the simple differences between messages")
        table.attach(but, 0, 2, 2, 3, xoptions=gtk.FILL | gtk.EXPAND, yoptions=gtk.FILL, xpadding=2, ypadding=2)

        # Widget button slick regex
        but = NetzobButton("Smooth partitioning")
        but.connect("clicked", self.smoothPartitioningOnAllSymbols)
        but.set_tooltip_text("Merge small static fields with its neighbours")
        table.attach(but, 0, 2, 3, 4, xoptions=gtk.FILL | gtk.EXPAND, yoptions=gtk.FILL, xpadding=2, ypadding=2)

        # Widget button reset partitioning
        but = NetzobButton("Reset partitioning")
        but.connect("clicked", self.resetPartitioningOnAllSymbols)
        but.set_tooltip_text("Reset the current partitioning")
        table.attach(but, 0, 2, 4, 5, xoptions=gtk.FILL | gtk.EXPAND, yoptions=gtk.FILL, xpadding=2, ypadding=2)

        ## Field type inference
        frame = NetzobFrame("2 - Field type inference")
        topPanel.pack_start(frame, False, False, 0)
        table = gtk.Table(rows=5, columns=2, homogeneous=False)
        table.show()
        frame.add(table)

        # Widget button refine regex
        but = NetzobButton("Freeze partitioning")
        but.connect("clicked", self.freezePartitioning_cb)
        but.set_tooltip_text("Automatically find and freeze the boundaries (min/max of cell's size) for each fields")
        table.attach(but, 0, 1, 0, 1, xoptions=gtk.FILL | gtk.EXPAND, yoptions=gtk.FILL, xpadding=2, ypadding=2)

        # Widget button to show message distribution
        but = NetzobButton("Messages distribution")
        but.connect("clicked", self.messagesDistribution_cb)
        but.set_tooltip_text("Open a graph with messages distribution, separated by fields")
        table.attach(but, 0, 1, 1, 2, xoptions=gtk.FILL | gtk.EXPAND, yoptions=gtk.FILL, xpadding=2, ypadding=2)

        # Widget button data carving
        but = NetzobButton("Data carving")
        but.connect("clicked", self.dataCarving_cb)
        but.set_tooltip_text("Automatically look for known patterns of data (URL, IP, email, etc.)")
        table.attach(but, 0, 1, 2, 3, xoptions=gtk.FILL | gtk.EXPAND, yoptions=gtk.FILL, xpadding=2, ypadding=2)

        # Widget button to analyze for ASN.1 presence
#        but = NetzobButton("Find ASN.1 fields")
#        but.connect("clicked", self.findASN1Fields_cb)
#        table.attach(but, 0, 1, 3, 4, xoptions=gtk.FILL | gtk.EXPAND, yoptions=gtk.FILL, xpadding=2, ypadding=2)

        ## Dependencies inference
        frame = NetzobFrame("3 - Dependencies inference")
        topPanel.pack_start(frame, False, False, 0)
        table = gtk.Table(rows=4, columns=4, homogeneous=False)
        table.show()
        frame.add(table)

        # Widget button find size fields
        but = NetzobButton("Find size fields")
        but.connect("clicked", self.findSizeFields)
        but.set_tooltip_text("Automatically find potential size fields and associated payloads")
        table.attach(but, 0, 1, 0, 1, xoptions=gtk.FILL | gtk.EXPAND, yoptions=gtk.FILL, xpadding=2, ypadding=2)

        # Widget button for environment dependencies
        but = NetzobButton("Environment dependencies")
        but.connect("clicked", self.env_dependencies_cb)
        but.set_tooltip_text("Automatically look for environmental dependencies (retrieved during capture) in messages")
        table.attach(but, 0, 1, 1, 2, xoptions=gtk.FILL | gtk.EXPAND, yoptions=gtk.FILL, xpadding=2, ypadding=2)

        ## Visualization
        frame = NetzobFrame("4 - Visualization")
        topPanel.pack_start(frame, False, False, 0)
        table = gtk.Table(rows=4, columns=4, homogeneous=False)
        table.show()
        frame.add(table)

        # Widget for choosing the format
        label = NetzobLabel("Format : ")
        self.comboDisplayFormat = NetzobComboBoxEntry()
        self.comboDisplayFormat_handler = self.comboDisplayFormat.connect("changed", self.updateDisplayFormat)
        table.attach(label, 0, 1, 0, 1, xoptions=gtk.FILL, yoptions=0, xpadding=2, ypadding=0)
        table.attach(self.comboDisplayFormat, 1, 2, 0, 1, xoptions=gtk.FILL, yoptions=0, xpadding=2, ypadding=0)

        # Widget for choosing the unit size
        label = NetzobLabel("Unit size : ")
        self.comboDisplayUnitSize = NetzobComboBoxEntry()
        self.comboDisplayUnitSize_handler = self.comboDisplayUnitSize.connect("changed", self.updateDisplayUnitSize)
        table.attach(label, 0, 1, 1, 2, xoptions=gtk.FILL, yoptions=0, xpadding=2, ypadding=0)
        table.attach(self.comboDisplayUnitSize, 1, 2, 1, 2, xoptions=gtk.FILL, yoptions=0, xpadding=2, ypadding=0)

        # Widget for choosing the displayed sign
        label = NetzobLabel("Sign : ")
        self.comboDisplaySign = NetzobComboBoxEntry()
        self.comboDisplaySign_handler = self.comboDisplaySign.connect("changed", self.updateDisplaySign)
        table.attach(label, 0, 1, 2, 3, xoptions=gtk.FILL, yoptions=0, xpadding=2, ypadding=0)
        table.attach(self.comboDisplaySign, 1, 2, 2, 3, xoptions=gtk.FILL, yoptions=0, xpadding=2, ypadding=0)

        # Widget for choosing the displayed endianess
        label = NetzobLabel("Endianess : ")
        self.comboDisplayEndianess = NetzobComboBoxEntry()
        self.comboDisplayEndianess_handler = self.comboDisplayEndianess.connect("changed", self.updateDisplayEndianess)
        table.attach(label, 0, 1, 3, 4, xoptions=gtk.FILL, yoptions=0, xpadding=2, ypadding=0)
        table.attach(self.comboDisplayEndianess, 1, 2, 3, 4, xoptions=gtk.FILL, yoptions=0, xpadding=2, ypadding=0)

        ## Semantic inference
        frame = NetzobFrame("5 - Search data")
        topPanel.pack_start(frame, False, False, 0)
        table = gtk.Table(rows=4, columns=4, homogeneous=False)
        table.show()
        frame.add(table)

        # Widget button for search
        self.searchEntry = gtk.Entry()
        self.searchEntry.show()
        table.attach(self.searchEntry, 0, 1, 0, 1, xoptions=gtk.FILL | gtk.EXPAND, yoptions=gtk.FILL, xpadding=2, ypadding=2)

        # Combo to select the type of the input
        self.typeCombo = gtk.combo_box_entry_new_text()
        self.typeCombo.show()
        self.typeStore = gtk.ListStore(str)
        self.typeCombo.set_model(self.typeStore)
        self.typeCombo.get_model().append([Format.STRING])
        self.typeCombo.get_model().append([Format.HEX])
#        self.typeCombo.get_model().append([Format.BINARY])
#        self.typeCombo.get_model().append([Format.OCTAL])
        self.typeCombo.get_model().append([Format.DECIMAL])
        self.typeCombo.get_model().append([Format.IP])
        self.typeCombo.set_active(0)
        table.attach(self.typeCombo, 0, 1, 1, 2, xoptions=gtk.FILL | gtk.EXPAND, yoptions=gtk.FILL, xpadding=2, ypadding=2)

        but = NetzobButton("Search")
        but.connect("clicked", self.search_cb)
        but.set_tooltip_text("A search function available in different encoding format")
        table.attach(but, 0, 1, 2, 3, xoptions=gtk.FILL | gtk.EXPAND, yoptions=gtk.FILL, xpadding=2, ypadding=2)

        #+----------------------------------------------
        #| LEFT PART OF THE GUI : SYMBOL TREEVIEW
        #+----------------------------------------------
        bottomPanel = gtk.HPaned()
        bottomPanel.show()
        self.panel.pack_start(bottomPanel, True, True, 0)
        leftPanel = gtk.VBox(False, spacing=0)
#        leftPanel.set_size_request(-1, -1)
        leftPanel.show()
        bottomPanel.add(leftPanel)
        # Initialize the treeview generator for the symbols
        leftPanel.pack_start(self.treeSymbolGenerator.getScrollLib(), True, True, 0)
        # Attach to the treeview few actions (DnD, cursor and buttons handlers...)
        self.treeSymbolGenerator.getTreeview().enable_model_drag_dest(self.TARGETS, gtk.gdk.ACTION_DEFAULT | gtk.gdk.ACTION_MOVE)
        self.treeSymbolGenerator.getTreeview().connect("drag-data-received", self.drop_fromDND)
        self.treeSymbolGenerator.getTreeview().connect('button-press-event', self.button_press_on_treeview_symbols)

        #+----------------------------------------------
        #| RIGHT PART OF THE GUI :
        #| includes the messages treeview and the optional views in tabs
        #+----------------------------------------------
        rightPanel = gtk.VPaned()
        rightPanel.show()
        bottomPanel.add(rightPanel)
        # add the messages in the right panel
        rightPanel.add(self.treeMessageGenerator.getScrollLib())
        # Attach to the treeview few actions (DnD, cursor and buttons handlers...)
        self.treeMessageGenerator.getTreeview().enable_model_drag_source(gtk.gdk.BUTTON1_MASK, self.TARGETS, gtk.gdk.ACTION_DEFAULT | gtk.gdk.ACTION_MOVE)
        self.treeMessageGenerator.getTreeview().connect("drag-data-get", self.drag_fromDND)
        self.treeMessageGenerator.getTreeview().connect('button-press-event', self.button_press_on_treeview_messages)
        self.treeMessageGenerator.getTreeview().connect('button-release-event', self.button_release_on_treeview_messages)
        self.treeMessageGenerator.getTreeview().connect("row-activated", self.dbClickToChangeFormat)

        # find the optional views
        rightPanel.add(self.optionalViews.getPanel())

    def sequenceAlignmentOnAllSymbols(self, widget):
        # Sanity checks
        if self.netzob.getCurrentProject() == None:
            NetzobErrorMessage("No project selected.")
            return
        # Retrieve all the symbols
        project = self.netzob.getCurrentProject()
        symbols = project.getVocabulary().getSymbols()
        # Execute the process of alignment (show the gui...)
        self.sequenceAlignment(symbols)

    def sequenceAlignmentOnSpecifiedSymbols(self, widget, symbols):
        # Execute the process of alignment (show the gui...)
        self.sequenceAlignment(symbols)

    #+----------------------------------------------
    #| sequenceAlignment:
    #|   Parse the traces and store the results
    #+----------------------------------------------
    def sequenceAlignment(self, symbols):

        self.treeMessageGenerator.clear()
        self.treeSymbolGenerator.clear()
        self.treeTypeStructureGenerator.clear()
        self.update()

        dialog = gtk.Dialog(title="Sequence alignment", flags=0, buttons=None)
        panel = gtk.Table(rows=5, columns=3, homogeneous=False)
        panel.show()

        ## Similarity threshold
        label = NetzobLabel("Similarity threshold:")
        combo = gtk.combo_box_entry_new_text()
        combo.set_model(gtk.ListStore(str))
        combo.connect("changed", self.updateScoreLimit)
        possible_choices = [100, 95, 90, 85, 80, 75, 70, 65, 60, 55, 50, 45, 40, 35, 30, 25, 20, 15, 10, 5]

        min_equivalence = self.netzob.getCurrentProject().getConfiguration().getVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_EQUIVALENCE_THRESHOLD)
        for i in range(len(possible_choices)):
            combo.append_text(str(possible_choices[i]))
            if str(possible_choices[i]) == str(int(min_equivalence)):
                combo.set_active(i)
        combo.show()
        panel.attach(label, 0, 1, 0, 1, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        panel.attach(combo, 1, 2, 0, 1, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        ## UnitSize for alignment
        label = NetzobLabel("Unit size (in bits):")
        comboUnitSize = gtk.combo_box_entry_new_text()
        comboUnitSize.set_model(gtk.ListStore(str))
        possible_choices = [8, 4]

        for i in range(len(possible_choices)):
            comboUnitSize.append_text(str(possible_choices[i]))
        comboUnitSize.set_active(0)
        comboUnitSize.show()
        panel.attach(label, 0, 1, 1, 2, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        panel.attach(comboUnitSize, 1, 2, 1, 2, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        # Widget button activate orphan reduction
        butOrphanReduction = gtk.CheckButton("Orphan reduction")
        doOrphanReduction = self.netzob.getCurrentProject().getConfiguration().getVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_ORPHAN_REDUCTION)
        if doOrphanReduction:
            butOrphanReduction.set_active(True)
        else:
            butOrphanReduction.set_active(False)
        butOrphanReduction.connect("toggled", self.activeOrphanReduction)
        butOrphanReduction.show()
        panel.attach(butOrphanReduction, 0, 1, 2, 3, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        # Widget checkbox for selecting the slickery during alignement process
        but = gtk.CheckButton("Smooth alignment")
        doInternalSlick = self.netzob.getCurrentProject().getConfiguration().getVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_DO_INTERNAL_SLICK)
        if doInternalSlick:
            but.set_active(True)
        else:
            but.set_active(False)
        but.connect("toggled", self.activeInternalSlickRegexes)
        but.show()
        panel.attach(but, 1, 2, 2, 3, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        # Progress bar
        self.progressbarAlignment = NetzobProgressBar()
        panel.attach(self.progressbarAlignment, 0, 2, 3, 4, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        # Button
        searchButton = NetzobButton("Sequence alignment")
        searchButton.connect("clicked", self.sequenceAlignment_cb_cb, dialog, symbols, comboUnitSize)
        panel.attach(searchButton, 0, 2, 4, 5, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        dialog.vbox.pack_start(panel, True, True, 0)
        dialog.show()

    #+----------------------------------------------
    #| sequenceAlignment_cb_cb:
    #|   Launch a sequence alignment thread
    #+----------------------------------------------
    def sequenceAlignment_cb_cb(self, widget, dialog, symbols, comboUnitSize):
        self.currentExecutionOfAlignmentHasFinished = False
        # Start the progress bar
        gobject.timeout_add(100, self.do_pulse_for_sequenceAlignment)
        # Start the alignment JOB
        unitSize = int(comboUnitSize.get_active_text())
        Job(self.startSequenceAlignment(symbols, dialog, unitSize))

    #+----------------------------------------------
    #| startSequenceAlignment:
    #|   Execute the Job of the Alignment in a unsynchronized way
    #+----------------------------------------------
    def startSequenceAlignment(self, symbols, dialog, unitSize):
        self.currentExecutionOfAlignmentHasFinished = False

        alignmentSolution = NeedlemanAndWunsch(unitSize, self.percentOfAlignmentProgessBar)

        try:
            (yield ThreadedTask(alignmentSolution.alignSymbols, symbols, self.netzob.getCurrentProject()))
        except TaskError, e:
            self.log.error("Error while proceeding to the alignment : " + str(e))

        new_symbols = alignmentSolution.getLastResult()
        self.currentExecutionOfAlignmentHasFinished = True

        dialog.destroy()

        # Show the new symbol in the interface
        self.netzob.getCurrentProject().getVocabulary().setSymbols(new_symbols)
        if len(new_symbols) > 0:
            symbol = new_symbols[0]
            self.selectedSymbol = symbol
            self.treeMessageGenerator.default(self.selectedSymbol)
            self.treeSymbolGenerator.default(self.selectedSymbol)

    def percentOfAlignmentProgessBar(self, percent, message):
#        gobject.idle_add(self.progressbarAlignment.set_fraction, float(percent))
        if message == None:
            gobject.idle_add(self.progressbarAlignment.set_text, "")
        else:
            gobject.idle_add(self.progressbarAlignment.set_text, message)

    #+----------------------------------------------
    #| do_pulse_for_sequenceAlignment:
    #|   Computes if the progress bar must be updated or not
    #+----------------------------------------------
    def do_pulse_for_sequenceAlignment(self):
        if self.currentExecutionOfAlignmentHasFinished == False:
            self.progressbarAlignment.pulse()
            return True
        return False

    def forcePartitioningOnAllSymbols(self, widget):
        # Sanity checks
        if self.netzob.getCurrentProject() == None:
            NetzobErrorMessage("No project selected.")
            return
        # Retrieve all the symbols
        project = self.netzob.getCurrentProject()
        symbols = project.getVocabulary().getSymbols()
        # Execute the process of alignment (show the gui...)
        self.forcePartitioning(symbols)

    def forcePartitioningOnSpecifiedSymbols(self, widget, symbols):
        # Execute the process of alignment (show the gui...)
        self.forcePartitioning(symbols)

    #+----------------------------------------------
    #| forcePartitioning_cb:
    #|   Force the delimiter for partitioning
    #+----------------------------------------------
    def forcePartitioning(self, symbols):
        self.treeMessageGenerator.clear()
        self.treeSymbolGenerator.clear()
        self.treeTypeStructureGenerator.clear()
        self.update()
        dialog = gtk.Dialog(title="Force partitioning", flags=0, buttons=None)
        panel = gtk.Table(rows=3, columns=3, homogeneous=False)
        panel.show()

        # Label
        label = NetzobLabel("Delimiter: ")
        panel.attach(label, 0, 1, 0, 1, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        # Entry for delimiter
        entry = gtk.Entry(4)
        entry.show()
        panel.attach(entry, 1, 2, 0, 1, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        # Label
        label = NetzobLabel("Format type: ")
        panel.attach(label, 0, 1, 1, 2, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        # Delimiter type
        typeCombo = gtk.combo_box_entry_new_text()
        typeCombo.show()
        typeStore = gtk.ListStore(str)
        typeCombo.set_model(typeStore)
        typeCombo.get_model().append([Format.STRING])
        typeCombo.get_model().append([Format.HEX])
        typeCombo.set_active(0)
        panel.attach(typeCombo, 1, 2, 1, 2, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        # Button
        searchButton = NetzobButton("Force partitioning")
        searchButton.connect("clicked", self.forcePartitioning_cb_cb, dialog, typeCombo, entry, symbols)
        panel.attach(searchButton, 0, 2, 2, 3, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        dialog.vbox.pack_start(panel, True, True, 0)
        dialog.show()

    #+----------------------------------------------
    #| forcePartitioning_cb_cb:
    #|   Force the delimiter for partitioning
    #+----------------------------------------------
    def forcePartitioning_cb_cb(self, widget, dialog, aFormat, delimiter, symbols):
        aFormat = aFormat.get_active_text()
        delimiter = delimiter.get_text()
        delimiter = TypeConvertor.encodeGivenTypeToNetzobRaw(delimiter, aFormat)

        for symbol in symbols:
            symbol.forcePartitioning(self.netzob.getCurrentProject().getConfiguration(), aFormat, delimiter)

        self.update()
        dialog.destroy()

    def simplePartitioningOnAllSymbols(self, widget):
        # Sanity checks
        if self.netzob.getCurrentProject() == None:
            NetzobErrorMessage("No project selected.")
            return
        # Retrieve all the symbols
        project = self.netzob.getCurrentProject()
        symbols = project.getVocabulary().getSymbols()
        # Execute the process of alignment (show the gui...)
        self.simplePartitioning(symbols)

    def simplePartitioningOnSpecifiedSymbols(self, widget, symbols):
        # Sanity checks
        if self.netzob.getCurrentProject() == None:
            NetzobErrorMessage("No project selected.")
            return
        # Retrieve all the symbols
        project = self.netzob.getCurrentProject()
        # Execute the process of alignment (show the gui...)
        self.simplePartitioning(symbols)

    #+----------------------------------------------
    #| simplePartitioning:
    #|   Apply a simple partitioning
    #+----------------------------------------------
    def simplePartitioning(self, symbols):
        self.treeMessageGenerator.clear()
        self.treeSymbolGenerator.clear()
        self.treeTypeStructureGenerator.clear()
        self.update()
        dialog = gtk.Dialog(title="Simple partitioning", flags=0, buttons=None)
        panel = gtk.Table(rows=3, columns=3, homogeneous=False)
        panel.show()

        # Label
        label = NetzobLabel("Minimum unit size: ")
        panel.attach(label, 0, 1, 0, 1, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        # Delimiter type
        possible_choices = [UnitSize.NONE, UnitSize.BIT, UnitSize.BITS8, UnitSize.BITS16, UnitSize.BITS32, UnitSize.BITS64]
        typeCombo = NetzobComboBoxEntry()
        for i in range(len(possible_choices)):
            typeCombo.append_text(possible_choices[i])
            if possible_choices[i] == UnitSize.NONE:
                typeCombo.set_active(i)
        panel.attach(typeCombo, 1, 2, 0, 1, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        # Button
        searchButton = NetzobButton("Simple partitioning")
        searchButton.connect("clicked", self.simplePartitioning_cb_cb, dialog, typeCombo, symbols)
        panel.attach(searchButton, 0, 2, 2, 3, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        dialog.vbox.pack_start(panel, True, True, 0)
        dialog.show()

    #+----------------------------------------------
    #| simplePartitioning_cb_cb:
    #|   Apply a simple partitioning
    #+----------------------------------------------
    def simplePartitioning_cb_cb(self, widget, dialog, unitSize_widget, symbols):
        unitSize = unitSize_widget.get_active_text()
        for symbol in symbols:
            symbol.simplePartitioning(self.netzob.getCurrentProject().getConfiguration(), unitSize)
        dialog.destroy()
        self.update()

    def smoothPartitioningOnAllSymbols(self, widget):
        # Sanity checks
        if self.netzob.getCurrentProject() == None:
            NetzobErrorMessage("No project selected.")
            return
        # Retrieve all the symbols
        project = self.netzob.getCurrentProject()
        symbols = project.getVocabulary().getSymbols()
        # Execute the process of alignment (show the gui...)
        self.smoothPartitioning(symbols)

    def smoothPartitioningOnSpecifiedSymbols(self, widget, symbols):
        # Sanity checks
        if self.netzob.getCurrentProject() == None:
            NetzobErrorMessage("No project selected.")
            return
        # Execute the process of alignment (show the gui...)
        self.smoothPartitioning(symbols)

    #+----------------------------------------------
    #| Called when user wants to slick the current regexes
    #+----------------------------------------------
    def smoothPartitioning(self, symbols):
        # Sanity checks
        if self.netzob.getCurrentProject() == None:
            NetzobErrorMessage("No project selected.")
            return

        for symbol in symbols:
            symbol.slickRegex(self.netzob.getCurrentProject())

        self.update()

    def resetPartitioningOnAllSymbols(self, widget):
        # Sanity checks
        if self.netzob.getCurrentProject() == None:
            NetzobErrorMessage("No project selected.")
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
        self.selectedSymbol = vocabulary.getSymbols()[0]
        self.resetPartitioning(vocabulary.getSymbols())
        self.update()

    def resetPartitioningOnSpecifiedSymbols(self, widget, symbols):
        # Sanity checks
        if self.netzob.getCurrentProject() == None:
            NetzobErrorMessage("No project selected.")
            return
        # Execute the process of alignment (show the gui...)
        self.resetPartitioning(symbols)

    #+----------------------------------------------
    #| resetPartitioning_cb:
    #|   Called when user wants to reset the current alignment
    #+----------------------------------------------
    def resetPartitioning(self, symbols):
        # Sanity checks
        if self.netzob.getCurrentProject() == None:
            NetzobErrorMessage("No project selected.")
            return
        for symbol in symbols:
            symbol.resetPartitioning(self.netzob.getCurrentProject())
        self.update()

    #+----------------------------------------------
    #| button_press_on_treeview_symbols:
    #|   operation when the user click on the treeview.
    #|   mainly to open a contextual menu
    #+----------------------------------------------
    def button_press_on_treeview_symbols(self, treeview, event):
        # Sanity checks
        project = self.netzob.getCurrentProject()
        if project == None:
            NetzobErrorMessage("No project selected.")
            return
        if project.getVocabulary() == None:
            NetzobErrorMessage("The current project doesn't have any referenced vocabulary.")
            return

        x = int(event.x)
        y = int(event.y)
        clickedSymbol = self.treeSymbolGenerator.getSymbolAtPosition(x, y)

        if event.type == gtk.gdk.BUTTON_PRESS and event.button == 1 and clickedSymbol != None:
            self.selectedSymbol = clickedSymbol
            self.treeTypeStructureGenerator.setSymbol(self.selectedSymbol)
            self.updateTreeStoreTypeStructure()
            self.updateTreeStoreMessage()

        if event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
            self.build_context_menu_for_symbols(event, clickedSymbol)

    def button_release_on_treeview_messages(self, treeview, event):
        # re-enable selection
        treeview.get_selection().set_select_function(lambda * ignore: True)
        target = treeview.get_path_at_pos(int(event.x), int(event.y))
        if (self.defer_select and target and self.defer_select == target[0] and not (event.x == 0 and event.y == 0)):  # certain drag and drop
            treeview.set_cursor(target[0], target[1], False)
            self.defer_select = False

    #+----------------------------------------------
    #| button_press_on_treeview_messages:
    #|   operation when the user click on the treeview.
    #|   mainly to open a contextual menu
    #+----------------------------------------------
    def button_press_on_treeview_messages(self, treeview, event):
        target = treeview.get_path_at_pos(int(event.x), int(event.y))
        if (target and event.type == gtk.gdk.BUTTON_PRESS and not (event.state & (gtk.gdk.CONTROL_MASK | gtk.gdk.SHIFT_MASK)) and treeview.get_selection().path_is_selected(target[0])):
            # disable selection
            treeview.get_selection().set_select_function(lambda * ignore: False)
            self.defer_select = target[0]

        # Display the details of a packet
        if event.type == gtk.gdk.BUTTON_PRESS and event.button == 1:
            x = int(event.x)
            y = int(event.y)
            try:
                (path, treeviewColumn, x, y) = treeview.get_path_at_pos(x, y)
            except:
                # No message selected
                pass
            else:
                # A message is selected
                aIter = treeview.get_model().get_iter(path)
                if aIter:
                    if treeview.get_model().iter_is_valid(aIter):
                        message_id = treeview.get_model().get_value(aIter, 0)

                        # search for the message in the vocabulary
                        message = self.netzob.getCurrentProject().getVocabulary().getMessageByID(message_id)
                        self.selectedMessage = message

                        # update
                        self.updateTreeStoreProperties()

                        # Following line commented because of unused variable symbol
                        #symbol = self.treeMessageGenerator.getSymbol()
                        # Do nothing for now

        # Popup a menu
        elif event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
            self.log.debug("User requested a contextual menu (treeview messages)")
            x = int(event.x)
            y = int(event.y)
            (path, treeviewColumn, x, y) = treeview.get_path_at_pos(x, y)

            # Retrieve the selected message
            message_id = None
            aIter = treeview.get_model().get_iter(path)
            if aIter:
                if treeview.get_model().iter_is_valid(aIter):
                    message_id = treeview.get_model().get_value(aIter, 0)

            # Retrieve the selected column number
            iField = 0
            for col in treeview.get_columns():
                if col == treeviewColumn:
                    break
                iField += 1

            selectedField = None
            for field in self.treeMessageGenerator.getSymbol().getFields():
                if field.getIndex() == iField:
                    selectedField = field
            if selectedField == None:
                self.log.warn("Impossible to retrieve the clicked field !")
                return

            # Add entry to move seleted messages
            menu = gtk.Menu()
            listmessages = []
            (model, paths) = self.treeMessageGenerator.getTreeview().get_selection().get_selected_rows()
            for path in paths:
                aIter = model.get_iter(path)
                if(model.iter_is_valid(aIter)):
                    id_message = model.get_value(aIter, 0)
                    listmessages.append(id_message)

            subMenu = self.build_moveto_submenu(self.selectedSymbol, listmessages)
            item = gtk.MenuItem("Move to ...")
            item.set_submenu(subMenu)
            item.show()
            menu.append(item)

            # Add entry to edit field
            item = gtk.MenuItem("Edit field")
            item.show()
            item.connect("activate", self.displayPopupToEditField, selectedField)
            menu.append(item)

            # Add sub-entries to change the type of a specific column
            subMenu = self.build_encoding_submenu(selectedField, message_id)
            item = gtk.MenuItem("Field visualization")
            item.set_submenu(subMenu)
            item.show()
            menu.append(item)

            # Add sub-entries to add mathematic filters on a  specific column
            subMenuMathematicFilters = self.build_mathematicFilter_submenu(selectedField)
            item = gtk.MenuItem("Configure mathematic filters")
            item.set_submenu(subMenuMathematicFilters)
            item.show()
            menu.append(item)

            # Add entries to concatenate column
            concatMenu = gtk.Menu()
            if selectedField.getIndex() > 0:
                item = gtk.MenuItem("with precedent field")
                item.show()
                item.connect("activate", self.rightClickToConcatColumns, selectedField, "left")
                concatMenu.append(item)

                item = gtk.MenuItem("with all precedent field")
                item.show()
                item.connect("activate", self.rightClickToConcatColumns, selectedField, "allleft")
                concatMenu.append(item)

            if selectedField.getIndex() < len(self.treeMessageGenerator.getSymbol().getFields()) - 1:
                item = gtk.MenuItem("with next field")
                item.show()
                item.connect("activate", self.rightClickToConcatColumns, selectedField, "right")
                concatMenu.append(item)

                item = gtk.MenuItem("with all next fields")
                item.show()
                item.connect("activate", self.rightClickToConcatColumns, selectedField, "allright")
                concatMenu.append(item)

            # Personalize the fields to be concatenated
            item = gtk.MenuItem("personalize selection")
            item.show()
            item.connect("activate", self.ConcatChosenColumns)
            concatMenu.append(item)

            item = gtk.MenuItem("Concatenate field")
            item.set_submenu(concatMenu)
            item.show()
            menu.append(item)

            # Add entry to split the column
            item = gtk.MenuItem("Split field")
            item.show()
            item.connect("activate", self.rightClickToSplitColumn, selectedField)
            menu.append(item)

            # Add sub-entries to do partitioning of field cells
            subMenu = self.build_partitioning_submenu_for_field(selectedField)
            item = gtk.MenuItem("Partitioning")
            item.set_submenu(subMenu)
            item.show()
            menu.append(item)

            # Add entry to retrieve the field domain of definition
            item = gtk.MenuItem("Field's domain of definition")
            item.show()
            item.connect("activate", self.rightClickDomainOfDefinition, selectedField)
            menu.append(item)

            # Add sub-entries to change the variable of a specific column
            if selectedField.getVariable() == None:
                typeMenuVariable = gtk.Menu()
                itemVariable = gtk.MenuItem("Create a variable")
                itemVariable.show()
                itemVariable.connect("activate", self.rightClickCreateVariable, self.treeMessageGenerator.getSymbol(), selectedField)
                typeMenuVariable.append(itemVariable)
            else:
                typeMenuVariable = gtk.Menu()
                itemVariable = gtk.MenuItem("Edit variable")
                itemVariable.show()
                itemVariable.connect("activate", self.rightClickEditVariable, selectedField)
                typeMenuVariable.append(itemVariable)

            if selectedField.getVariable() != None:
                itemVariable3 = gtk.MenuItem("Remove variable")
                itemVariable3.show()
                itemVariable3.connect("activate", self.rightClickRemoveVariable, selectedField)
                typeMenuVariable.append(itemVariable3)

            item = gtk.MenuItem("Configure variation of field")
            item.set_submenu(typeMenuVariable)
            item.show()
            menu.append(item)

            item = gtk.SeparatorMenuItem()
            item.show()
            menu.append(item)

            # Add entries for copy functions
            copyMenu = gtk.Menu()
            item = gtk.MenuItem("Raw message")
            item.show()
            item.connect("activate", self.rightClickToCopyToClipboard, message_id, False, False, None)
            copyMenu.append(item)
            item = gtk.MenuItem("Aligned message")
            item.show()
            item.connect("activate", self.rightClickToCopyToClipboard, message_id, True, False, None)
            copyMenu.append(item)
            item = gtk.MenuItem("Aligned formatted message")
            item.show()
            item.connect("activate", self.rightClickToCopyToClipboard, message_id, True, True, None)
            copyMenu.append(item)
            item = gtk.MenuItem("Field")
            item.show()
            item.connect("activate", self.rightClickToCopyToClipboard, message_id, True, False, selectedField)
            copyMenu.append(item)
            item = gtk.MenuItem("Formatted field")
            item.show()
            item.connect("activate", self.rightClickToCopyToClipboard, message_id, True, True, selectedField)
            copyMenu.append(item)
            item = gtk.MenuItem("Copy to clipboard")
            item.set_submenu(copyMenu)
            item.show()
            menu.append(item)

            # Add entry to show properties of the message
            item = gtk.MenuItem("Message properties")
            item.show()
            item.connect("activate", self.rightClickShowPropertiesOfMessage, message_id)
            menu.append(item)

            # Add entry to delete the message
            item = gtk.MenuItem("Delete message")
            item.show()
            item.connect("activate", self.rightClickDeleteMessage)
            menu.append(item)

            menu.popup(None, None, None, event.button, event.time)

    #+----------------------------------------------
    #| build_partitioning_submenu_for_field:
    #|   Build a submenu for field cell partitioning.
    #+----------------------------------------------
    def build_moveto_submenu(self, symbol_src, listmessages):
        project = self.netzob.getCurrentProject()

        # Sanity checks
        if project == None:
            NetzobErrorMessage("No project selected.")
            return
        menu = gtk.Menu()

        for symbol in project.getVocabulary().getSymbols():
            item = gtk.MenuItem(symbol.getName())
            item.show()
            item.connect("activate", self.moveTo, symbol, symbol_src, listmessages)
            menu.append(item)

        return menu

    #+----------------------------------------------
    #| build_partitioning_submenu_for_field:
    #|   Build a submenu for field cell partitioning.
    #+----------------------------------------------
    def build_partitioning_submenu_for_field(self, field):
        menu = gtk.Menu()

        # Sequence alignment
        item = gtk.MenuItem("Sequence Alignment")
        item.show()
        item.connect("activate", self.fieldPartitioning, field, "alignment")
        menu.append(item)

        # Force partitioning
        # TODO
#        item = gtk.MenuItem("Force Partitioning")
#        item.show()
#        item.connect("activate", self.fieldPartitioning, field, "force")
#        menu.append(item)

        # Simple partitioning
        item = gtk.MenuItem("Simple Partitioning")
        item.show()
        item.connect("activate", self.fieldPartitioning, field, "simple")
        menu.append(item)

        return menu

    #+----------------------------------------------
    #| build_mathematicFilter_submenu:
    #|   Build a submenu for field/symbol mathematic filters
    #|   param field: the selected field
    #+----------------------------------------------
    def build_mathematicFilter_submenu(self, field):
        menu = gtk.Menu()

        # Build the list of available filters
        mathematicalFilters = []
        mathematicalFilters.append(Base64Filter("Base64 Filter"))
        mathematicalFilters.append(GZipFilter("GZip Filter"))
        mathematicalFilters.append(BZ2Filter("BZ2 Filter"))

        for mathFilter in mathematicalFilters:

            operation = "Add"
            for f in field.getMathematicFilters():
                if f.getName() == mathFilter.getName():
                    operation = "Remove"

            mathFilterItem = gtk.MenuItem(operation + " " + mathFilter.getName())
            mathFilterItem.connect("activate", self.applyMathematicalFilterOnField, mathFilter, field)
            mathFilterItem.show()
            menu.append(mathFilterItem)

        return menu

    def applyMathematicalFilterOnField(self, object, filter, field):
        appliedFilters = field.getMathematicFilters()
        found = False
        for appliedFilter in appliedFilters:
            if appliedFilter.getName() == filter.getName():
                found = True
        if found:
            #deactivate the selected filter
            field.removeMathematicFilter(filter)
        else:
            field.addMathematicFilter(filter)
        self.update()

    #+----------------------------------------------
    #| build_encoding_submenu:
    #|   Build a submenu for field/symbol data visualization.
    #|   param aObject: either a field or a symbol
    #+----------------------------------------------
    def build_encoding_submenu(self, aObject, message_id):
        menu = gtk.Menu()

        # Retrieve the selected message and field content
        message = self.selectedSymbol.getMessageByID(message_id)
        if message != None:
            # Retrieve content of the field
            field_content = message.getFields(False)[aObject.getIndex()]
        else:
            field_content = None

        # Format submenu
        possible_choices = Format.getSupportedFormats()
        subMenu = gtk.Menu()
        for value in possible_choices:
            if field_content != None:
                # Get preview of field content
                text_preview = TypeConvertor.encodeNetzobRawToGivenType(field_content, value)
                if len(text_preview) > 10:
                    text_preview = text_preview[:10] + "..."

                item = gtk.MenuItem(value + " (" + text_preview + ")")
            else:
                item = gtk.MenuItem(value)
            item.show()
            item.connect("activate", self.rightClickToChangeFormat, aObject, value)
            subMenu.append(item)
        item = gtk.MenuItem("Format")
        item.set_submenu(subMenu)
        item.show()
        menu.append(item)

        # Unitsize submenu
        possible_choices = [UnitSize.NONE, UnitSize.BIT, UnitSize.BITS8, UnitSize.BITS16, UnitSize.BITS32, UnitSize.BITS64]
        subMenu = gtk.Menu()
        for value in possible_choices:
            item = gtk.MenuItem(value)
            item.show()
            item.connect("activate", self.rightClickToChangeUnitSize, aObject, value)
            subMenu.append(item)
        item = gtk.MenuItem("UnitSize")
        item.set_submenu(subMenu)
        item.show()
        menu.append(item)

        # Sign submenu
        possible_choices = [Sign.SIGNED, Sign.UNSIGNED]
        subMenu = gtk.Menu()
        for value in possible_choices:
            item = gtk.MenuItem(value)
            item.show()
            item.connect("activate", self.rightClickToChangeSign, aObject, value)
            subMenu.append(item)
        item = gtk.MenuItem("Sign")
        item.set_submenu(subMenu)
        item.show()
        menu.append(item)

        # Endianess submenu
        possible_choices = [Endianess.BIG, Endianess.LITTLE]
        subMenu = gtk.Menu()
        for value in possible_choices:
            item = gtk.MenuItem(value)
            item.show()
            item.connect("activate", self.rightClickToChangeEndianess, aObject, value)
            subMenu.append(item)
        item = gtk.MenuItem("Endianess")
        item.set_submenu(subMenu)
        item.show()
        menu.append(item)
        return menu

    def displayPopupToEditField(self, event, field):
        dialog = gtk.MessageDialog(None,
                                   gtk.DIALOG_MODAL,
                                   gtk.MESSAGE_INFO,
                                   gtk.BUTTONS_CANCEL,
                                   "Modify field attributes")
        vbox = gtk.VBox()

        # Create hbox for field name
        hbox = gtk.HBox()
        vbox.pack_start(hbox, False, 5, 5)
        hbox.pack_start(NetzobLabel("Name : "), False, 5, 5)
        entryName = gtk.Entry()
        entryName.set_text(field.getName())
        # Allow the user to press enter to do ok
        entryName.connect("activate", self.responseToDialog, dialog, gtk.RESPONSE_OK)
        hbox.pack_end(entryName)

        # Create hbox for field description
        hbox = gtk.HBox()
        vbox.pack_start(hbox, False, 5, 5)
        hbox.pack_start(NetzobLabel("Description : "), False, 5, 5)
        entryDescr = gtk.Entry()
        if field.getDescription():
            entryDescr.set_text(field.getDescription())
        else:
            entryDescr.set_text("")
        # Allow the user to press enter to do ok
        entryDescr.connect("activate", self.responseToDialog, dialog, gtk.RESPONSE_OK)
        hbox.pack_end(entryDescr)

        # Create hbox for field regex
        hbox = gtk.HBox()
        vbox.pack_start(hbox, False, 5, 5)
        hbox.pack_start(NetzobLabel("Regex (be careful !) : "), False, 5, 5)
        entryRegex = gtk.Entry()
        entryRegex.set_text(field.getRegex())
        # Allow the user to press enter to do ok
        entryRegex.connect("activate", self.responseToDialog, dialog, gtk.RESPONSE_OK)
        hbox.pack_end(entryRegex)

        # Create hbox for field encapsulation level
        hbox = gtk.HBox()
        vbox.pack_start(hbox, False, 5, 5)
        hbox.pack_start(NetzobLabel("Encapsulation level : "), False, 5, 5)
        comboEncap = NetzobComboBoxEntry()
        for i in range(10):
            comboEncap.append_text(str(i))
            if i == field.getEncapsulationLevel():
                comboEncap.set_active(i)
        hbox.pack_end(comboEncap)

        # Run the dialog
        dialog.vbox.pack_end(vbox, True, True, 0)
        dialog.show_all()
        dialog.add_button(gtk.STOCK_OK, gtk.RESPONSE_OK)
        result = dialog.run()
        if result != gtk.RESPONSE_OK:
            dialog.destroy()
            return

        # Update field name
        text = entryName.get_text()
        if (len(text) > 0):
            field.setName(text)

        # Update field description
        text = entryDescr.get_text()
        if (len(text) > 0):
            field.setDescription(text)

        # Update field regex
        text = entryRegex.get_text()
        if (len(text) > 0):
            field.setRegex(text)
        dialog.destroy()
        self.update()

        # Update field encapsulation level
        try:
            encapLevel = int(comboEncap.get_active())
        except TypeError:
            pass
        else:
            if encapLevel >= 0:
                field.setEncapsulationLevel(encapLevel)
        self.update()

    #+----------------------------------------------
    #| button_press_on_treeview_typeStructure:
    #|   operation when the user click on the treeview.
    #|   mainly to open a contextual menu
    #+----------------------------------------------
    def button_press_on_treeview_typeStructure(self, treeview, event):
        # Popup a menu
        if event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
            self.log.debug("User requested a contextual menu (on treeview typeStructure)")
            x = int(event.x)
            y = int(event.y)
            (path, treeviewColumn, x, y) = treeview.get_path_at_pos(x, y)
            (iField,) = path

            selectedField = None
            for field in self.treeMessageGenerator.getSymbol().getFields():
                if field.getIndex() == iField:
                    selectedField = field
            if selectedField == None:
                self.log.warn("Impossible to retrieve the clicked field !")
                return

            menu = gtk.Menu()

            # Add entry to edit field
            item = gtk.MenuItem("Edit field")
            item.show()
            item.connect("activate", self.displayPopupToEditField, selectedField)
            menu.append(item)

            # Add sub-entries to change the type of a specific field
            subMenu = self.build_encoding_submenu(selectedField, None)
            item = gtk.MenuItem("Field visualization")
            item.set_submenu(subMenu)
            item.show()
            menu.append(item)

            # Add entries to concatenate fields
            concatMenu = gtk.Menu()
            item = gtk.MenuItem("with precedent field")
            item.show()
            item.connect("activate", self.rightClickToConcatColumns, selectedField, "left")
            concatMenu.append(item)
            item = gtk.MenuItem("with all precedent field")
            item.show()
            item.connect("activate", self.rightClickToConcatColumns, selectedField, "allleft")
            concatMenu.append(item)

            item = gtk.MenuItem("with next field")
            item.show()
            item.connect("activate", self.rightClickToConcatColumns, selectedField, "right")
            concatMenu.append(item)
            item = gtk.MenuItem("with all next field")
            item.show()
            item.connect("activate", self.rightClickToConcatColumns, selectedField, "allright")
            concatMenu.append(item)

            item = gtk.MenuItem("personalize selection")
            item.show()
            item.connect("activate", self.ConcatChosenColumns)
            concatMenu.append(item)

            item = gtk.MenuItem("Concatenate field")
            item.set_submenu(concatMenu)
            item.show()
            menu.append(item)

            # Add entry to split the field
            item = gtk.MenuItem("Split field")
            item.show()
            item.connect("activate", self.rightClickToSplitColumn, selectedField)
            menu.append(item)

            # Add entry to retrieve the field domain of definition
            item = gtk.MenuItem("Field's domain of definition")
            item.show()
            item.connect("activate", self.rightClickDomainOfDefinition, selectedField)
            menu.append(item)

            # Add sub-entries to change the variable of a specific column
            if selectedField.getVariable() == None:
                typeMenuVariable = gtk.Menu()
                itemVariable = gtk.MenuItem("Create a variable")
                itemVariable.show()
                itemVariable.connect("activate", self.rightClickCreateVariable, self.treeMessageGenerator.getSymbol(), selectedField)
                typeMenuVariable.append(itemVariable)
            else:
                typeMenuVariable = gtk.Menu()
                itemVariable = gtk.MenuItem("Edit variable")
                itemVariable.show()
                itemVariable.connect("activate", self.rightClickEditVariable, selectedField)
                typeMenuVariable.append(itemVariable)

            if selectedField.getVariable() != None:
                itemVariable3 = gtk.MenuItem("Remove variable")
                itemVariable3.show()
                itemVariable3.connect("activate", self.rightClickRemoveVariable, selectedField)
                typeMenuVariable.append(itemVariable3)

            item = gtk.MenuItem("Configure variation of field")
            item.set_submenu(typeMenuVariable)
            item.show()
            menu.append(item)

            # Add entry to export fields
            item = gtk.MenuItem("Export selected fields")
            item.show()
            item.connect("activate", self.exportSelectedFields_cb)
            menu.append(item)

            menu.popup(None, None, None, event.button, event.time)

    #+----------------------------------------------
    #| exportSelectedFields_cb:
    #|   Callback to export the selected fields
    #|   as a new trace
    #+----------------------------------------------
    def exportSelectedFields_cb(self, event):
        # Retrieve associated messages of selected fields
        aggregatedCells = {}
        (model, paths) = self.treeTypeStructureGenerator.getTreeview().get_selection().get_selected_rows()
        for path in paths:
            aIter = model.get_iter(path)
            if(model.iter_is_valid(aIter)):
                iField = model.get_value(aIter, 0)

                selectedField = None
                for field in self.treeMessageGenerator.getSymbol().getFields():
                    if field.getIndex() == iField:
                        selectedField = field
                if selectedField == None:
                    self.log.warn("Impossible to retrieve the clicked field !")
                    return

                cells = self.treeTypeStructureGenerator.getSymbol().getCellsByField(selectedField)
                for i in range(len(cells)):
                    if not i in aggregatedCells:
                        aggregatedCells[i] = ""
                    aggregatedCells[i] += str(cells[i])

        # Popup a menu to save the data
        dialog = gtk.Dialog(title="Save selected data", flags=0, buttons=None)
        dialog.show()
        table = gtk.Table(rows=2, columns=3, homogeneous=False)
        table.show()

        # Add to an existing trace
        label = NetzobLabel("Add to an existing trace")
        entry = gtk.combo_box_entry_new_text()
        entry.show()
        entry.set_size_request(300, -1)
        entry.set_model(gtk.ListStore(str))
        projectsDirectoryPath = self.netzob.getCurrentWorkspace().getPath() + os.sep + "projects" + os.sep + self.netzob.getCurrentProject().getPath()
        for tmpDir in os.listdir(projectsDirectoryPath):
            if tmpDir == '.svn':
                continue
            entry.append_text(tmpDir)
        but = NetzobButton("Save")
        but.connect("clicked", self.add_packets_to_existing_trace, entry, aggregatedCells, dialog)
        table.attach(label, 0, 1, 0, 1, xoptions=0, yoptions=0, xpadding=5, ypadding=5)
        table.attach(entry, 1, 2, 0, 1, xoptions=0, yoptions=0, xpadding=5, ypadding=5)
        table.attach(but, 2, 3, 0, 1, xoptions=0, yoptions=0, xpadding=5, ypadding=5)

        # Create a new trace
        label = NetzobLabel("Create a new trace")
        entry = gtk.Entry()
        entry.show()
        but = NetzobButton("Save")
        but.connect("clicked", self.create_new_trace, entry, aggregatedCells, dialog)
        table.attach(label, 0, 1, 1, 2, xoptions=0, yoptions=0, xpadding=5, ypadding=5)
        table.attach(entry, 1, 2, 1, 2, xoptions=0, yoptions=0, xpadding=5, ypadding=5)
        table.attach(but, 2, 3, 1, 2, xoptions=0, yoptions=0, xpadding=5, ypadding=5)

        dialog.action_area.pack_start(table, True, True, 0)

    #+----------------------------------------------
    #| Add a selection of packets to an existing trace
    #+----------------------------------------------
    def add_packets_to_existing_trace(self, button, entry, messages, dialog):
        logging.warn("Not yet implemented")
        return

        # projectsDirectoryPath = self.netzob.getCurrentWorkspace().getPath() + os.sep + "projects" + os.sep + self.netzob.getCurrentProject().getPath()
        # existingTraceDir = projectsDirectoryPath + os.sep + entry.get_active_text()
        # # Create the new XML structure
        # res = "<datas>\n"
        # for message in messages:
        #     res += "<data proto=\"ipc\" sourceIp=\"local\" sourcePort=\"local\" targetIp=\"local\" targetPort=\"local\" timestamp=\"" + str(time.time()) + "\">\n"
        #     res += message + "\n"
        #     res += "</data>\n"
        # res += "</datas>\n"
        # # Dump into a random XML file
        # fd = open(existingTraceDir + os.sep + str(random.randint(100000, 9000000)) + ".xml"  , "w")
        # fd.write(res)
        # fd.close()
        # dialog.destroy()

    #+----------------------------------------------
    #| Creation of a new trace from a selection of packets
    #+----------------------------------------------
    def create_new_trace(self, button, entry, messages, dialog):
        logging.warn("Not yet implemented")
        return

        # projectsDirectoryPath = self.netzob.getCurrentWorkspace().getPath() + os.sep + "projects" + os.sep + self.netzob.getCurrentProject().getPath()
        # for tmpDir in os.listdir(projectsDirectoryPath):
        #     if tmpDir == '.svn':
        #         continue
        #     if entry.get_text() == tmpDir:
        #         dialogBis = gtk.Dialog(title="This trace already exists", flags=0, buttons=None)
        #         dialogBis.set_size_request(250, 50)
        #         dialogBis.show()
        #         return

        # # Create the dest Dir
        # newTraceDir = projectsDirectoryPath + os.sep + entry.get_text()
        # os.mkdir(newTraceDir)
        # # Create the new XML structure
        # res = "<datas>\n"
        # for message in messages.values():
        #     res += "<data proto=\"ipc\" sourceIp=\"local\" sourcePort=\"local\" targetIp=\"local\" targetPort=\"local\" timestamp=\"" + str(time.time()) + "\">\n"
        #     res += message + "\n"
        #     res += "</data>\n"
        # res += "</datas>\n"
        # # Dump into a random XML file
        # fd = open(newTraceDir + os.sep + str(random.randint(100000, 9000000)) + ".xml"  , "w")
        # fd.write(res)
        # fd.close()
        # dialog.destroy()
        # self.netzob.updateListOfAvailableProjects()

    #+----------------------------------------------
    #| rightClickDomainOfDefinition:
    #|   Retrieve the domain of definition of the selected column
    #+----------------------------------------------
    def rightClickDomainOfDefinition(self, event, field):
        # Sanity checks
        project = self.netzob.getCurrentProject()
        if project == None:
            NetzobErrorMessage("No project selected.")
            return

        cells = self.treeMessageGenerator.getSymbol().getUniqValuesByField(field)
        tmpDomain = set()
        for cell in cells:
            tmpDomain.add(TypeConvertor.encodeNetzobRawToGivenType(cell, field.getFormat()))
        domain = sorted(tmpDomain)

        dialog = gtk.Dialog(title="Domain of definition for the column " + field.getName(), flags=0, buttons=None)

        # Text view containing domain of definition
        ## ListStore format:
        # str: symbol.id
        treeview = gtk.TreeView(gtk.ListStore(str))
        treeview.set_size_request(500, 300)
        treeview.show()

        cell = gtk.CellRendererText()
        cell.set_sensitive(True)
        cell.set_property('editable', True)

        column = gtk.TreeViewColumn("Column " + str(field.getIndex()))
        column.pack_start(cell, True)
        column.set_attributes(cell, text=0)

        treeview.append_column(column)

        for elt in domain:
            treeview.get_model().append([elt])

        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scroll.show()
        scroll.add(treeview)

        dialog.vbox.pack_start(scroll, True, True, 0)
        dialog.show()

    #+----------------------------------------------
    #| rightClickToCopyToClipboard:
    #|   Copy the message to the clipboard
    #+----------------------------------------------
    def rightClickToCopyToClipboard(self, event, id_message, aligned, encoded, field):
        self.log.debug("The user wants to copy the following message to the clipboard : " + str(id_message))

        # Retrieve the selected message
        message = self.selectedSymbol.getMessageByID(id_message)
        if message == None:
            self.log.warning("Impossible to retrieve the message based on its ID [{0}]".format(id_message))
            return

        if aligned == False:  # Copy the entire raw message
            self.netzob.clipboard.set_text(message.getStringData())
        elif field == None:  # Copy the entire aligned message
            self.netzob.clipboard.set_text(str(message.applyAlignment(styled=False, encoded=encoded)))
        else:  # Just copy the selected field
            self.netzob.clipboard.set_text(message.applyAlignment(styled=False, encoded=encoded)[field.getIndex()])

    #+----------------------------------------------
    #| rightClickShowPropertiesOfMessage:
    #|   Show a popup to present the properties of the selected message
    #+----------------------------------------------
    def rightClickShowPropertiesOfMessage(self, event, id_message):
        self.log.debug("The user wants to see the properties of message " + str(id_message))

        # Retrieve the selected message
        message = self.selectedSymbol.getMessageByID(id_message)
        if message == None:
            self.log.warning("Impossible to retrieve the message based on its ID [{0}]".format(id_message))
            return

        # Create the dialog
        dialog = gtk.Dialog(title="Properties of message " + str(message.getID()), flags=0, buttons=None)
        ## ListStore format : (str=key, str=type, str=value)
        treeview = gtk.TreeView(gtk.ListStore(str, str, str))
        treeview.set_size_request(500, 300)
        treeview.show()

        cell = gtk.CellRendererText()

        columnProperty = gtk.TreeViewColumn("Property")
        columnProperty.pack_start(cell, True)
        columnProperty.set_attributes(cell, text=0)

        columnType = gtk.TreeViewColumn("Type")
        columnType.pack_start(cell, True)
        columnType.set_attributes(cell, text=1)

        columnValue = gtk.TreeViewColumn("Value")
        columnValue.pack_start(cell, True)
        columnValue.set_attributes(cell, text=2)

        treeview.append_column(columnProperty)
        treeview.append_column(columnType)
        treeview.append_column(columnValue)

        # Retrieves all the properties of current message and
        # insert them in the treeview
        for property in message.getProperties():
            treeview.get_model().append(property)

        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scroll.show()
        scroll.add(treeview)

        dialog.vbox.pack_start(scroll, True, True, 0)
        dialog.show()

    #+----------------------------------------------
    #| rightClickDeleteMessage:
    #|   Delete the requested message
    #+----------------------------------------------
    def rightClickDeleteMessage(self, event):
        questionMsg = "Click yes to confirm the deletion of the selected messages"
        md = gtk.MessageDialog(None, gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_QUESTION, gtk.BUTTONS_YES_NO, questionMsg)
        result = md.run()
        md.destroy()
        if result != gtk.RESPONSE_YES:
            return

        # Else, retrieve the selected messages
        (model, paths) = self.treeMessageGenerator.getTreeview().get_selection().get_selected_rows()
        for path in paths:
            aIter = model.get_iter(path)
            if(model.iter_is_valid(aIter)):
                id_message = model.get_value(aIter, 0)
                self.log.debug("The user wants to delete the message " + str(id_message))

                message_symbol = self.selectedSymbol
                message = self.selectedSymbol.getMessageByID(id_message)

                # Break if the message to move was not found
                if message == None:
                    self.log.warning("Impossible to retrieve the message to remove based on its ID [{0}]".format(id_message))
                    return
                message_symbol.removeMessage(message)
                self.netzob.getCurrentProject().getVocabulary().removeMessage(message)
        self.update()

    #+----------------------------------------------
    #| rightClickToChangeFormat:
    #|   Callback to change the field/symbol format
    #|   by doing a right click on it.
    #+----------------------------------------------
    def rightClickToChangeFormat(self, event, aObject, aFormat):
        aObject.setFormat(aFormat)
        self.update()

    #+----------------------------------------------
    #| rightClickToChangeUnitSize:
    #|   Callback to change the field/symbol unitsize
    #|   by doing a right click on it.
    #+----------------------------------------------
    def rightClickToChangeUnitSize(self, event, aObject, unitSize):
        aObject.setUnitSize(unitSize)
        self.update()

    #+----------------------------------------------
    #| rightClickToChangeSign:
    #|   Callback to change the field/symbol sign
    #|   by doing a right click on it.
    #+----------------------------------------------
    def rightClickToChangeSign(self, event, aObject, sign):
        aObject.setSign(sign)
        self.update()

    #+----------------------------------------------
    #| rightClickToChangeEndianess:
    #|   Callback to change the field/symbol endianess
    #|   by doing a right click on it.
    #+----------------------------------------------
    def rightClickToChangeEndianess(self, event, aObject, endianess):
        aObject.setEndianess(endianess)
        self.update()

    #+----------------------------------------------
    #| concatenateChosenFields:
    #|   Ask the user which field to concatenate
    #+----------------------------------------------
    def ConcatChosenColumns(self, event=None, errormessage=""):
        nrows = 2
        if(errormessage):
            nrows = 3
        dialog = gtk.Dialog(title="Concatenation of Fields", flags=0, buttons=None)
        panel = gtk.Table(rows=nrows, columns=4, homogeneous=False)
        panel.show()

        ## Label for indexes of the fields
        label = NetzobLabel("Fields from:")
        index1 = gtk.Entry(4)
        index1.show()
        label2 = NetzobLabel("to:")
        index2 = gtk.Entry(4)
        index2.show()
        if(errormessage):
            label3 = NetzobLabel(errormessage)

        panel.attach(label, 0, 1, 0, 1, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        panel.attach(index1, 1, 2, 0, 1, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        panel.attach(label2, 2, 3, 0, 1, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        panel.attach(index2, 3, 4, 0, 1, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        if(errormessage):
            panel.attach(label3, 2, 4, 2, 7, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        # Button
        searchButton = NetzobButton("Concatenate fields")
        searchButton.connect("clicked", self.clickToConcatChosenColumns, index1, index2, dialog)
        panel.attach(searchButton, 0, 2, 1, 2, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        dialog.vbox.pack_start(panel, True, True, 0)
        dialog.show()

    #+--------------------------------------------
    #|  clickToConcatChosenColumns:
    #|	try to concatenate wanted fields.
    #+-------------------------------------------
    def clickToConcatChosenColumns(self, event, index1, index2, dialog):
        try:
            nfirst = int(index1.get_text())
            nlast = int(index2.get_text())
            self.log.debug("Concatenate from " + str(nfirst) + " to the column " + str(nlast))
            if max(nlast, nfirst) >= len(self.selectedSymbol.fields):
                dialog.destroy()
                self.ConcatChosenColumns(errormessage="Error: " + str(max(nlast, nfirst)) + " > Last field index")
                return 1
            if(nlast > nfirst):
                for i_concatleft in range(nlast - nfirst):
                    if not self.selectedSymbol.concatFields(nfirst):
                        break
                    else:
                        for i_concatleft in range(nfirst - nlast):
                            if not self.selectedSymbol.concatFields(nlast):
                                break
                self.treeMessageGenerator.updateDefault()
                self.update()
                dialog.destroy()
        except:
            dialog.destroy()
            self.ConcatChosenColumns(errormessage="Error: You must put integers in forms")

    #+----------------------------------------------
    #|  rightClickToConcatColumns:
    #|   Callback to concatenate two columns
    #+----------------------------------------------
    def rightClickToConcatColumns(self, event, field, strOtherCol):
        self.log.debug("Concatenate the column " + str(field.getIndex()) + " with the " + str(strOtherCol) + " column")

        if field.getIndex() == 0 and (strOtherCol == "left" or strOtherCol == "allleft"):
            self.log.debug("Can't concatenate the first column with its left column")
            return

        if field.getIndex() + 1 == len(self.selectedSymbol.getFields()) and (strOtherCol == "right" or strOtherCol == "allright"):
            self.log.debug("Can't concatenate the last column with its right column")
            return

        if strOtherCol == "left":
            self.selectedSymbol.concatFields(field.getIndex() - 1)
        elif strOtherCol == "allleft":
            for i_concatleft in range(field.getIndex()):
                self.selectedSymbol.concatFields(0)
        elif strOtherCol == "allright":
            cont = self.selectedSymbol.concatFields(field.getIndex())
            while(cont):
                cont = self.selectedSymbol.concatFields(field.getIndex())
        else:
            self.selectedSymbol.concatFields(field.getIndex())
        self.treeMessageGenerator.updateDefault()
        self.update()

    #+----------------------------------------------
    #|  rightClickToSplitColumn:
    #|   Callback to split a column
    #+----------------------------------------------
    def rightClickToSplitColumn(self, event, field):
        dialog = gtk.Dialog(title="Split column " + str(field.getIndex()), flags=0, buttons=None)
        textview = gtk.TextView()
        textview.set_editable(False)
        textview.get_buffer().create_tag("redTag", weight=pango.WEIGHT_BOLD, foreground="red", family="Courier")
        textview.get_buffer().create_tag("greenTag", weight=pango.WEIGHT_BOLD, foreground="#006400", family="Courier")
        self.split_position = 1
        self.split_max_len = 0

        # Find the size of the longest message
        cells = self.selectedSymbol.getCellsByField(field)
        for m in cells:
            if len(m) > self.split_max_len:
                self.split_max_len = len(m)

        # Padding orientation
        self.split_align = "left"
        but = NetzobButton("Align to right")
        but.connect("clicked", self.doAlignSplit, textview, field, but)
        dialog.action_area.pack_start(but, True, True, 0)

        # Left arrow
        arrow = gtk.Arrow(gtk.ARROW_LEFT, gtk.SHADOW_OUT)
        arrow.show()
        but = gtk.Button()
        but.show()
        but.add(arrow)
        but.connect("clicked", self.adjustSplitColumn, textview, "left", field)
        dialog.action_area.pack_start(but, True, True, 0)

        # Right arrow
        arrow = gtk.Arrow(gtk.ARROW_RIGHT, gtk.SHADOW_OUT)
        arrow.show()
        but = gtk.Button()
        but.show()
        but.add(arrow)
        but.connect("clicked", self.adjustSplitColumn, textview, "right", field)
        dialog.action_area.pack_start(but, True, True, 0)

        # Split button
        but = NetzobButton("Split column")
        but.connect("clicked", self.doSplitColumn, textview, field, dialog)
        dialog.action_area.pack_start(but, True, True, 0)

        # Text view containing selected column messages
        frame = NetzobFrame("Content of the column to split")
        textview.set_size_request(600, 300)
#        cells = self.treeMessageGenerator.getSymbol().getCellsByCol(iCol)

        for m in cells:
            textview.get_buffer().insert_with_tags_by_name(textview.get_buffer().get_end_iter(), TypeConvertor.encodeNetzobRawToGivenType(m[:self.split_position], field.getFormat()) + "  ", "redTag")
            textview.get_buffer().insert_with_tags_by_name(textview.get_buffer().get_end_iter(), TypeConvertor.encodeNetzobRawToGivenType(m[self.split_position:], field.getFormat()) + "\n", "greenTag")
        textview.show()
        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scroll.show()
        scroll.add(textview)
        frame.add(scroll)
        dialog.vbox.pack_start(frame, True, True, 0)
        dialog.show()

    def rightClickCreateVariable(self, widget, symbol, field):
        self.log.debug("Opening the dialog for the creation of a variable")
        dialog = gtk.MessageDialog(None, gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_QUESTION, gtk.BUTTONS_OK, None)
        dialog.set_markup('Definition of the new variable')

        # Create the ID of the new variable
        variableID = uuid.uuid4()

        mainTable = gtk.Table(rows=3, columns=2, homogeneous=False)
        # id of the variable
        variableIDLabel = NetzobLabel("ID :")
        variableIDValueLabel = NetzobLabel(str(variableID))
        variableIDValueLabel.set_sensitive(False)
        mainTable.attach(variableIDLabel, 0, 1, 0, 1, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        mainTable.attach(variableIDValueLabel, 1, 2, 0, 1, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        # name of the variable
        variableNameLabel = NetzobLabel("Name : ")
        variableNameEntry = gtk.Entry()
        variableNameEntry.show()
        mainTable.attach(variableNameLabel, 0, 1, 1, 2, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        mainTable.attach(variableNameEntry, 1, 2, 1, 2, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        # Include current binary values
        variableWithCurrentBinariesLabel = NetzobLabel("Add current binaries : ")

        variableWithCurrentBinariesButton = gtk.CheckButton("Disjunctive inclusion")
        variableWithCurrentBinariesButton.set_active(False)
        variableWithCurrentBinariesButton.show()

        mainTable.attach(variableWithCurrentBinariesLabel, 0, 1, 2, 3, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        mainTable.attach(variableWithCurrentBinariesButton, 1, 2, 2, 3, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        dialog.vbox.pack_end(mainTable, True, True, 0)
        dialog.show_all()
        result = dialog.run()

        if result != gtk.RESPONSE_OK:
            dialog.destroy()
            return

        # We retrieve the value of the variable
        varName = variableNameEntry.get_text()

        # Disjonctive inclusion ?
        disjunctive = variableWithCurrentBinariesButton.get_active()

        if disjunctive:
            # Create a default value
            defaultValue = field.getDefaultVariable(symbol)
        else:
            defaultValue = None

        # We close the current dialog
        dialog.destroy()

        # Dedicated view for the creation of a variable
        creationPanel = VariableView(self.netzob, field, variableID, varName, defaultValue)
        creationPanel.display()

    def rightClickRemoveVariable(self, widget, field):
        questionMsg = "Click yes to confirm the removal of the variable {0}".format(field.getVariable().getID())
        md = gtk.MessageDialog(None, gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_QUESTION, gtk.BUTTONS_YES_NO, questionMsg)
        result = md.run()
        md.destroy()
        if result == gtk.RESPONSE_YES:
            field.setVariable(None)
            self.update()
        else:
            self.log.debug("The user didn't confirm the deletion of the variable " + str(field.getVariable().getID()))

    def rightClickEditVariable(self, widget, field):
        logging.error("The edition of an existing variable is not yet implemented")

    def doSplitColumn(self, widget, textview, field, dialog):
        if self.split_max_len <= 1:
            dialog.destroy()
            return

        if self.split_align == "right":
            split_index = -self.split_position
        else:
            split_index = self.split_position
        self.selectedSymbol.splitField(field, split_index, self.split_align)
        self.treeMessageGenerator.updateDefault()
        dialog.destroy()
        self.update()

    def adjustSplitColumn(self, widget, textview, direction, field):
        if self.split_max_len <= 1:
            return
        messages = self.selectedSymbol.getCellsByField(field)

        # Bounds checking
        if self.split_align == "left":
            if direction == "left":
                self.split_position -= 1
                if self.split_position < 1:
                    self.split_position = 1
            else:
                self.split_position += 1
                if self.split_position > self.split_max_len - 1:
                    self.split_position = self.split_max_len - 1
        else:
            if direction == "left":
                self.split_position += 1
                if self.split_position > self.split_max_len - 1:
                    self.split_position = self.split_max_len - 1
            else:
                self.split_position -= 1
                if self.split_position < 1:
                    self.split_position = 1

        # Colorize text according to position
        textview.get_buffer().set_text("")
        for m in messages:
            # Crate padding in case of right alignment
            if self.split_align == "right":
                padding = ""
                messageLen = len(m)
                for i in range(self.split_max_len - messageLen):
                    padding += " "
                textview.get_buffer().insert_with_tags_by_name(textview.get_buffer().get_end_iter(), padding, "greenTag")
                split_index = -self.split_position
            else:
                split_index = self.split_position
            textview.get_buffer().insert_with_tags_by_name(textview.get_buffer().get_end_iter(), TypeConvertor.encodeNetzobRawToGivenType(m[:split_index], field.getFormat()) + "  ", "redTag")
            textview.get_buffer().insert_with_tags_by_name(textview.get_buffer().get_end_iter(), TypeConvertor.encodeNetzobRawToGivenType(m[split_index:], field.getFormat()) + "\n", "greenTag")

    def doAlignSplit(self, widget, textview, field, button_align):
        if self.split_align == "left":
            self.split_align = "right"
            button_align.set_label("Align to left")
        else:
            self.split_align = "left"
            button_align.set_label("Align to right")

        messages = self.selectedSymbol.getCellsByField(field)

        # Adapt alignment
        textview.get_buffer().set_text("")
        for m in messages:
            # Crate padding in case of right alignment
            if self.split_align == "right":
                padding = ""
                messageLen = len(m)
                for i in range(self.split_max_len - messageLen):
                    padding += " "
                textview.get_buffer().insert_with_tags_by_name(textview.get_buffer().get_end_iter(), padding, "greenTag")
                split_index = -self.split_position
            else:
                split_index = self.split_position
            textview.get_buffer().insert_with_tags_by_name(textview.get_buffer().get_end_iter(), TypeConvertor.encodeNetzobRawToGivenType(m[:split_index], field.getFormat()) + "  ", "redTag")
            textview.get_buffer().insert_with_tags_by_name(textview.get_buffer().get_end_iter(), TypeConvertor.encodeNetzobRawToGivenType(m[split_index:], field.getFormat()) + "\n", "greenTag")

    #+----------------------------------------------
    #| dbClickToChangeFormat:
    #|   Called when user double click on a row
    #|    in order to change the field format
    #+----------------------------------------------
    def dbClickToChangeFormat(self, treeview, path, treeviewColumn):
        # Retrieve the selected column number
        iField = 0
        for col in treeview.get_columns():
            if col == treeviewColumn:
                break
            iField += 1

        selectedField = None
        for field in self.treeMessageGenerator.getSymbol().getFields():
            if field.getIndex() == iField:
                selectedField = field

        if selectedField == None:
            self.log.warn("Impossible to retrieve the clicked field !")
            return

        possible_choices = Format.getSupportedFormats()
#        possibleTypes = self.treeMessageGenerator.getSymbol().getPossibleTypesForAField(selectedField)
        i = 0
        chosedFormat = selectedField.getFormat()
        for aFormat in possible_choices:
            if aFormat == chosedFormat:
                chosedFormat = possible_choices[(i + 1) % len(possible_choices)]
                break
            i += 1

        # Apply the new choosen format for this field
        selectedField.setFormat(chosedFormat)
        self.treeMessageGenerator.updateDefault()
        self.treeTypeStructureGenerator.update()

    #+----------------------------------------------
    #| button_press_on_search_results:
    #|   operation when the user click on the treeview of the search results.
    #+----------------------------------------------
    def button_press_on_search_results(self, treeview, event):
        elementType = None
        elementValue = None

        target = treeview.get_path_at_pos(int(event.x), int(event.y))
        # Retrieve informations on the clicked element
        if event.type == gtk.gdk.BUTTON_PRESS and event.button == 1:
            x = int(event.x)
            y = int(event.y)
            try:
                (path, treeviewColumn, x, y) = treeview.get_path_at_pos(x, y)
            except:
                # No element selected
                pass
            else:
                # An element is selected
                aIter = treeview.get_model().get_iter(path)
                if aIter:
                    if treeview.get_model().iter_is_valid(aIter):
                        elementType = treeview.get_model().get_value(aIter, 0)
                        elementID = treeview.get_model().get_value(aIter, 1)
                        elementValue = treeview.get_model().get_value(aIter, 2)

        # Depending of its type, we select it
        if elementType != None and elementValue != None:
            if elementType == "Symbol":
                clickedSymbol = self.netzob.getCurrentProject().getVocabulary().getSymbolByID(elementID)
                self.selectedSymbol = clickedSymbol
                self.updateTreeStoreSymbol()
                self.updateTreeStoreMessage()
            elif elementType == "Message":
                clickedMessage = self.netzob.getCurrentProject().getVocabulary().getMessageByID(elementID)
                clickedSymbol = self.netzob.getCurrentProject().getVocabulary().getSymbolWhichContainsMessage(clickedMessage)
                self.selectedSymbol = clickedSymbol
                self.selectedMessage = clickedMessage
                self.updateTreeStoreMessage()

    #+----------------------------------------------
    #| build_context_menu_for_symbols:
    #|   Create a menu to display available operations
    #|   on the treeview symbols
    #+----------------------------------------------
    def build_context_menu_for_symbols(self, event, symbol):
        # Build the contextual menu
        menu = gtk.Menu()

        if (symbol != None):
            # Edit the Symbol
            itemEditSymbol = gtk.MenuItem("Edit symbol")
            itemEditSymbol.show()
            itemEditSymbol.connect("activate", self.displayPopupToEditSymbol, symbol)
            menu.append(itemEditSymbol)

            # Search in the Symbol
            itemSearchSymbol = gtk.MenuItem("Search in")
            itemSearchSymbol.show()
            itemSearchSymbol.connect("activate", self.displayPopupToSearch, "Symbol", symbol)
            menu.append(itemSearchSymbol)

            # SubMenu : Alignments
            subMenuAlignment = gtk.Menu()

            # Sequence alignment
            itemSequenceAlignment = gtk.MenuItem("Sequence Alignment")
            itemSequenceAlignment.show()
            itemSequenceAlignment.connect("activate", self.sequenceAlignmentOnSpecifiedSymbols, [symbol])
            subMenuAlignment.append(itemSequenceAlignment)

            # Force partitioning
            itemForcePartitioning = gtk.MenuItem("Force Partitioning")
            itemForcePartitioning.show()
            itemForcePartitioning.connect("activate", self.forcePartitioningOnSpecifiedSymbols, [symbol])
            subMenuAlignment.append(itemForcePartitioning)

            # Simple partitioning
            itemSimplePartitioning = gtk.MenuItem("Simple Partitioning")
            itemSimplePartitioning.show()
            itemSimplePartitioning.connect("activate", self.simplePartitioningOnSpecifiedSymbols, [symbol])
            subMenuAlignment.append(itemSimplePartitioning)

            # Smooth partitioning
            itemSmoothPartitioning = gtk.MenuItem("Smooth Partitioning")
            itemSmoothPartitioning.show()
            itemSmoothPartitioning.connect("activate", self.smoothPartitioningOnSpecifiedSymbols, [symbol])
            subMenuAlignment.append(itemSmoothPartitioning)

            # Reset partitioning
            itemResetPartitioning = gtk.MenuItem("Reset Partitioning")
            itemResetPartitioning.show()
            itemResetPartitioning.connect("activate", self.resetPartitioningOnSpecifiedSymbols, [symbol])
            subMenuAlignment.append(itemResetPartitioning)

            itemMenuAlignment = gtk.MenuItem("Align the symbol")
            itemMenuAlignment.show()
            itemMenuAlignment.set_submenu(subMenuAlignment)

            menu.append(itemMenuAlignment)

            # Add sub-entries to change the type of a specific column
            subMenu = self.build_encoding_submenu(symbol, None)
            item = gtk.MenuItem("Field visualization")
            item.set_submenu(subMenu)
            item.show()
            menu.append(item)

            # Remove a Symbol
            itemRemoveSymbol = gtk.MenuItem("Remove symbol")
            itemRemoveSymbol.show()
            itemRemoveSymbol.connect("activate", self.displayPopupToRemoveSymbol, symbol)
            menu.append(itemRemoveSymbol)
        else:
            # Create a Symbol
            itemCreateSymbol = gtk.MenuItem("Create a symbol")
            itemCreateSymbol.show()
            itemCreateSymbol.connect("activate", self.displayPopupToCreateSymbol, symbol)
            menu.append(itemCreateSymbol)

        menu.popup(None, None, None, event.button, event.time)

    def displayPopupToSearch(self, event, typeSearch, searchTarget):
        dialog = gtk.MessageDialog(None,
                                   gtk.DIALOG_MODAL,
                                   gtk.MESSAGE_OTHER,
                                   gtk.BUTTONS_OK,
                                   "Searching")
        # Create the main panel
        panel = gtk.Table(rows=3, columns=2, homogeneous=False)
        panel.show()

        # Create the header (first row) with the search form
        # Search entry
        searchEntry = gtk.Entry()
        searchEntry.show()

        # Combo to select the type of the input
        typeCombo = gtk.combo_box_entry_new_text()
        typeCombo.show()
        typeStore = gtk.ListStore(str)
        typeCombo.set_model(typeStore)
        typeCombo.get_model().append([Format.STRING])
        typeCombo.get_model().append([Format.HEX])
        typeCombo.get_model().append([Format.BINARY])
        typeCombo.get_model().append([Format.OCTAL])
        typeCombo.get_model().append([Format.DECIMAL])
        typeCombo.get_model().append([Format.IP])
        typeCombo.set_active(0)

        panel.attach(searchEntry, 0, 1, 0, 1, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        panel.attach(typeCombo, 1, 2, 0, 1, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        dialog.vbox.pack_end(panel, True, True, 0)

        dialog.run()
        searchedPattern = searchEntry.get_text()
        typeOfPattern = typeCombo.get_active_text()
        self.prepareSearchInSymbol(searchedPattern, typeOfPattern, searchTarget)

        dialog.destroy()

    def displayPopupToEditSymbol(self, event, symbol):
        dialog = gtk.MessageDialog(
        None,
        gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
        gtk.MESSAGE_QUESTION,
        gtk.BUTTONS_OK,
        None)
        dialog.set_markup("<b>Please enter the name of the symbol :</b>")
        #create the text input field
        entry = gtk.Entry()
        entry.set_text(symbol.getName())
        #allow the user to press enter to do ok
        entry.connect("activate", self.responseToDialog, dialog, gtk.RESPONSE_OK)
        #create a horizontal box to pack the entry and a label
        hbox = gtk.HBox()
        hbox.pack_start(NetzobLabel("Name : "), False, 5, 5)
        hbox.pack_end(entry)
        dialog.vbox.pack_end(hbox, True, True, 0)
        dialog.show_all()
        #go go go
        dialog.run()
        text = entry.get_text()
        if (len(text) > 0):
            self.selectedSymbol.setName(text)
        dialog.destroy()
        self.update()

    #+----------------------------------------------
    #| responseToDialog:
    #|   pygtk is so good ! arf :(<-- clap clap :D
    #+----------------------------------------------
    def responseToDialog(self, entry, dialog, response):
        dialog.response(response)

    #+----------------------------------------------
    #| displayPopupToCreateSymbol:
    #|   Display a form to create a new symbol.
    #|   Based on the famous dialogs
    #+----------------------------------------------
    def displayPopupToCreateSymbol(self, event, symbol):

        #base this on a message dialog
        dialog = gtk.MessageDialog(
                                   None,
                                   gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                   gtk.MESSAGE_QUESTION,
                                   gtk.BUTTONS_OK,
                                   None)
        dialog.set_markup("<b>Please enter symbol's name</b> :")
        #create the text input field
        entry = gtk.Entry()
        #allow the user to press enter to do ok
        entry.connect("activate", self.responseToDialog, dialog, gtk.RESPONSE_OK)
        #create a horizontal box to pack the entry and a label
        hbox = gtk.HBox()
        hbox.pack_start(NetzobLabel("Name :"), False, 5, 5)
        hbox.pack_end(entry)
        #add it and show it
        dialog.vbox.pack_end(hbox, True, True, 0)
        dialog.show_all()
        #go go go
        dialog.run()
        newSymbolName = entry.get_text()
        dialog.destroy()

        if (len(newSymbolName) > 0):
            newSymbolId = str(uuid.uuid4())
            self.log.debug("a new symbol will be created with the given name : {0}".format(newSymbolName))
            newSymbol = Symbol(newSymbolId, newSymbolName, self.netzob.getCurrentProject())

            self.netzob.getCurrentProject().getVocabulary().addSymbol(newSymbol)

            #Update Left and Right
            self.update()

    #+----------------------------------------------
    #| displayPopupToRemoveSymbol:
    #|   Display a popup to remove a symbol
    #|   the removal of a symbol can only occurs
    #|   if its an empty symbol
    #+----------------------------------------------
    def displayPopupToRemoveSymbol(self, event, symbol):

        self.log.debug("Can remove the symbol {0} since it's an empty one.".format(symbol.getName()))
        questionMsg = "Click yes to confirm the removal of the symbol {0}".format(symbol.getName())
        md = gtk.MessageDialog(None, gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_QUESTION, gtk.BUTTONS_YES_NO, questionMsg)
        result = md.run()
        md.destroy()
        if result == gtk.RESPONSE_YES:
            while(symbol.getMessages()):
                message = symbol.getMessages()[0]
                symbol.removeMessage(message)
                self.netzob.getCurrentProject().getVocabulary().removeMessage(message)
            self.netzob.getCurrentProject().getVocabulary().removeSymbol(symbol)
            #Update Left and Right
            self.update()
        else:
            self.log.debug("The user didn't confirm the deletion of the symbol " + symbol.getName())

    #+----------------------------------------------
    #| drop_fromDND:
    #|   defines the operation executed when a message is
    #|   is dropped out current symbol to the selected symbol
    #+----------------------------------------------
    def drop_fromDND(self, treeview, context, x, y, selection, info, etime):
        ids = selection.data

        modele = treeview.get_model()
        info_depot = treeview.get_dest_row_at_pos(x, y)

        for msg_id in ids.split(";"):

            # First we search for the message to move
            message = None
            message_symbol = self.selectedSymbol
            for msg in message_symbol.getMessages():
                if str(msg.getID()) == msg_id:
                    message = msg

            # Break if the message to move was not found
            if message == None:
                self.log.warning("Impossible to retrieve the message to move based on its ID [{0}]".format(msg_id))
                return

            self.log.debug("The message having the ID [{0}] has been found !".format(msg_id))

            # Now we search for the new symbol of the message
            if info_depot:
                # TODO : check need to position variable
                chemin, position = info_depot
                iter = modele.get_iter(chemin)
                new_symbol_id = str(modele.get_value(iter, 0))

                new_message_symbol = self.netzob.getCurrentProject().getVocabulary().getSymbol(new_symbol_id)

            if new_message_symbol == None:
                self.log.warning("Impossible to retrieve the symbol in which the selected message must be moved out.")
                return

            self.log.debug("The new symbol of the message is {0}".format(str(new_message_symbol.getID())))
            # Removing from its old symbol
            message_symbol.removeMessage(message)

            # Adding to its new symbol
            new_message_symbol.addMessage(message)

            # Retrieve default parameters of alignment
            doInternalSlick = False
            defaultFormat = Format.HEX
            global_unitsize = self.netzob.getCurrentProject().getConfiguration().getVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_GLOBAL_UNITSIZE)
            unitSize = UnitSize.getSizeInBits(global_unitsize)
            if unitSize == None:
                unitSize = 8

            alignmentProcess = NeedlemanAndWunsch(unitSize, self.loggingNeedlemanStatus)
            alignmentProcess.alignSymbol(new_message_symbol, doInternalSlick, defaultFormat)
            alignmentProcess.alignSymbol(message_symbol, doInternalSlick, defaultFormat)

#            message_symbol.buildRegexAndAlignment(self.netzob.getCurrentProject().getConfiguration())
#            new_message_symbol.buildRegexAndAlignment(self.netzob.getCurrentProject().getConfiguration())

        #Update Left and Right
        self.update()
        return

    #+--------------------------------------------------------
    #| moveTo:
    #|   Move selected messages from symbol_src to symbol_dst
    #+--------------------------------------------------------
    def moveTo(self, widget, symbol_dst, symbol_src, listmessages):

        self.log.debug("Move messages from {0} to {1} : {2}".format(symbol_src.getName(), symbol_dst.getName(), ",".join(listmessages)))

        if not listmessages:
            return

        for id_message in listmessages:
            message = symbol_src.getMessageByID(id_message)
            symbol_src.removeMessage(message)
            symbol_dst.addMessage(message)

        #TODO do a needleman ?
        # Retrieve default parameters of alignment
        #doInternalSlick = False
        #defaultFormat = Format.HEX
        #global_unitsize = self.netzob.getCurrentProject().getConfiguration().getVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_GLOBAL_UNITSIZE)
        #unitSize = UnitSize.getSizeInBits(global_unitsize)
        #if unitSize == None:
        #    unitSize = 8

        #alignmentProcess = NeedlemanAndWunsch(unitSize, self.loggingNeedlemanStatus)
        #alignmentProcess.alignSymbol(symbol_src, doInternalSlick, defaultFormat)
        #alignmentProcess.alignSymbol(symbol_dst, doInternalSlick, defaultFormat)

        self.update()

    #+----------------------------------------------
    #| fieldPartitioning:
    #|   Make a partitioning at the field level
    #+----------------------------------------------
    def fieldPartitioning(self, widget, field, partitioningType):
        # Create a temporary symbol to store cells
        id = str(uuid.uuid4())
        tmpSymbol = Symbol(id, "", self.netzob.getCurrentProject())
        for cell in self.selectedSymbol.getCellsByField(field):
            idMsg = str(uuid.uuid4())
            msg = RawMessage(idMsg, 0, cell)
            tmpSymbol.addMessage(msg)

        # Retrieve default parameters of alignment
        doInternalSlick = False
        defaultFormat = Format.HEX
        global_unitsize = self.netzob.getCurrentProject().getConfiguration().getVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_GLOBAL_UNITSIZE)
        unitSize = UnitSize.getSizeInBits(global_unitsize)
        if unitSize == None:
            unitSize = 4

        # Process the partitioning
        if partitioningType == "alignment":
            alignmentProcess = NeedlemanAndWunsch(unitSize, self.loggingNeedlemanStatus)
            alignmentProcess.alignSymbol(tmpSymbol, doInternalSlick, defaultFormat)
        elif partitioningType == "force":
            logging.warn("Not yet implemented")
            return
        elif partitioningType == "simple":
            tmpSymbol.simplePartitioning(self.netzob.getCurrentProject().getConfiguration(), unitSize)
        else:
            return

        # Adapt the computated field partitionment to the original symbol
        index = field.getIndex()
        self.selectedSymbol.popField(index)

        i = 0
        for tmpField in tmpSymbol.getFields():
            currentIndex = index + i
            i += 1
            self.selectedSymbol.addField(tmpField, currentIndex)
            tmpField.setName(tmpField.getName() + "-" + str(i))

        # Adapt next fields indexes
        for nextField in self.selectedSymbol.fields:
            if nextField.getIndex() > index:
                nextField.setIndex(index + len(tmpSymbol.getFields()))
        self.update()

    def loggingNeedlemanStatus(self, status, message):
        self.log.debug("Status = " + str(status) + " : " + str(message))

    #+----------------------------------------------
    #| drag_fromDND:
    #|   defines the operation executed when a message is
    #|   is dragged out current symbol
    #+----------------------------------------------
    def drag_fromDND(self, treeview, contexte, selection, info, dateur):
        ids = []
        treeview.get_selection().selected_foreach(self.foreach_drag_fromDND, ids)
        selection.set(selection.target, 8, ";".join(ids))

    def foreach_drag_fromDND(self, model, path, iter, ids):
        texte = str(model.get_value(iter, 0))
        ids.append(texte)
        return

    #+----------------------------------------------
    #| Update the content of the tree store for symbols
    #+----------------------------------------------
    def updateTreeStoreSymbol(self):
        # Updates the treestore with a selected message
        if (self.selectedMessage != None):
            self.treeSymbolGenerator.default(self.selectedSymbol)
            self.selectedMessage = None
        else:
            # Default display of the symbols
            self.treeSymbolGenerator.default(self.selectedSymbol)

    #+----------------------------------------------
    #| Update the content of the tree store for messages
    #+----------------------------------------------
    def updateTreeStoreMessage(self):
        if self.netzob.getCurrentProject() != None:
            isActive = self.netzob.getCurrentProject().getConfiguration().getVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_DISPLAY_MESSAGES)
            if isActive:
                self.treeMessageGenerator.show()
                self.treeMessageGenerator.default(self.selectedSymbol, self.selectedMessage)
            else:
                self.treeMessageGenerator.hide()

    #+----------------------------------------------
    #| Update the content of the tree store for type structure
    #+----------------------------------------------
    def updateTreeStoreTypeStructure(self):
        if self.netzob.getCurrentProject() != None:
            isActive = self.netzob.getCurrentProject().getConfiguration().getVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_DISPLAY_SYMBOL_STRUCTURE)
            if isActive:
                self.treeTypeStructureGenerator.show()
                self.treeTypeStructureGenerator.update()
            else:
                self.treeTypeStructureGenerator.hide()

    #+----------------------------------------------
    #| Update the content of the tree store for type structure
    #+----------------------------------------------
    def updateTreeStoreSearchView(self):
        if self.netzob.getCurrentProject() != None:
            isActive = self.netzob.getCurrentProject().getConfiguration().getVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_DISPLAY_SEARCH)
            if isActive:
                self.treeSearchGenerator.show()
            else:
                self.treeSearchGenerator.update()
                self.treeSearchGenerator.hide()

    def updateTreeStoreProperties(self):
        if self.netzob.getCurrentProject() != None:
            isActive = self.netzob.getCurrentProject().getConfiguration().getVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_DISPLAY_PROPERTIES)
            if isActive:
                self.treePropertiesGenerator.show()
                self.treePropertiesGenerator.update(self.selectedMessage)
            else:
                self.treePropertiesGenerator.hide()

    #+----------------------------------------------
    #| Called when user select a new score limit
    #+----------------------------------------------
    def updateScoreLimit(self, combo):
        val = combo.get_active_text()
        if self.netzob.getCurrentProject() != None:
            self.netzob.getCurrentProject().getConfiguration().setVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_EQUIVALENCE_THRESHOLD, int(val))

    #+----------------------------------------------
    #| Called when user wants to slick internally in libNeedleman
    #+----------------------------------------------
    def activeInternalSlickRegexes(self, checkButton):
        if self.netzob.getCurrentProject() != None:
            self.netzob.getCurrentProject().getConfiguration().setVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_DO_INTERNAL_SLICK, checkButton.get_active())

    #+----------------------------------------------
    #| Called when user wants to activate orphan reduction
    #+----------------------------------------------
    def activeOrphanReduction(self, checkButton):
        if self.netzob.getCurrentProject() != None:
            self.netzob.getCurrentProject().getConfiguration().setVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_ORPHAN_REDUCTION, checkButton.get_active())

    #+----------------------------------------------
    #| Called when user wants to modify the format displayed
    #+----------------------------------------------
    def updateDisplayFormat(self, combo):
        # Sanity checks
        if self.netzob.getCurrentProject() == None:
            NetzobErrorMessage("No project selected.")
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
        if self.netzob.getCurrentProject() == None:
            NetzobErrorMessage("No project selected.")
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
        if self.netzob.getCurrentProject() == None:
            NetzobErrorMessage("No project selected.")
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
        if self.netzob.getCurrentProject() == None:
            NetzobErrorMessage("No project selected.")
            return

        # Set the endianess choice as default
        endianess = combo.get_active_text()
        configuration = self.netzob.getCurrentProject().getConfiguration()
        configuration.setVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_GLOBAL_ENDIANESS, endianess)

        # Apply choice on selected symbol
        for symbol in self.netzob.getCurrentProject().getVocabulary().getSymbols():
            symbol.setEndianess(endianess)
        self.update()

    #+----------------------------------------------
    #| Called when user wants to freeze partitioning (at the regex level)
    #+----------------------------------------------
    def freezePartitioning_cb(self, button):
        # Sanity checks
        if self.netzob.getCurrentProject() == None:
            NetzobErrorMessage("No project selected.")
            return
        if self.selectedSymbol == None:
            NetzobErrorMessage("No symbol selected.")
            return

        self.selectedSymbol.freezePartitioning()
        self.update()
        NetzobInfoMessage("Freezing done.")

    #+----------------------------------------------
    #| Called when user wants to execute data carving
    #+----------------------------------------------
    def dataCarving_cb(self, button):
        # Sanity checks
        if self.netzob.getCurrentProject() == None:
            NetzobErrorMessage("No project selected.")
            return
        if self.selectedSymbol == None:
            NetzobErrorMessage("No symbol selected.")
            return

        self.log.info("Execute Data Carving on symbol ${0}".format(self.selectedSymbol.getName()))
        self.executeDataCarving(self.selectedSymbol)

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
            self.treeSearchGenerator.update(task)
#
#        box = self.selectedSymbol.dataCarving()
#        if box != None:
#            NetzobErrorMessage("No data found in messages and fields.")
#        else:
#            dialog = gtk.Dialog(title="Data carving results", flags=0, buttons=None)
#            dialog.vbox.pack_start(box, True, True, 0)
#            dialog.show()

    #+----------------------------------------------
    #| Called when user wants to search data in messages
    #+----------------------------------------------
    def search_cb(self, button):
        # Sanity checks
        if self.netzob.getCurrentProject() == None:
            NetzobErrorMessage("No project selected.")
            return

        self.prepareSearch(self.searchEntry.get_text(), self.typeCombo.get_active_text())

    def prepareSearch(self, searchedPattern, typeOfPattern):
        if len(searchedPattern) == 0:
            NetzobErrorMessage("Do not start the searching process since no pattern has been provided")
            return

        if len(typeOfPattern) == 0:
            NetzobErrorMessage("Do not start the searching process since no type has been provided")
            return

        self.log.debug("User searches for " + searchedPattern + " of type " + typeOfPattern)
        self.search(searchedPattern, typeOfPattern)

        # Active the messages and the search view
        self.netzob.getCurrentProject().getConfiguration().setVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_DISPLAY_MESSAGES, True)
        self.netzob.getCurrentProject().getConfiguration().setVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_DISPLAY_SEARCH, True)
        self.netzob.getMenu().setDisplaySearchViewActiveStatus(True)
        # We update the different views
        self.update()

    def prepareSearchInSymbol(self, searchedPattern, typeOfPattern, symbol):
        if len(searchedPattern) == 0:
            NetzobErrorMessage("Do not start the searching process since no pattern has been provided")
            return

        if len(typeOfPattern) == 0:
            NetzobErrorMessage("Do not start the searching process since no type has been provided")
            return

        self.log.debug("User searches for " + searchedPattern + " of type " + typeOfPattern + " in symbol " + str(symbol.getName()))
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
            self.log.warn("No data to search after were computed.")
            return

        self.log.debug("The following data will be searched for :")
        for data in searchedData:
            self.log.debug(" - " + str(data))

        # Then we search them in the list of messages included in the vocabulary
        if type == None:
            searchTasks = searcher.search(searchedData)
        elif type == "Symbol" and inclusion != None:
            searchTasks = searcher.searchInSymbol(searchedData, inclusion)

        # Give the results to the dedicated view
        self.treeSearchGenerator.update(searchTasks)

    #+----------------------------------------------
    #| Called when user wants to identifies environment dependencies
    #+----------------------------------------------
    def env_dependencies_cb(self, button):
        # Sanity checks
        if self.netzob.getCurrentProject() == None:
            NetzobErrorMessage("No project selected.")
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
                        self.treeSearchGenerator.update(searchTasks)
                    elif propertyType == Format.IP:
                        searchTasks = searcher.searchInMessage(searcher.getSearchedDataForIP(str(propertyValue)), message)
                        self.treeSearchGenerator.update(searchTasks)
                    elif propertyType == Format.DECIMAL:
                        searchTasks = searcher.searchInMessage(searcher.getSearchedDataForDecimal(str(propertyValue)), message)
                        self.treeSearchGenerator.update(searchTasks)

    #+----------------------------------------------
    #| Called when user wants to see the distribution of a symbol of messages
    #+----------------------------------------------
    def messagesDistribution_cb(self, but):
        # Sanity checks
        if self.netzob.getCurrentProject() == None:
            NetzobErrorMessage("No project selected.")
            return
        if self.selectedSymbol == None:
            NetzobErrorMessage("No symbol selected.")
            return

        entropy = Entropy(self.selectedSymbol)
        entropy.buildDistributionView()

    #+----------------------------------------------
    #| Called when user wants to find ASN.1 fields
    #+----------------------------------------------
    def findASN1Fields_cb(self, button):
        # Sanity checks
        if self.netzob.getCurrentProject() == None:
            NetzobErrorMessage("No project selected.")
            return
        if self.selectedSymbol == None:
            NetzobErrorMessage("No symbol selected.")
            return

        box = self.selectedSymbol.findASN1Fields(self.netzob.getCurrentProject())
        if box == None:
            NetzobErrorMessage("No ASN.1 field found.")
        else:  # Show the results
            dialog = gtk.Dialog(title="Find ASN.1 fields", flags=0, buttons=None)
            dialog.vbox.pack_start(box, True, True, 0)
            dialog.show()

    #+----------------------------------------------
    #| Called when user wants to find the potential size fields
    #+----------------------------------------------
    def findSizeFields(self, button):
        # Sanity checks
        if self.netzob.getCurrentProject() == None:
            NetzobErrorMessage("No project selected.")
            return
        if self.selectedSymbol == None:
            NetzobErrorMessage("No symbol selected.")
            return

        # Save the current encapsulation level of each field
        savedEncapsulationLevel = []
        for field in self.selectedSymbol.getFields():
            savedEncapsulationLevel.append(field.getEncapsulationLevel())

        sizeFieldIdentifier = SizeFieldIdentifier()

        # Show the progression dialog
        dialog = gtk.Dialog(title="Size Fields Identifications", flags=0, buttons=None)
        panel = gtk.Table(rows=2, columns=2, homogeneous=False)
        panel.show()

        # Progress bar
        self.progressBarSizeField = NetzobProgressBar()
        panel.attach(self.progressBarSizeField, 0, 2, 0, 1, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        # Buttons
        cancelSizeFieldButton = NetzobButton("Cancel")
        startSizeFieldButton = NetzobButton("Start")

        cancelSizeFieldButton.set_sensitive(False)
        cancelSizeFieldButton.connect("clicked", self.cancelfindSizeFields_cb, dialog, startSizeFieldButton, sizeFieldIdentifier)
        startSizeFieldButton.connect("clicked", self.findSizeFields_cb, dialog, sizeFieldIdentifier, [self.selectedSymbol], cancelSizeFieldButton, savedEncapsulationLevel)

        panel.attach(startSizeFieldButton, 0, 1, 1, 2, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        panel.attach(cancelSizeFieldButton, 1, 2, 1, 2, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        dialog.vbox.pack_start(panel, True, True, 0)
        dialog.show()

    def findSizeFields_cb(self, button, dialog, sizeFieldIdentifier, symbols, cancelButton, savedEncapsulationLevel):
        # first we deactivate the start button
        button.set_sensitive(False)
        # reactivate the cancel button
        cancelButton.set_sensitive(True)

        self.currentExecutionOfFindSizeFieldHasFinished = False
        # Start the progress bar
        gobject.timeout_add(100, self.do_pulse_for_findSizeField)
        # Start the findsize field JOB
        Job(self.startFindSizeField(sizeFieldIdentifier, symbols, dialog, savedEncapsulationLevel))

    def startFindSizeField(self, sizeFieldIdentifier, symbols, dialog, savedEncapsulationLevel):
        results = []
        self.currentExecutionOfFindSizeFieldHasFinished = False
        try:
            (yield ThreadedTask(sizeFieldIdentifier.search, symbols, results))
        except TaskError, e:
            self.log.error("Error while proceeding to the size field identification : " + str(e))

        sizeFields = sizeFieldIdentifier.getResults()
        logging.debug(sizeFields)

        self.currentExecutionOfFindSizeFieldHasFinished = True
        dialog.destroy()
        self.findSizeFields_results_cb(results, savedEncapsulationLevel)

    #+----------------------------------------------
    #| do_pulse_for_findSizeField:
    #|   Computes if the progress bar must be updated or not
    #+----------------------------------------------
    def do_pulse_for_findSizeField(self):
        if self.currentExecutionOfFindSizeFieldHasFinished == False:
            self.progressBarSizeField.pulse()
            return True
        return False

    def cancelfindSizeFields_cb(self, button, dialog, startButton, sizeFieldIdentifier):
        # first we deactivate the cancel button
        button.set_sensitive(False)
        # deactivate the start button
        startButton.set_sensitive(True)

        sizeFieldIdentifier.cancel()

        self.currentExecutionOfFindSizeFieldHasFinished = True

    def findSizeFields_results_cb(self, results, savedEncapsulationLevel):
       dialog = gtk.Dialog(title="Potential size fields and related payload", flags=0, buttons=None)
       ## ListStore format:
       # int: size field column
       # int: size field size
       # int: start column
       # int: substart column
       # int: end column
       # int: subend column
       # str: message rendered in cell
       treeview = gtk.TreeView(gtk.ListStore(int, int, int, int, int, int, str))
       cell = gtk.CellRendererText()
       treeview.connect("cursor-changed", self.sizeField_selected, savedEncapsulationLevel)
       column = gtk.TreeViewColumn('Size field and related payload')
       column.pack_start(cell, True)
       column.set_attributes(cell, text=6)
       treeview.append_column(column)

       # Chose button
       but = NetzobButton("Apply size field")
       but.connect("clicked", self.applySizeField, dialog, savedEncapsulationLevel)
       dialog.action_area.pack_start(but, True, True, 0)

       # Text view containing potential size fields
       treeview.set_size_request(800, 300)

       if len(results) == 0:
           NetzobErrorMessage("No size field found.")
       else:
           for result in results:
               treeview.get_model().append(result)

           treeview.show()
           scroll = gtk.ScrolledWindow()
           scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
           scroll.show()
           scroll.add(treeview)
           dialog.vbox.pack_start(scroll, True, True, 0)
           dialog.connect("destroy", self.destroyDialogFindSizeFields, savedEncapsulationLevel)
           dialog.show()

    def destroyDialogFindSizeFields(self, dialog, savedEncapsulationLevel):
        # Optionaly restore original encapsulation levels if there were no modification
        i = -1
        for field in self.selectedSymbol.getFields():
            i += 1
            field.setEncapsulationLevel(savedEncapsulationLevel[i])
        self.update()

    #+----------------------------------------------
    #| Called when user wants to try to apply a size field on a symbol
    #+----------------------------------------------
    def sizeField_selected(self, treeview, savedEncapsulationLevel):
        # Optionaly restore original encapsulation levels
        i = -1
        for field in self.selectedSymbol.getFields():
            i += 1
            field.setEncapsulationLevel(savedEncapsulationLevel[i])

        # Apply new encapsulation levels
        (model, iter) = treeview.get_selection().get_selected()
        if(iter):
            if(model.iter_is_valid(iter)):
                size_field = model.get_value(iter, 0)
                size_field_len = model.get_value(iter, 1)
                start_field = model.get_value(iter, 2)
                start_field_len = model.get_value(iter, 3)
                end_field = model.get_value(iter, 4)
                end_field_len = model.get_value(iter, 5)

                sizeField = self.selectedSymbol.getFieldByIndex(size_field)
                startField = self.selectedSymbol.getFieldByIndex(start_field)
                endField = self.selectedSymbol.getFieldByIndex(end_field)

#                # We check if some values of the size field are longer than the expected size field length
#                cells = self.selectedSymbol.getCellsByField(sizeField)
#                for cell in cells:
#                    if len(cell) > size_field_len:
#                        print "SPLIT"
#                        # Then we split the field
#                        self.selectedSymbol.splitField(sizeField, size_field_len)

                sizeField.setDescription("size field")
                startField.setDescription("start of payload")
                for i in range(start_field, end_field + 1):
                    field = self.selectedSymbol.getFieldByIndex(i)
                    field.setEncapsulationLevel(field.getEncapsulationLevel() + 1)

                self.update()

    #+----------------------------------------------
    #| Called when user wants to apply a size field on a symbol
    #+----------------------------------------------
    def applySizeField(self, button, dialog, savedEncapsulationLevel):
        # Apply the new encapsulation levels on original fields
        del savedEncapsulationLevel[:]
        for field in self.selectedSymbol.getFields():
            savedEncapsulationLevel.append(field.getEncapsulationLevel())
