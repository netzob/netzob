# -*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|          01001110 01100101 01110100 01111010 01101111 01100010            |
#|                                                                           |
#|               Netzob : Inferring communication protocols                  |
#+---------------------------------------------------------------------------+
#| Copyright (C) 2011 AMOSSYS                                                |
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
import zlib
import uuid

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+
from gi.repository import Gtk

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Plugins.RelationsIdentifier.AbstractRelationsIdentifierController import AbstractRelationsIdentifierController
from MINERelationsView import MINERelationsView
from MINERelations import MINERelations
from netzob.Common.Type.TypeConvertor import TypeConvertor
from RelationsMakerController import RelationsMakerController


class MINERelationsController(AbstractRelationsIdentifierController):
    """MINERelationsController:
            A controller liking the MINE exporter and its view in the netzob GUI.
    """

    def __init__(self, netzob, plugin):
        """Constructor of MINERelationsController:

                @type netzob: MINEExporterPlugin
                @param netzob: the plugin instance
        """
        self.netzob = netzob
        self.plugin = plugin
        self.selectedSymbols = self.getVocabularyController().symbolController.getCheckedSymbolList()
        self.model = MINERelations(netzob)
        self.view = MINERelationsView(self, plugin, self.selectedSymbols)
        super(MINERelationsController, self).__init__(netzob, plugin, self.view)

    def run(self):
        """run:
            Show the plugin view.
        """
        self.update()

    def update(self):
        self.view.show()

    def getPanel(self):
        """getPanel:

                @rtype: netzob_plugins.
                @return: the plugin view.
        """
        return self.view

    def cancelButton_clicked_cb(self, widget):
        self.view.destroy()

    def startButton_clicked_cb(self, widget):
        """startButton_clicked_cb:
            Callback executed when the user clicks on the MINERelations button in main menu"""

        results = self.model.findCorrelationsInSymbols(self.selectedSymbols)
        self.view.destroy()

        # Start the relation maker controller
        controller = RelationsMakerController(self.getPlugin(), self, results)
        controller.run()
