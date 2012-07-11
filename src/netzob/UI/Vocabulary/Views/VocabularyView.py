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
gi.require_version('Gtk', '3.0')
import logging

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
from netzob.UI.Vocabulary.Views.TreeSymbolView import TreeSymbolView
from netzob.UI.Vocabulary.Views.TreeMessageView import TreeMessageView
from netzob.UI.Vocabulary.Views.TreeTypeStructureView import TreeTypeStructureView
from netzob.UI.Vocabulary.Views.TreePropertiesView import TreePropertiesView
from netzob.UI.Vocabulary.Views.TreeSearchView import TreeSearchView
from netzob.Inference.Vocabulary.VariableView import VariableView
from netzob.Inference.Vocabulary.Alignment.NeedlemanAndWunsch import NeedlemanAndWunsch
from netzob.Inference.Vocabulary.Searcher import Searcher


#+----------------------------------------------
#| VocabularyView:
#|     GUI for vocabulary inference
#+----------------------------------------------
class VocabularyView:

    #+----------------------------------------------
    #| Constructor:
    #| @param netzob: the netzob main class
    #+----------------------------------------------
    def __init__(self, netzob, controller):
        self.netzob = netzob
        self.log = logging.getLogger('netzob.UI.Vocabulary.View.VocabularyView.py')
        self.controller = controller
        self.buildPanel()

    def buildPanel(self):
        # Definition of the Sequence Onglet
        # First we create an VBox which hosts the two main children
        self.panel = Gtk.VBox(False, spacing=0)
        self.panel.show()

        #+----------------------------------------------
        #| TOP PART OF THE GUI : BUTTONS
        #+----------------------------------------------
        topPanel = Gtk.HBox(False, spacing=2)
        topPanel.show()
        self.panel.pack_start(topPanel, False, False, 0)

        ## Message format inference
        frame = NetzobFrame(_("1 - Message format inference"))
        topPanel.pack_start(frame, False, False, 0)
        table = Gtk.Table(rows=5, columns=2, homogeneous=False)
        table.show()
        frame.add(table)

        # Widget for sequence alignment
        self.butSeqAlignment = NetzobButton(_("Sequence alignment"))
        self.butSeqAlignment.set_tooltip_text(_("Automatically discover the best alignment of messages"))
        table.attach(self.butSeqAlignment, 0, 2, 0, 1, xoptions=Gtk.AttachOptions.FILL | Gtk.AttachOptions.EXPAND, yoptions=Gtk.AttachOptions.FILL, xpadding=2, ypadding=2)

        # Widget for forcing partitioning delimiter
        self.butForcePartitioning = NetzobButton(_("Force partitioning"))
        self.butForcePartitioning.set_tooltip_text(_("Set a delimiter to force partitioning"))
        table.attach(self.butForcePartitioning, 0, 2, 1, 2, xoptions=Gtk.AttachOptions.FILL | Gtk.AttachOptions.EXPAND, yoptions=Gtk.AttachOptions.FILL, xpadding=2, ypadding=2)

        # Widget for simple partitioning
        self.butSimplePartitioning = NetzobButton(_("Simple partitioning"))
        self.butSimplePartitioning.set_tooltip_text(_("In order to show the simple differences between messages"))
        table.attach(self.butSimplePartitioning, 0, 2, 2, 3, xoptions=Gtk.AttachOptions.FILL | Gtk.AttachOptions.EXPAND, yoptions=Gtk.AttachOptions.FILL, xpadding=2, ypadding=2)

        # Widget button slick regex
        self.butSmoothPartitioning = NetzobButton(_("Smooth partitioning"))
        self.butSmoothPartitioning.set_tooltip_text(_("Merge small static fields with its neighbours"))
        table.attach(self.butSmoothPartitioning, 0, 2, 3, 4, xoptions=Gtk.AttachOptions.FILL | Gtk.AttachOptions.EXPAND, yoptions=Gtk.AttachOptions.FILL, xpadding=2, ypadding=2)

        # Widget button reset partitioning
        self.butResetPartitioning = NetzobButton(_("Reset partitioning"))
        self.butResetPartitioning.set_tooltip_text(_("Reset the current partitioning"))
        table.attach(self.butResetPartitioning, 0, 2, 4, 5, xoptions=Gtk.AttachOptions.FILL | Gtk.AttachOptions.EXPAND, yoptions=Gtk.AttachOptions.FILL, xpadding=2, ypadding=2)

        ## Field type inference
        frame = NetzobFrame(_("2 - Field type inference"))
        topPanel.pack_start(frame, False, False, 0)
        table = Gtk.Table(rows=5, columns=2, homogeneous=False)
        table.show()
        frame.add(table)

        # Widget button refine regex
        self.butFreezePartitioning = NetzobButton(_("Freeze partitioning"))
        self.butFreezePartitioning.set_tooltip_text(_("Automatically find and freeze the boundaries (min/max of cell's size) for each fields"))
        table.attach(self.butFreezePartitioning, 0, 1, 0, 1, xoptions=Gtk.AttachOptions.FILL | Gtk.AttachOptions.EXPAND, yoptions=Gtk.AttachOptions.FILL, xpadding=2, ypadding=2)

        # Widget button to show message distribution
        self.butMessagesDistribution = NetzobButton(_("Messages distribution"))
        self.butMessagesDistribution.set_tooltip_text(_("Open a graph with messages distribution, separated by fields"))
        table.attach(self.butMessagesDistribution, 0, 1, 1, 2, xoptions=Gtk.AttachOptions.FILL | Gtk.AttachOptions.EXPAND, yoptions=Gtk.AttachOptions.FILL, xpadding=2, ypadding=2)

        # Widget button data carving
        self.butDataCarving = NetzobButton(_("Data carving"))
        self.butDataCarving.set_tooltip_text(_("Automatically look for known patterns of data (URL, IP, email, etc.)"))
        table.attach(self.butDataCarving, 0, 1, 2, 3, xoptions=Gtk.AttachOptions.FILL | Gtk.AttachOptions.EXPAND, yoptions=Gtk.AttachOptions.FILL, xpadding=2, ypadding=2)

        # Widget button to analyze for ASN.1 presence
#        self.but = NetzobButton("Find ASN.1 fields")
#        table.attach(self.but, 0, 1, 3, 4, xoptions=Gtk.AttachOptions.FILL | Gtk.AttachOptions.EXPAND, yoptions=Gtk.AttachOptions.FILL, xpadding=2, ypadding=2)

        ## Dependencies inference
        frame = NetzobFrame(_("3 - Dependencies inference"))
        topPanel.pack_start(frame, False, False, 0)
        table = Gtk.Table(rows=4, columns=4, homogeneous=False)
        table.show()
        frame.add(table)

        # Widget button find size fields
        self.butFindSizeFields = NetzobButton(_("Find size fields"))
        self.butFindSizeFields.set_tooltip_text(_("Automatically find potential size fields and associated payloads"))
        table.attach(self.butFindSizeFields, 0, 1, 0, 1, xoptions=Gtk.AttachOptions.FILL | Gtk.AttachOptions.EXPAND, yoptions=Gtk.AttachOptions.FILL, xpadding=2, ypadding=2)

        # Widget button for environment dependencies
        self.butEnvDependencies = NetzobButton(_("Environment dependencies"))
        self.butEnvDependencies.set_tooltip_text(_("Automatically look for environmental dependencies (retrieved during capture) in messages"))
        table.attach(self.butEnvDependencies, 0, 1, 1, 2, xoptions=Gtk.AttachOptions.FILL | Gtk.AttachOptions.EXPAND, yoptions=Gtk.AttachOptions.FILL, xpadding=2, ypadding=2)

        ## Visualization
        frame = NetzobFrame(_("4 - Visualization"))
        topPanel.pack_start(frame, False, False, 0)
        table = Gtk.Table(rows=4, columns=4, homogeneous=False)
        table.show()
        frame.add(table)

        # Widget for choosing the format
        label = NetzobLabel(_("Format : "))
        self.comboDisplayFormat = NetzobComboBoxEntry()
        table.attach(label, 0, 1, 0, 1, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=2, ypadding=0)
        table.attach(self.comboDisplayFormat, 1, 2, 0, 1, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=2, ypadding=0)

        # Widget for choosing the unit size
        label = NetzobLabel(_("Unit size : "))
        self.comboDisplayUnitSize = NetzobComboBoxEntry()
        table.attach(label, 0, 1, 1, 2, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=2, ypadding=0)
        table.attach(self.comboDisplayUnitSize, 1, 2, 1, 2, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=2, ypadding=0)

        # Widget for choosing the displayed sign
        label = NetzobLabel(_("Sign : "))
        self.comboDisplaySign = NetzobComboBoxEntry()
        table.attach(label, 0, 1, 2, 3, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=2, ypadding=0)
        table.attach(self.comboDisplaySign, 1, 2, 2, 3, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=2, ypadding=0)

        # Widget for choosing the displayed endianess
        label = NetzobLabel(_("Endianess : "))
        self.comboDisplayEndianess = NetzobComboBoxEntry()
        table.attach(label, 0, 1, 3, 4, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=2, ypadding=0)
        table.attach(self.comboDisplayEndianess, 1, 2, 3, 4, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=2, ypadding=0)

        ## Semantic inference
        frame = NetzobFrame(_("5 - Search data"))
        topPanel.pack_start(frame, False, False, 0)
        table = Gtk.Table(rows=4, columns=4, homogeneous=False)
        table.show()
        frame.add(table)

        # Widget button for search
        self.searchEntry = Gtk.Entry()
        self.searchEntry.show()
        table.attach(self.searchEntry, 0, 1, 0, 1, xoptions=Gtk.AttachOptions.FILL | Gtk.AttachOptions.EXPAND, yoptions=Gtk.AttachOptions.FILL, xpadding=2, ypadding=2)

        # Combo to select the type of the input
        self.typeCombo = Gtk.ComboBoxText.new_with_entry()
        self.typeCombo.show()
        self.typeStore = Gtk.ListStore(str)
        self.typeCombo.set_model(self.typeStore)
        self.typeCombo.get_model().append([Format.STRING])
        self.typeCombo.get_model().append([Format.HEX])
#        self.typeCombo.get_model().append([Format.BINARY])
#        self.typeCombo.get_model().append([Format.OCTAL])
        self.typeCombo.get_model().append([Format.DECIMAL])
        self.typeCombo.get_model().append([Format.IP])
        self.typeCombo.set_active(0)
        table.attach(self.typeCombo, 0, 1, 1, 2, xoptions=Gtk.AttachOptions.FILL | Gtk.AttachOptions.EXPAND, yoptions=Gtk.AttachOptions.FILL, xpadding=2, ypadding=2)

        self.butSearch = NetzobButton(_("Search"))
        self.butSearch.set_tooltip_text(_("A search function available in different encoding format"))
        table.attach(self.butSearch, 0, 1, 2, 3, xoptions=Gtk.AttachOptions.FILL | Gtk.AttachOptions.EXPAND, yoptions=Gtk.AttachOptions.FILL, xpadding=2, ypadding=2)

        #+----------------------------------------------
        #| LEFT PART OF THE GUI : SYMBOL TREEVIEW
        #+----------------------------------------------
        bottomPanel = Gtk.HPaned()
        bottomPanel.show()
        self.panel.pack_start(bottomPanel, True, True, 0)
        leftPanel = Gtk.VBox(False, spacing=0)
#        leftPanel.set_size_request(-1, -1)
        leftPanel.show()
        bottomPanel.add(leftPanel)
        # Initialize the treeview generator for the symbols
        leftPanel.pack_start(self.controller.treeSymbolController.getScrollLib(), True, True, 0)
        # Attach to the treeview few actions (DnD, cursor and buttons handlers...)
        self.controller.treeSymbolController.getTreeview().enable_model_drag_dest([], Gdk.DragAction.DEFAULT)
        self.controller.treeSymbolController.getTreeview().drag_dest_add_text_targets()

        #+----------------------------------------------
        #| RIGHT PART OF THE GUI :
        #| includes the messages treeview and the optional views in tabs
        #+----------------------------------------------
        rightPanel = Gtk.VPaned()
        rightPanel.show()
        bottomPanel.add(rightPanel)
        # add the messages in the right panel
        rightPanel.add(self.controller.treeMessageController.getScrollLib())
        # Attach to the treeview few actions (DnD, cursor and buttons handlers...)
        self.controller.treeMessageController.getTreeview().enable_model_drag_source(Gdk.ModifierType.BUTTON1_MASK, [], Gdk.DragAction.DEFAULT | Gdk.DragAction.MOVE)
        self.controller.treeMessageController.getTreeview().drag_source_add_text_targets()

        # find the optional views
        rightPanel.add(self.controller.optionalPanelsController.getView().getPanel())
