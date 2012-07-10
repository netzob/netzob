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
from netzob.Common.Type.Format import Format
from netzob.Common.Type.UnitSize import UnitSize
from netzob.Common.Type.Sign import Sign
from netzob.Common.Type.Endianess import Endianess


#+----------------------------------------------
#| SimplePartitioningController:
#+----------------------------------------------
class SimplePartitioningController:

    #+----------------------------------------------
    #| Constructor:
    #| @param netzob: the netzob main class
    #+----------------------------------------------
    def __init__(self, netzob, vocabularyController):
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.UI.Vocabulary.Controllers.SimplePartitioningController.py')
        self.netzob = netzob
        self.vocabularyController = vocabularyController
        self.initCallbacks()

    def initCallbacks(self):
        pass

    #+----------------------------------------------
    #| simplePartitioning:
    #|   Apply a simple partitioning
    #+----------------------------------------------
    def simplePartitioning(self, symbols):
#        self.vocabularyController.clear()
#        self.vocabularyController.update()

        dialog = Gtk.Dialog(title=_("Simple partitioning"), flags=0, buttons=None)
        panel = Gtk.Table(rows=3, columns=3, homogeneous=False)
        panel.show()

        # Label
        label = NetzobLabel(_("Minimum unit size: "))
        panel.attach(label, 0, 1, 0, 1, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)

        # Delimiter type
        possible_choices = [UnitSize.NONE, UnitSize.BIT, UnitSize.BITS8, UnitSize.BITS16, UnitSize.BITS32, UnitSize.BITS64]
        typeCombo = NetzobComboBoxEntry()
        for i in range(len(possible_choices)):
            typeCombo.append_text(possible_choices[i])
            if possible_choices[i] == UnitSize.NONE:
                typeCombo.set_active(i)
        panel.attach(typeCombo, 1, 2, 0, 1, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)

        # Button
        searchButton = NetzobButton(_("Simple partitioning"))
        searchButton.connect("clicked", self.simplePartitioning_cb_cb, dialog, typeCombo, symbols)
        panel.attach(searchButton, 0, 2, 2, 3, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)

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
        self.vocabularyController.update()
