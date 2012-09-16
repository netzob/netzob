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

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.Plugins.AbstractPluginView import AbstractPluginView


class AbstractCapturerView(AbstractPluginView):
    GLADE_FILENAME = "abstractCapturerView.glade"

    def __init__(self, plugin, controller):
        super(AbstractCapturerView, self).__init__(plugin, controller)
        self._builder = Gtk.Builder()
        gladeFilePath = os.path.join(
            self.getPlugin().getNetzobStaticResourcesPath(),
            "ui", "capturer", AbstractCapturerView.GLADE_FILENAME)

        self._builder.add_from_file(gladeFilePath)
        self._getObjects(self._builder, ["dialog", "openFileEntry",
                                         "listTreeView", "detailTextView", "cancelButton", "warnAlign",
                                         "warnLabel", "displayCountLabel", "selectCountLabel", "importButton",
                                         "globalBox", "importProgressBar"])
        # Change packet details textview font
        monoFontDesc = Pango.FontDescription("monospace")
        self.detailTextView.modify_font(monoFontDesc)
        self._builder.connect_signals(self.getController())
        self.cancelButton.connect_object("clicked", Gtk.Widget.destroy,
                                         self.dialog)

    def setConfigurationWidget(self, widget):
        self.globalBox.pack_start(widget, False, False, 0)
        self.globalBox.reorder_child(widget, 1)
        widget.show()

    def setDialogTitle(self, title):
        self.dialog.set_title(title)

    def _getObjects(self, builder, objectsList):
        for object in objectsList:
            setattr(self, object, builder.get_object(object))

    def run(self):
        self.dialog.show_all()
        self.hideWarning()

    def showWarning(self, text):
        self.warnLabel.set_text(text)
        self.warnAlign.show_all()

    def hideWarning(self):
        self.warnAlign.hide()

    def clearPacketView(self):
        self.listListStore.clear()
        self.detailTextView.get_buffer().set_text("")

    def updateCounters(self, displayedPackets, selectedPackets):
        if selectedPackets == 0:
            self.importButton.set_sensitive(False)
        else:
            self.importButton.set_sensitive(True)

        self.displayCountLabel.set_text(str(displayedPackets))
        self.selectCountLabel.set_text(str(selectedPackets))
