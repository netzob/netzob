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
from netzob.UI.Vocabulary.Views.Partitioning.NewForcePartitioningView import NewForcePartitioningView


class NewForcePartitioningController(object):
    '''
    classdocs
    '''

    def __init__(self, vocabularyController):
        self.vocabularyController = vocabularyController
        self._view = NewForcePartitioningView(self)
        self.log = logging.getLogger(__name__)

    @property
    def view(self):
        return self._view

    def force_cancel_clicked_cb(self, widget):
        self._view.forceDialog.destroy()

    def force_execute_clicked_cb(self, widget):
        #update widget
        self._view.force_stop.set_sensitive(True)
        self._view.force_cancel.set_sensitive(False)
        self._view.force_execute.set_sensitive(False)
        self._view.force_entry.set_sensitive(False)
        self._view.force_radiobutton_hexa.set_sensitive(False)
        self._view.force_radiobutton_string.set_sensitive(False)
        #extract choose value
        symbolList = self.vocabularyController.view.getCheckedSymbolList()
        delimiter = self._view.force_entry.get_text()
        if self._view.force_radiobutton_hexa.get_active():
            delimiterType = "hexa"
        else:
            delimiterType = "string"
        # ++CODE HERE++
        # FORCE PARTITIONING ON symbolList
        # THE PARAMETER FORMAT: [ symbolList (symbol list),delimiter (string), delimiterType (string) ]
        # OPEN THREAD TO STOP IT
        # SET REGULARLY VALUE FOR PROGRESS BAR WITH
        # fraction = 0 <+int+< 1
        # self._view.force_progressbar.set_fraction(fraction)

        #update button
        self._view.force_stop.set_sensitive(True)

        #close dialog box
        #self._view.forceDialog.destroy()

    def force_stop_clicked_cb(self, widget):
        # update button
        self._view.force_stop.set_sensitive(False)

        # ++CODE HERE++
        # STOP THE THREAD OF FORCE PARTITIONING

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
        # ++CODE HERE++
        # SET THE LAST DELIMITER USE WITH
        # delimiter = +string+
        # self._view.force_entry.set_text(delimiter)
        # SET THE LAST VALUE USE FOR FORMAT OF DELIMITER
        # self._view.force_radiobutton_hexa.set_active(True)
        # or
        # self._view.force_radiobutton_string.set_active(True)
        self.force_entry_changed_cb(self._view.force_entry)
        self._view.run()
