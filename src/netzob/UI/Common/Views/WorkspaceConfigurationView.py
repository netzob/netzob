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
from locale import gettext as _
import os

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+
from gi.repository import Gtk, Gdk

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.ResourcesConfiguration import ResourcesConfiguration


class WorkspaceConfigurationView(object):

    def __init__(self, controller, parent=None):
        self.builder = Gtk.Builder()
        self.builder.add_from_file(os.path.join(ResourcesConfiguration.getStaticResources(),
                                                "ui",
                                                "workspaceConfigurationDialog.glade"))
        self._getObjects(self.builder,
                         ["workspaceConfigurationDialog",
                          "advancedLoggingCombobox",
                          ])
        self.controller = controller
        self.workspaceConfigurationDialog.set_transient_for(parent)

        # Set combobox to the configured log level
        model = self.advancedLoggingCombobox.get_model()
        treeIter = model.get_iter_first()
        while treeIter is not None:
            if model[treeIter][0] == self.controller._loggingConfiguration.getLoggingLevel():
                self.advancedLoggingCombobox.set_active_iter(treeIter)
                break
            treeIter = model.iter_next(treeIter)

        # Finally, connect signals to the controller
        self.builder.connect_signals(self.controller)

    def _getObjects(self, builder, objectsList):
        for obj in objectsList:
            setattr(self, obj, builder.get_object(obj))

    def run(self):
        self.workspaceConfigurationDialog.show_all()

    def destroy(self):
        self.workspaceConfigurationDialog.destroy()
