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
import os

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+
from gi.repository import Gtk, Pango
from netzob.Common.Plugins.Importers.AbstractImporterView import AbstractImporterView


class AbstractFileImporterView(AbstractImporterView):

    SOURCE_WIDGET_GLADE_FILENAME = "fileListSourceWidget.glade"

    def __init__(self, plugin, controller):
        super(AbstractFileImporterView, self).__init__(plugin, controller)
        sourceWidgetGladeFilePath = os.path.join(
            self.getPlugin().getNetzobStaticResourcesPath(),
            "ui", "import", AbstractFileImporterView.SOURCE_WIDGET_GLADE_FILENAME)
        sourceWidgetBuilder = Gtk.Builder()
        sourceWidgetBuilder.add_from_file(sourceWidgetGladeFilePath)
        self._getObjects(sourceWidgetBuilder, ["fileListLabel", "fileListExpander"])
        self.setSourceConfigurationWidget(self.fileListExpander)

    def setSourceFiles(self, filePathList):
        self.fileListLabel.set_text("\n".join(filePathList))
        if len(filePathList) <= 5:
            self.fileListExpander.set_expanded(True)
