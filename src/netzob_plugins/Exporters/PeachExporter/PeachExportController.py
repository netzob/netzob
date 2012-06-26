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

#+----------------------------------------------
#| Global Imports
#+----------------------------------------------
from gettext import gettext as _
import gtk
import pygtk
import logging
pygtk.require('2.0')

#+----------------------------------------------
#| Local Imports
#+----------------------------------------------
from netzob_plugins.Exporters.PeachExporter.PeachExportView import PeachExportView
from netzob_plugins.Exporters.PeachExporter.PeachExport import PeachExport


#+----------------------------------------------
#| PeachExportController:
#|     GUI for exporting results in Peach pit xml
#+----------------------------------------------
class PeachExportController:

    #+----------------------------------------------
    #| Called when user select a new trace
    #+----------------------------------------------
    def new(self):
        pass

    def update(self):
        self.view.symbolTreeview.get_model().clear()

        # Append an "Entire project" leaf to the tree view.
        iter = self.view.symbolTreeview.get_model().append(None, ["-1", "{0} [{1}, {2}]".format(_("Entire project"), str(len(self.netzob.getCurrentProject().getVocabulary().getSymbols())), str(len(self.netzob.getCurrentProject().getVocabulary().getMessages()))), "0", '#000000', '#DEEEF0'])

        for symbol in self.netzob.getCurrentProject().getVocabulary().getSymbols():
            iter = self.view.symbolTreeview.get_model().append(None, ["{0}".format(symbol.getID()), "{0} [{1}]".format(symbol.getName(), str(len(symbol.getMessages()))), "{0}".format(symbol.getScore()), '#000000', '#DEEEF0'])

    def clear(self):
        pass

    def kill(self):
        pass

    #+----------------------------------------------
    #| Constructor:
    #| @param netzob: the main netzob object
    #+----------------------------------------------
    def __init__(self, netzob):
        self.netzob = netzob
        self.model = PeachExport(netzob)
        self.view = PeachExportView()
        self.initCallbacks()
        self.update()

    def initCallbacks(self):
        self.view.symbolTreeview.connect("cursor-changed", self.symbolSelected_cb)

    def symbolSelected_cb(self, treeview):
        (model, iter) = treeview.get_selection().get_selected()
        if(iter):
            if(model.iter_is_valid(iter)):
                symbolID = model.get_value(iter, 0)
                self.showXMLDefinition(symbolID)

    def showXMLDefinition(self, symbolID):

        # Special case "entire project"
        if symbolID == "-1":
            xmlDefinition = self.model.getPeachDefinition(0, True)

        # Usual case with usual symbolID
        else:
            xmlDefinition = self.model.getPeachDefinition(symbolID, False)

        if xmlDefinition != None:
            self.view.textarea.get_buffer().set_text("")
            self.view.textarea.get_buffer().insert_with_tags_by_name(self.view.textarea.get_buffer().get_start_iter(), xmlDefinition, "normalTag")
        else:
            self.view.textarea.get_buffer().set_text(_("No XML definition found"))

    #+----------------------------------------------
    #| GETTERS
    #+----------------------------------------------
    def getPanel(self):
        return self.view
