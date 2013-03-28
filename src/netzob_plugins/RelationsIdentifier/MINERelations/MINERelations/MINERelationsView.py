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
import os

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+
from gi.repository import Gtk

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Plugins.RelationsIdentifier.AbstractRelationsIdentifierView import AbstractRelationsIdentifierView


class MINERelationsView(AbstractRelationsIdentifierView):
    """MINERelationsView:
            GUI for computing the MINE relations
    """

    GLADE_FILENAME = "MINERelationsDialog.glade"

    def __init__(self, controller, plugin, selectedSymbols):
        """Constructor of MINEExporterView"""

        super(MINERelationsView, self).__init__(plugin, controller)

        # Import and add configuration widget
        self.builderConfWidget = Gtk.Builder()
        gladePath = os.path.join(self.getPlugin().getPluginStaticResourcesPath(), "ui", MINERelationsView.GLADE_FILENAME)
        self.builderConfWidget.add_from_file(gladePath)

        self._getObjects(self.builderConfWidget, ["dialog",
                                                  "warningImage",
                                                  "errorLabel",
                                                  "cancelButton",
                                                  "startButton",
                                                  "javaFileChooserButton",
                                                  "MINEFileChooserButton",
                                                  "interSymbolCheckButton",
                                                  "selectedSymbolsListStore"])
        self.builderConfWidget.connect_signals(self.controller)

        for selectedSymbol in selectedSymbols:
            self.selectedSymbolsListStore.append([selectedSymbol.getName()])

        if len(selectedSymbols) == 0:
            self.showError(_("No symbols have been selected"))
            self.startButton.set_sensitive(False)

    def getJavaPath(self):
        """Returns the provided java path"""
        return self.javaFileChooserButton.get_filename()

    def getMINEPath(self):
        """Returns the path to the Jar MINE file"""
        return self.MINEFileChooserButton.get_filename()

    def isInterSymbolRelationsRequested(self):
        """Returns True if the user checked the inter symbols relations identifications"""
        return self.interSymbolCheckButton.get_active()

    def showError(self, message):
        if message is not None:
            self.errorLabel.set_label(message)
            self.errorLabel.set_visible(True)
            self.warningImage.set_visible(True)
        else:
            self.errorLabel.set_visible(False)
            self.warningImage.set_visible(False)

    def show(self):
        self.dialog.show()

    def destroy(self):
        self.dialog.destroy()

    def _getObjects(self, builder, objectsList):
        for obj in objectsList:
            setattr(self, obj, builder.get_object(obj))
