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
#| Standard library imports                                                  |
#+---------------------------------------------------------------------------+
from gettext import gettext as _
from gi.repository import Gtk
from netzob.Common.MMSTD.Dictionary.Variables.AggregateVariable import \
    AggregateVariable
from netzob.Common.MMSTD.Dictionary.Variables.AlternateVariable import \
    AlternateVariable
from netzob.UI.Vocabulary.Views.VariableView import VariableTreeView
import logging
import os
import uuid

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+


class VariableTreeController:
    """VariableTreeController:
            Controls a variable's tree view display
    """

    def __init__(self, netzob, field):
        """Constructor of VariableTreeController:

                @type netzob: netzob.Common.NetzobGui.NetzobGui
                @param netzob: the main netzob project.
                @type field: netzob.Common.Field.Field
                @param field: the field, the variable of which we want to display.
        """
        self.log = logging.getLogger(__name__)
        self.netzob = netzob
        self.field = field
        self.view = VariableTreeView(self)
        self.fillTreeView(self.field.getVariable())
        self.initCallbacks()

    def initCallbacks(self):
        """initCallbacks:
                Init the callbacks.
        """
        self.treeview.connect('button-press-event', self.showMenu)

    def fillTreeView(self, variable):
        """fillTreeView:
                Fill the tree view of a variable with all its displayable content.

                @type variable: netzob.Common.MMSTD.Dictionary.Variables.AbstractVariable.AbstractVariable
                @param variable: the root variable which content will be displayed.
        """
        self.lvcolumn = Gtk.TreeViewColumn(_("Description of the variable"))
        self.lvcolumn.set_sort_column_id(1)
        cell = Gtk.CellRendererText()
        self.lvcolumn.pack_start(cell, True)
        self.lvcolumn.add_attribute(cell, "text", 1)
        self.view.treeview.append_column(self.lvcolumn)

        self.treestore = Gtk.TreeStore(str, str)  # id of the data, description
        self.registerVariable(None, variable)
        self.view.treeview.set_model(self.treestore)

    def registerVariable(self, rootEntry, variable):
        """registerVariable:
                Register a variable in the tree view under its root variable (Aggregate or Alternate).

                @type rootEntry: Gtk.treestore entry
                @param rootEntry: the root entry under which we will add this entry.
                @type variable: netzob.Common.MMSTD.Dictionary.Variables.AbstractVariable.AbstractVariable
                @param variable: the variable which will be added to the tree view representation.
        """
        self.datas[str(variable.getID())] = variable
        newEntry = self.treestore.append(rootEntry, [str(variable.getID()), variable.getName()])
        if variable.getType() == AggregateVariable.TYPE or variable.getType() == AlternateVariable.TYPE:
            for child in variable.getChildren():
                self.registerVariable(newEntry, child)

    def showMenu(self, treeview, event):
        """showMenu:
                Called on right click on a variable.

                @param treeview: the treeview which contains the triggering variable.
                @param event: the mouse event which called this function.
        """
        rootVariable = None
        if event.type == Gtk.EventType.BUTTON_PRESS and event.button == 3:
            x = int(event.x)
            y = int(event.y)
            (path, treeviewColumn, x, y) = treeview.get_path_at_pos(x, y)

            # Retrieve the selected variable
            variable_id = None
            aIter = treeview.get_model().get_iter(path)
            if aIter:
                if treeview.get_model().iter_is_valid(aIter):
                    variable_id = treeview.get_model().get_value(aIter, 0)

                    for varid in self.datas.keys():
                        if varid == variable_id:
                            rootVariable = self.datas[varid]

        if rootVariable is None:
            self.log.debug(_("Impossible to find the selected variable."))
            return

        # We display the menu for the insertion of sub-elements if its an Aggregate or an Alternative
        self.menu = Gtk.Menu()
        subElementMenu = Gtk.Menu()

        # Data Variable
        itemDataVariable = Gtk.MenuItem(_("Data variable"))
        itemDataVariable.show()
        itemDataVariable.connect("activate", DataVariableCreationController, self.netzob, rootVariable)
        subElementMenu.append(itemDataVariable)

        # Structural Variable
        itemStructVariable = Gtk.MenuItem(_("Structural variable"))
        itemStructVariable.show()
        itemStructVariable.connect("activate", DataVariableCreationController, self.netzob, rootVariable)
        subElementMenu.append(itemStructVariable)

        itemAdd = Gtk.MenuItem(_("Add a sub-element"))
        itemAdd.set_submenu(subElementMenu)
        itemAdd.show()

        itemEdit = Gtk.MenuItem(_("Edit"))
        itemEdit.show()

        self.menu.append(itemAdd)
        self.menu.append(itemEdit)
        self.menu.popup(None, None, None, None, event.button, event.time)


class DataVariableCreationController:

    def __init__(self, netzob, rootVariable):
        self.netzob = netzob
        self.rootVariable = rootVariable
