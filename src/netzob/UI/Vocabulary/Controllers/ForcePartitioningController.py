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
#| ForcePartitioningController:
#+----------------------------------------------
class ForcePartitioningController:

    #+----------------------------------------------
    #| Constructor:
    #| @param netzob: the netzob main class
    #+----------------------------------------------
    def __init__(self, netzob, vocabularyController):
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.UI.Vocabulary.Controllers.ForcePartitioningController.py')
        self.netzob = netzob
        self.vocabularyController = vocabularyController
        self.initCallbacks()

    def initCallbacks(self):
        pass

    def forcePartitioningOnSpecifiedSymbols(self, widget, symbols):
        # Execute the process of alignment (show the gui...)
        self.forcePartitioning(symbols)

    #+----------------------------------------------
    #| forcePartitioning_cb:
    #|   Force the delimiter for partitioning
    #+----------------------------------------------
    def forcePartitioning(self, symbols):
        self.vocabularyController.clear()
        self.vocabularyController.update()

        dialog = Gtk.Dialog(title=_("Force partitioning"), flags=0, buttons=None)
        panel = Gtk.Table(rows=3, columns=3, homogeneous=False)
        panel.show()

        # Label
        label = NetzobLabel(_("Delimiter: "))
        panel.attach(label, 0, 1, 0, 1, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)

        # Entry for delimiter
        entry = Gtk.Entry()
        entry.set_max_length(4)
        entry.show()
        panel.attach(entry, 1, 2, 0, 1, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)

        # Label
        label = NetzobLabel(_("Format type: "))
        panel.attach(label, 0, 1, 1, 2, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)

        # Delimiter type
        typeCombo = Gtk.ComboBoxText.new_with_entry()
        typeCombo.show()
        typeStore = Gtk.ListStore(str)
        typeCombo.set_model(typeStore)
        typeCombo.get_model().append([Format.STRING])
        typeCombo.get_model().append([Format.HEX])
        typeCombo.set_active(0)
        panel.attach(typeCombo, 1, 2, 1, 2, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)

        # Button
        searchButton = NetzobButton(_("Force partitioning"))
        searchButton.connect("clicked", self.forcePartitioning_cb_cb, dialog, typeCombo, entry, symbols)
        panel.attach(searchButton, 0, 2, 2, 3, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)

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
