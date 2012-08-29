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
import time

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+
from gi.repository import Gtk, Gdk
import gi
from netzob.Common.Type.TypeConvertor import TypeConvertor
from netzob.Common.Threads.Tasks.ThreadedTask import ThreadedTask, TaskError
from netzob.Common.Threads.Job import Job
from netzob.Common.Type.Format import Format
gi.require_version('Gtk', '3.0')
from gi.repository import GObject

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.UI.Vocabulary.Views.Partitioning.ForcePartitioningView import ForcePartitioningView


class ForcePartitioningController(object):
    """Manages the execution of the force partitioning on
    the selected symbols"""

    def __init__(self, vocabularyController, symbols=[]):
        self.vocabularyController = vocabularyController
        self._view = ForcePartitioningView(self)
        self.log = logging.getLogger(__name__)
        self.flagStop = False
        self.symbols = symbols

    @property
    def view(self):
        return self._view

    def force_cancel_clicked_cb(self, widget):
        self._view.forceDialog.destroy()

    def force_execute_clicked_cb(self, widget):
        self.flagStop = False
        #update widget
        self._view.force_stop.set_sensitive(True)
        self._view.force_cancel.set_sensitive(False)
        self._view.force_execute.set_sensitive(False)
        self._view.force_entry.set_sensitive(False)
        self._view.force_radiobutton_hexa.set_sensitive(False)
        self._view.force_radiobutton_string.set_sensitive(False)
        #extract choose value
        delimiter = self._view.force_entry.get_text()
        if self._view.force_radiobutton_hexa.get_active():
            delimiterType = Format.HEX
        else:
            delimiterType = Format.STRING

        # encode the delimiter
        encodedDelimiter = TypeConvertor.encodeGivenTypeToNetzobRaw(delimiter, delimiterType)

        # create a job to execute the partitioning
        Job(self.startForcePartitioning(encodedDelimiter, delimiterType))

    def startForcePartitioning(self, delimiter, format):
        if len(self.symbols) > 0:
            self.log.debug("Start to force partitioning the selected symbols")
            try:
                (yield ThreadedTask(self.forcePartitioning, delimiter, format))
            except TaskError, e:
                self.log.error(_("Error while proceeding to the force partitioning of symbols: {0}").format(str(e)))
        else:
            self.log.debug("No symbol selected")

        #update button
        self._view.force_stop.set_sensitive(True)

        #close dialog box
        self._view.forceDialog.destroy()

    def forcePartitioning(self, encodedDelimiter, format):
        """Smooth the provided symbols"""
        step = float(100) / float(len(self.symbols))
        total = float(0)
        for symbol in self.symbols:
            GObject.idle_add(self._view.force_progressbar.set_text, _("Force partitioning symbol {0}".format(symbol.getName())))
            if self.flagStop:
                return
            symbol.forcePartitioning(format, encodedDelimiter)
            total = total + step
            rtotal = float(total) / float(100)
            time.sleep(0.01)
            GObject.idle_add(self._view.force_progressbar.set_fraction, rtotal)
        GObject.idle_add(self._view.force_progressbar.set_text, _("Force partitioning finished !"))

    def force_stop_clicked_cb(self, widget):
        # update button
        self._view.force_stop.set_sensitive(False)

        self.flagStop = True

        #update widget
        self._view.force_execute.set_sensitive(True)
        self._view.force_cancel.set_sensitive(True)
        self._view.force_entry.set_sensitive(True)
        self._view.force_radiobutton_hexa.set_sensitive(True)
        self._view.force_radiobutton_string.set_sensitive(True)

    def force_entry_changed_cb(self, widget):
        if(len(widget.get_text()) > 0):
            self._view.force_execute.set_sensitive(True)
        else:
            self._view.force_execute.set_sensitive(False)

    def run(self):
        self._view.force_stop.set_sensitive(False)
        self._view.run()
