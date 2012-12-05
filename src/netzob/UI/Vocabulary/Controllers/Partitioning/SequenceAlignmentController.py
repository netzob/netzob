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
from gettext import gettext as _
import logging

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+
import gi
from gi.repository import Gtk, Gdk, GObject
gi.require_version('Gtk', '3.0')
import time

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.Threads.Job import Job
from netzob.Common.Threads.Tasks.ThreadedTask import ThreadedTask, TaskError
from netzob.Common.ProjectConfiguration import ProjectConfiguration
from netzob.UI.Vocabulary.Views.Partitioning.SequenceAlignmentView import SequenceAlignmentView
from netzob.Inference.Vocabulary.Alignment.NeedlemanAndWunsch import NeedlemanAndWunsch


class SequenceAlignmentController(object):
    '''Controls the execution of the alignment process'''

    def __init__(self, vocabularyController, fields=[], doUpgma=False):
        self.vocabularyController = vocabularyController
        self._view = SequenceAlignmentView(self)
        self.log = logging.getLogger(__name__)
        self.alignmentSolution = None
        self.fields = fields
        self.doUpgma = doUpgma

        if doUpgma is False:
            self.view.similarity_box.hide()
            self.view.orphanButton.hide()

    @property
    def view(self):
        return self._view

    def sequence_cancel_clicked_cb(self, widget):
        """Callback executed when the user close the alignment window"""
        self._view.sequenceDialog.destroy()

    def sequence_execute_clicked_cb(self, widget):
        """Callback executed when the user request to start
        the alignment process"""

        self._view.sequence_cancel.set_sensitive(False)
        self._view.sequence_execute.set_sensitive(False)
        self._view.sequence_scale.set_sensitive(False)
        self._view.sequence_spinbutton.set_sensitive(False)
        self._view.radiobutton4bit.set_sensitive(False)
        self._view.radiobutton8bit.set_sensitive(False)
        self._view.orphanButton.set_sensitive(False)
        self._view.smoothButton.set_sensitive(False)

        # retrieves the alignment parameters
        similarityPercent = self._view.sequence_adjustment.get_value()
        if self._view.radiobutton8bit.get_mode():
            unitSize = 8
        else:
            unitSize = 4
        orphan = self._view.orphanButton.get_active()
        smooth = self._view.smoothButton.get_active()

        self.vocabularyController.getCurrentProject().getConfiguration().setVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_EQUIVALENCE_THRESHOLD, int(similarityPercent))
        self.vocabularyController.getCurrentProject().getConfiguration().setVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_ORPHAN_REDUCTION, orphan)
        self.vocabularyController.getCurrentProject().getConfiguration().setVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_DO_INTERNAL_SLICK, smooth)

        # Configure Needleman and Wunsch
        self.alignmentSolution = NeedlemanAndWunsch(unitSize, self.vocabularyController.getCurrentProject(), self.doUpgma, self.percentOfAlignmentProgessBar)

        # Define the alignment JOB
        self._view.sequence_stop.set_sensitive(True)
        Job(self.startSequenceAlignment(unitSize))

    def startSequenceAlignment(self, unitSize):
        """Definition of a JOB, which executes the alignment process
        @type unitSize: int
        @var unitSize: the unit size to consider when aligning
        """
        try:
            (yield ThreadedTask(self.alignmentSolution.alignFields, self.fields))
        except TaskError, e:
            self.log.error("Error while proceeding to the alignment: {0}".format(str(e)))

        if self.doUpgma is True:
            # We have new symbols
            newSymbols = self.alignmentSolution.getNewSymbols()
            if newSymbols is not None and len(newSymbols) > 0:
                self.vocabularyController.getCurrentProject().getVocabulary().setSymbols(newSymbols)
                # Clean the interface
                self._view.resetProgressBars()
                # Close dialog box
                self._view.sequenceDialog.destroy()
                self.vocabularyController.restart()
                return
        else:
            # Clean the interface
            self._view.resetProgressBars()
            # Close dialog box
            self._view.sequenceDialog.destroy()
            # Update the message table view
            self.vocabularyController.view.updateSelectedMessageTable()
            # Update the field properties view
            self.vocabularyController.view.updateLeftPanel()

    def percentOfAlignmentProgessBar(self, stage, percent, message):
        # select the good progress bar in function of the stage
        progressBar = None
        totalPercent = None
        nbStage = 4
        if self.vocabularyController.getCurrentProject().getConfiguration().getVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_ORPHAN_REDUCTION):
            nbStage = 5

        if stage == 0:
            progressBar = self._view.stage0ProgressBar
        elif stage == 1:
            progressBar = self._view.stage1ProgressBar
        elif stage == 2:
            progressBar = self._view.stage2ProgressBar
        elif stage == 3:
            progressBar = self._view.stage3ProgressBar
        elif stage == 4:
            progressBar = self._view.stage4ProgressBar

        if nbStage != 5:
            self._view.labelStage3.hide()
            self._view.stage3ProgressBar.hide()

        if stage > 0:
            self._view.labelStage0.hide()
            self._view.stage0ProgressBar.hide()

        if stage > 1:
            self._view.labelStage1.hide()
            self._view.stage1ProgressBar.hide()

        if stage > 2:
            self._view.labelStage2.hide()
            self._view.stage2ProgressBar.hide()

        if stage > 3:
            self._view.labelStage3.hide()
            self._view.stage3ProgressBar.hide()

        if stage > 4:
            self._view.labelStage4.hide()
            self._view.stage4ProgressBar.hide()

        if percent is not None:
            totalPercent = (100 / nbStage) * stage + percent / nbStage
            valPercent = float(percent) / float(100)
            valTotalPercent = float(totalPercent) / float(100)
            time.sleep(0.01)
            GObject.idle_add(self._view.sequence_progressbar.set_fraction, valTotalPercent)
            GObject.idle_add(progressBar.set_fraction, valPercent)

        if message is None:
            GObject.idle_add(self._view.sequence_progressbar.set_text, "")
        else:
            GObject.idle_add(self._view.sequence_progressbar.set_text, message)

    def sequence_stop_clicked_cb(self, widget):
        #update button

        self._view.sequence_stop.set_sensitive(False)
        # ++CODE HERE++
        self.alignmentSolution.stop()

        #update widget
        self._view.sequence_cancel.set_sensitive(True)
        self._view.sequence_execute.set_sensitive(True)
        self._view.sequence_scale.set_sensitive(True)
        self._view.sequence_spinbutton.set_sensitive(True)
        self._view.radiobutton4bit.set_sensitive(True)
        self._view.radiobutton8bit.set_sensitive(True)
        self._view.orphanButton.set_sensitive(True)
        self._view.smoothButton.set_sensitive(True)

    def run(self):
        self._view.sequence_stop.set_sensitive(False)
        # ++CODE HERE++
        # SET THE LAST SIMILARITY PERCENT USE WITH
        # similarityPercent = 0 <+double+< 100
        # self._view.sequence_adjustment.set_value(similarityPercent)
        # SET THE LAST VALUE USE FOR ORPHAN AND SMOOTH REDUCTION
        # self._view.orphanButton.set_active(+boolean+)
        # self._view.smoothButton.set_active(+boolean+)
        # SET THE LAST VALUE USE FOR UNITSIZE
        # self._view.radiobutton8bit.set_active(True)
        # or
        # self._view.radiobutton4bit.set_active(True)
        self._view.run()
