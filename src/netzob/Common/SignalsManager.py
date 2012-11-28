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

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+


class SignalsManager(object):
    """Manage the signals for feature availability"""

    SIG_PROJECT_OPEN = "project.open"
    SIG_PROJECT_CLOSE = "project.close"

    SIG_SYMBOLS_NONE_CHECKED = "symbols.none_checked"
    SIG_SYMBOLS_SINGLE_CHECKED = "symbols.single_checked"
    SIG_SYMBOLS_MULTIPLE_CHECKED = "symbols.multiple_checked"

    SIG_SYMBOLS_NO_SELECTION = "symbols.no_selection"
    SIG_SYMBOLS_SINGLE_SELECTION = "symbols.single_selection"
    SIG_SYMBOLS_MULTIPLE_SELECTION = "symbols.multiple_selection"

    SIG_FIELDS_NO_SELECTION = "fields.no_selection"
    SIG_FIELDS_SINGLE_SELECTION = "field.single_selection"
    SIG_FIELDS_MULTIPLE_SELECTION = "field.multiple_selection"

    SIG_MESSAGES_NO_SELECTION = "messages.no_selection"
    SIG_MESSAGES_SINGLE_SELECTION = "messages.single_selection"
    SIG_MESSAGES_MULTIPLE_SELECTION = "messages.multiple_selection"

    def __init__(self):
        self.log = logging.getLogger(__name__)
        self.log.debug("Initialize signals manager")
        self.listeners = dict()

    def emitSignals(self, signals):
        for signal in signals:
            self.emitSignal(signal)

    def emitSignal(self, signal):
        """emitSignal"""
        listeners = self.getListenersMethodsForSignal(signal)
        for listener in listeners:
            listener(signal)

    def attach(self, methodToExecute, signals):
        self.listeners[methodToExecute] = signals

    def getListenersMethodsForSignal(self, signal):
        result = []
        for l in self.listeners.keys():
            if signal in self.listeners[l]:
                result.append(l)
        return result
