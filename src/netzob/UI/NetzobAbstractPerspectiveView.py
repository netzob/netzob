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
from gi.repository import Gtk

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.UI.NetzobAbstractView import NetzobAbstractView


class NetzobAbstractPerspectiveView(NetzobAbstractView):
    def __init__(self, controller, viewFilePath, root="root", actionGroup="actionGroup", actionGroupFilePath=None, uiMenuBar=None):
        super(NetzobAbstractPerspectiveView, self).__init__(controller, viewFilePath, root)

        self.actionGroup = None
        self.menubarUIDefinition = None

        if actionGroup is not None:
            if actionGroupFilePath is not None:
                builder = Gtk.Builder()
                builder.add_from_file(self._findUiResource(actionGroupFilePath))
                self.actionGroup = builder.get_object(actionGroup)
                builder.connect_signals(controller)
            else:
                self.actionGroup = self.builder.get_object(actionGroup)

        if uiMenuBar is not None:
            with open(self._findUiResource(uiMenuBar), "r") as menubarUIDefinitionFile:
                self.menubarUIDefinition = menubarUIDefinitionFile.read()

    def getPanel(self):
        return self.root

    def getActionGroup(self):
        return self.actionGroup

    def getMenuToolbarUIDefinition(self):
        return self.menubarUIDefinition
