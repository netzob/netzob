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
from netzob.UI.Vocabulary.Views.Menus.ContextualMenuOnSymbolView import ContextualMenuOnSymbolView
from netzob.UI.NetzobWidgets import NetzobLabel
from netzob.Common.Type.TypeConvertor import TypeConvertor
from netzob.UI.Vocabulary.Controllers.PopupEditFieldController import PopupEditFieldController


class ContextualMenuOnSymbolController(object):
    """Contextual menu on symbol (visualization, etc.)"""

    def __init__(self, vocabularyController, symbol):
        self.vocabularyController = vocabularyController
        self.symbol = symbol
        self._view = ContextualMenuOnSymbolView(self)
        self.log = logging.getLogger(__name__)

    @property
    def view(self):
        return self._view

    def run(self, event):
        self._view.run(event)

    #+----------------------------------------------
    #| rightClickToChangeFormat:
    #|   Callback to change the field/symbol format
    #|   by doing a right click on it.
    #+----------------------------------------------
    def changeFormat_cb(self, event, aFormat):
        self.symbol.setFormat(aFormat)
        self.vocabularyController.view.updateSelectedMessageTable()

    #+----------------------------------------------
    #| rightClickToChangeUnitSize:
    #|   Callback to change the field/symbol unitsize
    #|   by doing a right click on it.
    #+----------------------------------------------
    def changeUnitSize_cb(self, event, unitSize):
        self.symbol.setUnitSize(unitSize)
        self.vocabularyController.view.updateSelectedMessageTable()

    #+----------------------------------------------
    #| rightClickToChangeSign:
    #|   Callback to change the field/symbol sign
    #|   by doing a right click on it.
    #+----------------------------------------------
    def changeSign_cb(self, event, sign):
        self.symbol.setSign(sign)
        self.vocabularyController.view.updateSelectedMessageTable()

    #+----------------------------------------------
    #| rightClickToChangeEndianess:
    #|   Callback to change the field/symbol endianess
    #|   by doing a right click on it.
    #+----------------------------------------------
    def changeEndianess_cb(self, event, endianess):
        self.symbol.setEndianess(endianess)
        self.vocabularyController.view.updateSelectedMessageTable()


    def applyMathematicFilter_cb(self, event, mathFilter):
        """Add the selected mathematic filter"""
        found = False
        for appliedFilter in self.symbol.getMathematicFilters():
            if appliedFilter.getName() == mathFilter.getName():
                found = True
                break
        if found:
            self.symbol.removeMathematicFilter(appliedFilter)
        else:
            self.symbol.addMathematicFilter(mathFilter)

        self.vocabularyController.view.updateSelectedMessageTable()

