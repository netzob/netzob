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
from netzob.UI.Common.Views.CustomMathFilterView import CustomMathFilterView
gi.require_version('Gtk', '3.0')
from gi.repository import GObject
from netzob.Common.ResourcesConfiguration import ResourcesConfiguration


#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
class CustomMathFilterController(object):
    """Manage the creation of a custom math filter"""

    def __init__(self, vocabularyController):
        self.vocabularyController = vocabularyController
        self.log = logging.getLogger(__name__)
        self._view = CustomMathFilterView(self)

    @property
    def view(self):
        return self._view

    def run(self):
        self._view.run()

    def cancelButton_clicked_cb(self, widget):
        """Callback executed when the user clicks
        on the cancel button"""
        print "cancel"

    def applyButton_clicked_cb(self, widget):
        """Callback executed when the user clicks
        on the apply button."""
        print "apply"
