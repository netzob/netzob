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
import logging
import os

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+
from gi.repository import Gtk

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.ResourcesConfiguration import ResourcesConfiguration


class AbstractView(object):
    """AbstractView:
            An abstract class mothering all views for the variable management.
    """
    def __init__(self, controller, gladeFileName):

        self.controller = controller
        self.builderWidget = Gtk.Builder()
        gladePath = os.path.join(ResourcesConfiguration.getStaticResources(), "ui", "Variables", gladeFileName)
        self.builderWidget.add_from_file(gladePath)
        self.widgDict = dict()

    def getObjects(self, keyList):
        """getObjects:
                Get a list of objects from the glade model to python.

                @type strObjectList: string list
                @param strObjectList: the list of all the objects we want to get from the glade model to python.
        """
        self.widgDict = dict()
        for key in keyList:
            # logging.debug("get object: {0} with key: {1}".format(self.builderWidget.get_object(key), key))
            self.widgDict[key] = self.builderWidget.get_object(key)

    def showObjects(self):
        """showObjects:
                Show all objects of a view.
        """
        for widget in self.widgDict.itervalues():
            widget.show()

#+---------------------------------------------------------------------------+
#| Getters and setters                                                       |
#+---------------------------------------------------------------------------+
    def getWidgDict(self):
        return self.widgDict

    def getWidg(self, key):
        return self.widgDict[key]


class VariableTreeView(AbstractView):
    """VariableTreeView:
            The tree view of a variable (and its prospective children).
    """

    GLADE_FILENAME = "VariableTreeView.glade"

    def __init__(self, controller):
        AbstractView.__init__(self, controller, VariableTreeView.GLADE_FILENAME)
        self.getObjects(["dialog", "button", "treeview", "createDefaultVariable_button"])
        self.showObjects()

        # Make the column
        self.lvcolumn = Gtk.TreeViewColumn(_("Description of the variable"))
        self.lvcolumn.set_sort_column_id(-1)
        cell = Gtk.CellRendererText()
        self.lvcolumn.pack_start(cell, True)
        self.lvcolumn.add_attribute(cell, "text", 1)
        self.getWidg("treeview").append_column(self.lvcolumn)

    def destroyDialog(self, widget):
        """destroyDialog:
                Destroy the dialog window.
                This function is here for connection purpose. A connection always add extra arguments such as this 'widget'.
        """
        self.getWidg("dialog").destroy()


class VariableCreationView(AbstractView):
    """VariableCreationView:
            The view that allows users to create/edit variables.
    """

    GLADE_FILENAME = "VariableCreationView.glade"

    def __init__(self, controller):
        AbstractView.__init__(self, controller, VariableCreationView.GLADE_FILENAME)
        self.getObjects(["dialog", "applyButton", "nameEntry", "mutableCheck", "learnableCheck", "minLabel", "maxLabel", "minSpin", "maxSpin", "variableTypeCombo", "valueLabel", "valueEntry", "typeLabel", "typeCombo", "relationTypeLabel", "relationTypeCombo", "IDButton", "IDEntry", "IDLabel", "IDGrid", "sizedLabel", "sizedCheck", "delimiterLabel", "delimiterEntry"])
        self.showObjects()


class VariableMovingView(AbstractView):
    """VariableMovingView:
            The view that allows users to move variables.
    """

    GLADE_FILENAME = "VariableMovingView.glade"

    def __init__(self, controller):
        AbstractView.__init__(self, controller, VariableMovingView.GLADE_FILENAME)
        self.getObjects(["dialog", "applyButton", "entry"])
        self.showObjects()
