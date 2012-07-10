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
from netzob.Inference.Vocabulary.Alignment.NeedlemanAndWunsch import NeedlemanAndWunsch


#+----------------------------------------------
#| SequenceAlignmentController:
#+----------------------------------------------
class SequenceAlignmentController:

    #+----------------------------------------------
    #| Constructor:
    #| @param netzob: the netzob main class
    #+----------------------------------------------
    def __init__(self, netzob, vocabularyController):
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.UI.Vocabulary.Controllers.SequenceAlignmentController.py')
        self.netzob = netzob
        self.vocabularyController = vocabularyController
        self.initCallbacks()

    def initCallbacks(self):
        pass

    def sequenceAlignmentOnSpecifiedSymbols(self, widget, symbols):
        # Execute the process of alignment (show the gui...)
        self.sequenceAlignment(symbols)

    #+----------------------------------------------
    #| sequenceAlignment:
    #|   Parse the traces and store the results
    #+----------------------------------------------
    def sequenceAlignment(self, symbols):
        self.vocabularyController.clear()
        self.vocabularyController.update()

        dialog = Gtk.Dialog(title=_("Sequence alignment"), flags=0, buttons=None)
        panel = Gtk.Table(rows=5, columns=3, homogeneous=False)
        panel.show()

        ## Similarity threshold
        label = NetzobLabel(_("Similarity threshold:"))
        self.comboSimilarityThreshold = Gtk.ComboBoxText.new_with_entry()
        self.comboSimilarityThreshold.set_model(Gtk.ListStore(str))
        self.comboSimilarityThreshold.connect("changed", self.updateScoreLimit)
        possible_choices = [100, 95, 90, 85, 80, 75, 70, 65, 60, 55, 50, 45, 40, 35, 30, 25, 20, 15, 10, 5]

        min_equivalence = self.netzob.getCurrentProject().getConfiguration().getVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_EQUIVALENCE_THRESHOLD)
        for i in range(len(possible_choices)):
            self.comboSimilarityThreshold.append_text(str(possible_choices[i]))
            if str(possible_choices[i]) == str(int(min_equivalence)):
                self.comboSimilarityThreshold.set_active(i)
        self.comboSimilarityThreshold.show()
        panel.attach(label, 0, 1, 0, 1, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)
        panel.attach(self.comboSimilarityThreshold, 1, 2, 0, 1, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)

        ## UnitSize for alignment
        label = NetzobLabel(_("Unit size (in bits):"))
        self.comboUnitSize = Gtk.ComboBoxText.new_with_entry()
        self.comboUnitSize.set_model(Gtk.ListStore(str))
        possible_choices = [8, 4]

        for i in range(len(possible_choices)):
            self.comboUnitSize.append_text(str(possible_choices[i]))
        self.comboUnitSize.set_active(0)
        self.comboUnitSize.show()
        panel.attach(label, 0, 1, 1, 2, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)
        panel.attach(self.comboUnitSize, 1, 2, 1, 2, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)

        # Widget button activate orphan reduction
        self.butOrphanReduction = Gtk.CheckButton(_("Orphan reduction"))
        doOrphanReduction = self.netzob.getCurrentProject().getConfiguration().getVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_ORPHAN_REDUCTION)
        if doOrphanReduction:
            self.butOrphanReduction.set_active(True)
        else:
            self.butOrphanReduction.set_active(False)
        self.butOrphanReduction.connect("toggled", self.activeOrphanReduction)
        self.butOrphanReduction.show()
        panel.attach(self.butOrphanReduction, 0, 1, 2, 3, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)

        # Widget checkbox for selecting the slickery during alignement process
        butdoInternalSlick = Gtk.CheckButton(_("Smooth alignment"))
        doInternalSlick = self.netzob.getCurrentProject().getConfiguration().getVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_DO_INTERNAL_SLICK)
        if doInternalSlick:
            butdoInternalSlick.set_active(True)
        else:
            butdoInternalSlick.set_active(False)
        butdoInternalSlick.connect("toggled", self.activeInternalSlickRegexes)
        butdoInternalSlick.show()
        panel.attach(but, 1, 2, 2, 3, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)

        # Progress bar
        self.progressbarAlignment = NetzobProgressBar()
        panel.attach(self.progressbarAlignment, 0, 2, 3, 4, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)

        # Button
        searchButton = NetzobButton(_("Sequence alignment"))
        searchButton.connect("clicked", self.sequenceAlignment_cb_cb, dialog, symbols, self.comboUnitSize)
        panel.attach(searchButton, 0, 2, 4, 5, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)

        dialog.vbox.pack_start(panel, True, True, 0)
        dialog.show()

    #+----------------------------------------------
    #| sequenceAlignment_cb_cb:
    #|   Launch a sequence alignment thread
    #+----------------------------------------------
    def sequenceAlignment_cb_cb(self, widget, dialog, symbols, comboUnitSize):
        self.currentExecutionOfAlignmentHasFinished = False
        # Start the progress bar
        GObject.timeout_add(100, self.do_pulse_for_sequenceAlignment)
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
            self.log.error(_("Error while proceeding to the alignment: {0}").format(str(e)))

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
#        GObject.idle_add(self.progressbarAlignment.set_fraction, float(percent))
        if message == None:
            GObject.idle_add(self.progressbarAlignment.set_text, "")
        else:
            GObject.idle_add(self.progressbarAlignment.set_text, message)

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
    #| Called when user select a new score limit
    #+----------------------------------------------
    def updateScoreLimit(self, combo):
        val = combo.get_active_text()
        if self.netzob.getCurrentProject() != None:
            self.netzob.getCurrentProject().getConfiguration().setVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_EQUIVALENCE_THRESHOLD, int(val))

    #+----------------------------------------------
    #| do_pulse_for_sequenceAlignment:
    #|   Computes if the progress bar must be updated or not
    #+----------------------------------------------
    def do_pulse_for_sequenceAlignment(self):
        if self.currentExecutionOfAlignmentHasFinished == False:
            self.progressbarAlignment.pulse()
            return True
        return False
