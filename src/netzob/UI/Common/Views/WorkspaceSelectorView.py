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
from gi.repository import Gtk, Gdk, Pango
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import GObject

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.ResourcesConfiguration import ResourcesConfiguration


class WorkspaceSelectorView(object):

    def __init__(self, controller, parent=None):
        self.builder = Gtk.Builder()
        self.builder.add_from_file(os.path.join(ResourcesConfiguration.getStaticResources(),
                                                "ui",
                                                "workspaceSelectorDialog.glade"))
        self._getObjects(self.builder, ["workspaceSelectorDialog", "pathEntry", "browseButton", "imageLabel", "errorTextBuffer", "errorTextView", "cancelButton", "applyButton"])
        self.controller = controller
        self.builder.connect_signals(self.controller)

        # create a bold tag for the error buffer
        self.errorBoldTag = self.errorTextBuffer.create_tag("bold", weight=Pango.Weight.BOLD)

        # Hide error labels and images
        self.setError(None)

    def setError(self, message):
        """Set the error message and so its visibility
        with its attached icon"""

        if message is None:
            self.imageLabel.hide()
            self.errorTextBuffer.delete(self.errorTextBuffer.get_start_iter(), self.errorTextBuffer.get_end_iter())
            self.errorTextView.hide()
        else:
            self.imageLabel.show()
            self.errorTextBuffer.delete(self.errorTextBuffer.get_start_iter(), self.errorTextBuffer.get_end_iter())
            requestedWorkspace = self.controller.getSelectedWorkspace()
            if requestedWorkspace is not None:
                self.errorTextBuffer.insert_with_tags(self.errorTextBuffer.get_start_iter(), "{0}:\n".format(requestedWorkspace), self.errorBoldTag)
            self.errorTextBuffer.insert(self.errorTextBuffer.get_end_iter(), message)
            self.errorTextView.show()

    def openBrowseDialog(self, currentSelectedWorkspace=None):
        """Open a dialog which allows a user to browse
        and select the directory which will host the current workspace"""
        chooser = Gtk.FileChooserDialog(title=_("Select the workspace"),
                                        parent=self.workspaceSelectorDialog,
                                        action=Gtk.FileChooserAction.SELECT_FOLDER,
                                        buttons=(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                                 Gtk.STOCK_OPEN, Gtk.ResponseType.OK))

        if currentSelectedWorkspace is not None:
            chooser.set_filename(currentSelectedWorkspace)

        res = chooser.run()
        if res == Gtk.ResponseType.OK:
            self.pathEntry.set_text(chooser.get_filename())

        if self.pathEntry.get_text() == "":
            self.browseButton.grab_focus()
        else:
            self.applyButton.grab_focus()

        chooser.destroy()

    def _getObjects(self, builder, objectsList):
        for obj in objectsList:
            setattr(self, obj, builder.get_object(obj))

    def run(self):
        self.workspaceSelectorDialog.show_all()

    def destroy(self):
        self.workspaceSelectorDialog.destroy()
