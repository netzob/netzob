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
from gi.repository import Gtk, Gdk, GObject
import gi
from netzob.Common.Threads.Job import Job
from netzob.Common.Threads.Tasks.ThreadedTask import ThreadedTask, TaskError
gi.require_version('Gtk', '3.0')
from gi.repository import GObject

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.UI.Vocabulary.Views.NewSmoothPartitioningView import NewSmoothPartitioningView


class NewSmoothPartitioningController(object):
    """Executes the smooth operation on selected symbols"""

    def __init__(self, vocabularyController):
        self.vocabularyController = vocabularyController
        self._view = NewSmoothPartitioningView(self)
        self.log = logging.getLogger(__name__)
        self.flagStop = False

    @property
    def view(self):
        return self._view

    def smooth_cancel_clicked_cb(self, widget):
        self._view.smoothDialog.destroy()

    def smooth_execute_clicked_cb(self, widget):
        """Callback executed when the user
        requests to start the smooth
        operation"""
        # update widget
        self._view.smooth_cancel.set_sensitive(False)
        self._view.smooth_execute.set_sensitive(False)
        self._view.smooth_stop.set_sensitive(True)
        #extract choose value
        symbolList = self.vocabularyController.view.getCheckedSymbolList()

        # Define the smooth JOB
        Job(self.startSmooth(symbolList))

        #update button
        self._view.smooth_cancel.set_sensitive(True)
        self._view.smooth_execute.set_sensitive(False)
        self._view.smooth_stop.set_sensitive(False)

    def startSmooth(self, symbols):
        """Start the smooth operation by creating
        a dedicated thread
        @var symbols: the list of symbols that should be smoothed
        """
        if len(symbols) > 0:
            self.log.debug("Start to smooth the selected symbols")
            try:
                (yield ThreadedTask(self.smooth, symbols))
            except TaskError, e:
                self.log.error(_("Error while proceeding to the smoothing of symbols: {0}").format(str(e)))

            self.vocabularyController.restart()
        else:
            self.log.debug("No symbol selected")

    def smooth(self, symbols):
        """Smooth the provided symbols"""
        step = float(100) / float(len(symbols))
        total = float(0)
        for symbol in symbols:
            GObject.idle_add(self._view.smooth_progressbar.set_text, _("Smooth symbol {0}".format(symbol.getName())))
            if self.flagStop:
                return
            symbol.slickRegex(self.vocabularyController.getCurrentProject())
            total = total + step
            rtotal = float(total) / float(100)
            time.sleep(0.01)
            GObject.idle_add(self._view.smooth_progressbar.set_fraction, rtotal)
        GObject.idle_add(self._view.smooth_progressbar.set_text, _("Smooth finished !"))

    def smooth_stop_clicked_cb(self, widget):
        """Callback executed when the
        user wants to stop the current smooth operation"""
        # update button
        self._view.smooth_stop.set_sensitive(False)
        # update widget
        self._view.smooth_execute.set_sensitive(True)
        self._view.smooth_cancel.set_sensitive(True)
        self.flagStop = True

    def run(self):
        self._view.smooth_stop.set_sensitive(False)
        self._view.run()

    def stop(self):
        self.flagStop = True
