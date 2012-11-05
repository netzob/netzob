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
gi.require_version('Gtk', '3.0')
from gi.repository import GObject

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.UI.Vocabulary.Views.Partitioning.SimplePartitioningView import SimplePartitioningView
from netzob.Common.Threads.Tasks.ThreadedTask import ThreadedTask, TaskError
from netzob.Common.Threads.Job import Job
from netzob.Common.Type.UnitSize import UnitSize


class SimplePartitioningController(object):
    '''
    classdocs
    '''

    def __init__(self, vocabularyController, fields=[]):
        self.vocabularyController = vocabularyController
        self._view = SimplePartitioningView(self)
        self.log = logging.getLogger(__name__)
        self.flagStop = False
        self.fields = fields

    @property
    def view(self):
        return self._view

    def simple_cancel_clicked_cb(self, widget):
        self._view.simpleDialog.destroy()

    def simple_execute_clicked_cb(self, widget):
        self.flagStop = False
        # update widget
        self._view.simple_cancel.set_sensitive(False)
        self._view.simple_execute.set_sensitive(False)
        self._view.radiobutton4bits.set_sensitive(False)
        self._view.radiobutton8bits.set_sensitive(False)
        self._view.radiobutton16bits.set_sensitive(False)
        self._view.radiobutton32bits.set_sensitive(False)
        self._view.radiobutton64bits.set_sensitive(False)

        self._view.simple_stop.set_sensitive(True)

        #extract chosen value
        formatBits = UnitSize.BITS8
        if self._view.radiobutton4bits.get_active():
            formatBits = UnitSize.BITS4
        elif self._view.radiobutton16bits.get_active():
            formatBits = UnitSize.BITS16
        elif self._view.radiobutton32bits.get_active():
            formatBits = UnitSize.BITS32
        elif self._view.radiobutton64bits.get_active():
            formatBits = UnitSize.BITS64

        # create a job to execute the partitioning
        Job(self.startSimplePartitioning(formatBits))

    def startSimplePartitioning(self, unitSize):
        if len(self.fields) > 0:
            self.log.debug("Start to simple partitioning the selected fields")
            try:
                (yield ThreadedTask(self.simplePartitioning, unitSize))
            except TaskError, e:
                self.log.error("Error while proceeding to the simple partitioning of fields: {0}".format(str(e)))
        else:
            self.log.debug("No field selected")

        # Update button
        self._view.simple_stop.set_sensitive(False)

        # Close dialog box
        self._view.simpleDialog.destroy()

        # Update the message table view
        self.vocabularyController.view.updateSelectedMessageTable()
        # Update the field properties view
        self.vocabularyController.view.updateLeftPanel()

    def simplePartitioning(self, unitSize):
        """Simple partitioning the provided fields"""
        self.id_current_field = 0
        for field in self.fields:
            GObject.idle_add(self._view.simple_progressbar.set_text, _("Simple partitioning field {0}".format(field.getName())))
            if self.isFlagStopRaised():
                return
            field.simplePartitioning(unitSize, self.updateProgessBar, self.isFlagStopRaised)
            self.id_current_field += 1

    def updateProgessBar(self, percent, message):
        """Update the progress bar given the provided informations"""
        nbStage = len(self.fields)
        if percent is not None:
            totalPercent = (100 / nbStage) * self.id_current_field + percent / nbStage
            valTotalPercent = float(totalPercent) / float(100)
            time.sleep(0.01)
            GObject.idle_add(self._view.simple_progressbar.set_fraction, valTotalPercent)

        if message is None:
            GObject.idle_add(self._view.simple_progressbar.set_text, "")
        else:
            GObject.idle_add(self._view.simple_progressbar.set_text, message)

    def isFlagStopRaised(self):
        return self.flagStop

    def simple_stop_clicked_cb(self, widget):
        # update button
        self._view.simple_stop.set_sensitive(False)
        self.flagStop = True

        # update widget
        self._view.simple_execute.set_sensitive(True)
        self._view.simple_cancel.set_sensitive(True)
        self._view.radiobutton4bits.set_sensitive(True)
        self._view.radiobutton8bits.set_sensitive(True)
        self._view.radiobutton16bits.set_sensitive(True)
        self._view.radiobutton32bits.set_sensitive(True)
        self._view.radiobutton64bits.set_sensitive(True)

    def run(self):
        self._view.simple_stop.set_sensitive(False)
        self._view.radiobutton8bits.set_active(True)
        self._view.run()
