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
import os

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


class ContextualMenuOnStateView(object):

    def __init__(self, controller):
        self.controller = controller

    def run(self, event):
        self.menu = Gtk.Menu()

        # Add entry to edit state
        item = Gtk.MenuItem(_("Edit State"))
        item.show()
        item.connect("activate", self.controller.editState_cb)
        self.menu.append(item)

        # Transitions
        for transition in self.controller.getState().getTransitions():
            subMenu = self.build_submenu_for_transition(transition)
            item = Gtk.MenuItem(_("Transition {0}".format(transition.getName())))
            item.set_submenu(subMenu)
            item.show()
            self.menu.append(item)

        # Add entry to delete state
        item = Gtk.MenuItem(_("Delete State"))
        item.show()
        item.connect("activate", self.controller.deleteState_cb)
        self.menu.append(item)

        self.menu.popup(None, None, None, None, event.button, event.time)

    def build_submenu_for_transition(self, transition):
        menu = Gtk.Menu()

        item = Gtk.MenuItem(_("Edit"))
        item.show()
        item.connect("button-press-event", self.controller.editTransition_cb, transition)
        # We use 'button-press-event', because 'activate' does not always work in submenu
        menu.append(item)

        item = Gtk.MenuItem(_("Delete"))
        item.show()
        item.connect("button-press-event", self.controller.deleteTransition_cb, transition)
        # We use 'button-press-event', because 'activate' does not always work in submenu
        menu.append(item)

        return menu
