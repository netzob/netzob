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
import os
from gi.repository import Gtk

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.ResourcesConfiguration import ResourcesConfiguration


class NetzobAbstractViewException(Exception):
    pass


class NetzobAbstractView(object):

    def __init__(self, controller, viewFilePath, root="root", parent=None):
        self.builder = Gtk.Builder()
        self.builder.add_from_file(self._findUiResource(viewFilePath))

        self._getObjects([root])
        self.root = getattr(self, root)

        self.controller = controller

        if parent is not None:
            window = getattr(self, root)
            window.set_transient_for(parent)

        self.builder.connect_signals(self.controller)

    def run(self):
        self.root.show_all()

    def _findUiResource(self, resource):
        r = os.path.join(ResourcesConfiguration.getStaticResources(), "ui", resource)
        if os.path.isfile(r):
            return r

        r = os.path.join(ResourcesConfiguration.getPluginsStaticResources(), "ui", resource)
        if os.path.isfile(r):
            return r

        raise NetzobAbstractViewException(_("Requested file ({0}) was not found.").format(resource))

    def _getObjects(self, objectsList):
        for obj in objectsList:
            setattr(self, obj, self.builder.get_object(obj))
