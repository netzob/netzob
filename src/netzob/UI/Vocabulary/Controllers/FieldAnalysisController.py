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
from netzob.UI.Vocabulary.Views.FieldAnalysisView import FieldAnalysisView
from netzob.Common.Type.TypeConvertor import TypeConvertor


class FieldAnalysisController(object):
    """Popup for field analysis (definition domain and type guessing)"""

    def __init__(self, vocabularyController, field):
        self.vocabularyController = vocabularyController
        self._view = FieldAnalysisView(self)
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

        # Definition domain
        cells = self.field.getUniqValuesByField()
        tmpDomain = set()
        for cell in cells:
            tmpDomain.add(TypeConvertor.encodeNetzobRawToGivenType(cell, self.field.getFormat()))
        domain = sorted(tmpDomain)
        for elt in domain:
            self.view.domainListstore.append([elt])

        # Type guessing
        types = self.field.getPossibleTypes()
        for t in types:
            self.view.typeListstore.append([t])

    def close_clicked_cb(self, widget):
        self.view.dialog.destroy()
