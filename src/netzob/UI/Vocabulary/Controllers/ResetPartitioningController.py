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
#| ResetPartitioningController:
#+----------------------------------------------
class ResetPartitioningController:

    #+----------------------------------------------
    #| Constructor:
    #| @param netzob: the netzob main class
    #+----------------------------------------------
    def __init__(self, netzob, vocabularyController):
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.UI.Vocabulary.Controllers.ResetPartitioningController.py')
        self.netzob = netzob
        self.vocabularyController = vocabularyController
        self.initCallbacks()

    def initCallbacks(self):
        pass

    #+----------------------------------------------
    #| resetPartitioning_cb:
    #|   Called when user wants to reset the current alignment
    #+----------------------------------------------
    def resetPartitioning(self, symbols):
        # Sanity checks
        if self.netzob.getCurrentProject() == None:
            NetzobErrorMessage(_("No project selected."))
            return
        for symbol in symbols:
            symbol.resetPartitioning(self.netzob.getCurrentProject())
        self.vocabularyController.update()
