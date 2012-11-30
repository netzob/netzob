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
from netzob.Common.ResourcesConfiguration import ResourcesConfiguration


class EnvironmentDependenciesSearcherView(object):

    def __init__(self, controller):
        '''
        Constructor
        '''
        self.builder = Gtk.Builder()
        self.builder.add_from_file(os.path.join(ResourcesConfiguration.getStaticResources(),
                                                "ui", "vocabulary",
                                                "environmentDependenciesSearcherView.glade"))
        self._getObjects(self.builder, ["envDepsSearcherDialog",
                                        "cancelButton",
                                        "executeButton",
                                        "searchProgressBar",
                                        "envDependenciesListstore"
                                        ])
        self.controller = controller
        self.builder.connect_signals(self.controller)
        self.cancelButton.set_sensitive(True)

        # Update the list store of env. dependencies
        currentProject = self.controller.vocabularyController.getCurrentProject()
        envDeps = []
        if currentProject is not None:
            envDeps.extend(currentProject.getEnvironmentDependencies())

        for envDep in envDeps:
            i = self.envDependenciesListstore.append()
            self.envDependenciesListstore.set(i, 0, str(envDep.getCurrentValue()))
            self.envDependenciesListstore.set(i, 1, str(envDep.getName()))
            self.envDependenciesListstore.set(i, 2, str(envDep.getFormat()))

    def _getObjects(self, builder, objectsList):
        for obj in objectsList:
            setattr(self, obj, builder.get_object(obj))

    def run(self):
        self.envDepsSearcherDialog.run()

    def destroy(self):
        self.envDepsSearcherDialog.destroy()
