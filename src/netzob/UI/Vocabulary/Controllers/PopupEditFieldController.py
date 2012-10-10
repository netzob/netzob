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
gi.require_version('Gtk', '3.0')
from gi.repository import GObject
from gi.repository import Pango

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.UI.Vocabulary.Views.PopupEditFieldView import PopupEditFieldView
from netzob.Common.Type.TypeConvertor import TypeConvertor


class PopupEditFieldController(object):
    """Popup to edit a field"""

    def __init__(self, vocabularyController, field):
        self.vocabularyController = vocabularyController
        self._view = PopupEditFieldView(self)
        self.log = logging.getLogger(__name__)
        self.field = field

    @property
    def view(self):
        return self._view

    def run(self):
        self.populateData()
        self._view.run()

    #+----------------------------------------------
    #|  populateData:
    #|   Populate data in the popup
    #+----------------------------------------------
    def populateData(self):
        # Fieldname
        self.view.fieldName.set_text(self.field.getName())
        # Description
        if self.field.getDescription():
            self.view.description.set_text(self.field.getDescription())
        else:
            self.view.description.set_text("")
        # Regex
        self.view.regex.set_text(self.field.getRegex())

    def cancel_clicked_cb(self, widget):
        self.view.dialog.destroy()

    def apply_clicked_cb(self, widget):
        # Update field name
        text = self.view.fieldName.get_text()
        if (len(text) > 0):
            self.field.setName(text)
        # Update field description
        text = self.view.description.get_text()
        if (len(text) > 0):
            self.field.setDescription(text)
        # Update field regex
        text = self.view.regex.get_text()
        if (len(text) > 0):
            self.field.setRegex(text)
        self.vocabularyController.view.updateSelectedMessageTable()
        # UI update
        self.view.dialog.destroy()
        self.vocabularyController.view.updateSelectedMessageTable()
