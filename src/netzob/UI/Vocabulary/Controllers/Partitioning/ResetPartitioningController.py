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
from netzob.UI.Vocabulary.Views.Partitioning.ResetPartitioningView import ResetPartitioningView


class ResetPartitioningController(object):
    """Reset the partitions on selected fields"""

    def __init__(self, vocabularyController, fields=[]):
        self.vocabularyController = vocabularyController
        self._view = ResetPartitioningView(self)
        self.log = logging.getLogger(__name__)
        self.flagStop = False
        self.fields = fields

    @property
    def view(self):
        return self._view

    def reset_cancel_clicked_cb(self, widget):
        self._view.resetDialog.destroy()

    def reset_execute_clicked_cb(self, widget):
        """Callback executed when the user
        requests to start the r
        operation"""
        # update widget
        self._view.reset_cancel.set_sensitive(False)
        self._view.reset_execute.set_sensitive(False)
        self._view.reset_stop.set_sensitive(True)

        # Define the reset JOB
        Job(self.startReset())

        #update button
        self._view.reset_cancel.set_sensitive(True)
        self._view.reset_execute.set_sensitive(False)
        self._view.reset_stop.set_sensitive(False)

    def startReset(self):
        """Start the reset operation by creating
        a dedicated thread
        """
        if len(self.fields) > 0:
            self.log.debug("Start to reset the selected fields")
            try:
                (yield ThreadedTask(self.reset))
            except TaskError, e:
                self.log.error("Error while proceeding to the reseting of fields: {0}".format(str(e)))
        else:
            self.log.debug("No field selected")

        # Update button
        self._view.reset_stop.set_sensitive(True)

        # Close dialog box
        self._view.resetDialog.destroy()

        # Update the UI
        self.vocabularyController.view.updateLeftPanel()
        self.vocabularyController.view.updateSelectedMessageTable()

    def reset(self):
        """Reset the provided fields"""
        step = float(100) / float(len(self.fields))
        total = float(0)
        for field in self.fields:
            GObject.idle_add(self._view.reset_progressbar.set_text, _("Reset field {0}".format(field.getName())))
            if self.flagStop:
                return
            field.resetPartitioning()
            total = total + step
            rtotal = float(total) / float(100)
            time.sleep(0.01)
            GObject.idle_add(self._view.reset_progressbar.set_fraction, rtotal)
        GObject.idle_add(self._view.reset_progressbar.set_text, _("Reset finished!"))

    def reset_stop_clicked_cb(self, widget):
        """Callback executed when the
        user wants to stop the current reset operation"""
        # update button
        self._view.reset_stop.set_sensitive(False)
        # update widget
        self._view.reset_execute.set_sensitive(True)
        self._view.reset_cancel.set_sensitive(True)
        self.flagStop = True

    def run(self):
        self._view.reset_stop.set_sensitive(False)
        self._view.run()

    def stop(self):
        self.flagStop = True
