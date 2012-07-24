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
from gi.repository import Gtk, Gdk
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import GObject

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.UI.Vocabulary.Views.NewSequenceAlignmentView import NewSequenceAlignmentView

class NewSequenceAlignmentController(object):
    '''
    classdocs
    '''


    def __init__(self, vocabularyController):
        self.vocabularyController = vocabularyController
        self._view = NewSequenceAlignmentView(self)
        self.log = logging.getLogger(__name__)

    @property
    def view(self):
        return self._view

    def sequence_cancel_clicked_cb(self, widget):
        self._view.sequenceDialog.destroy()

    def sequence_execute_clicked_cb(self, widget):
        #update button
        self._view.sequence_stop.set_sensitive(True)
        self._view.sequence_cancel.set_sensitive(False)
        self._view.sequence_execute.set_sensitive(False)
        #extract choose value
        symbolList = self.vocabularyController.getCheckedSymbolList()
        similarityPercent = self._view.sequence_adjustment.get_value()
        if self._view.radiobutton8bit.get_mode():
            unitSize = 8
        else:
            unitSize = 4
        orphan = self._view.orphanButton.get_active()
        smooth = self._view.smoothButton.get_active()
        # ++CODE HERE++
        # SEQUENCE ALIGNMENT ON symbolList
        # THE PARAMETER FORMAT: [ symbolList (symbol list),similarityPercent (double), orphan smooth (boolean) ]
        # OPEN THREAD TO STOP IT
        # SET REGULARLY VALUE FOR PROGRESS BAR WITH
        # fraction = 0 <+int+< 1
        # self._view.sequence_progressbar.set_fraction(fraction)

    def sequence_stop_clicked_cb(self, widget):
        self._view.sequence_execute.set_sensitive(True)
        self._view.sequence_cancel.set_sensitive(True)
        self._view.sequence_stop.set_sensitive(False)
        # ++CODE HERE++
        # STOP THE THREAD OF SEQUENCE ALIGNEMENT


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
