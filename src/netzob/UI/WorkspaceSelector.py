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
#| Global Imports
#+---------------------------------------------------------------------------+
from gettext import gettext as _
from gi.repository import Gtk
import gi
from gi.repository import Pango
import logging
gi.require_version('Gtk', '3.0')


class WorkspaceSelector(object):
    """Workspace selection dialog"""

    def __init__(self):
            # Set up GTK Window
        self.dialog = Gtk.Dialog(title=_("Select Workspace"), flags=0,
                                 buttons=None)
        self.dialog.set_size_request(600, 220)
        self.dialog.connect("destroy", self.destroy)

        # Instructions text view
        instrTextView = Gtk.TextView()
        instrTextView.set_editable(False)
        instrTextView.set_cursor_visible(False)
        instrTextView.set_left_margin(10)
        textBuffer = instrTextView.get_buffer()
        bold_tag = textBuffer.create_tag("bold", weight=Pango.Weight.BOLD)
        pos = textBuffer.get_end_iter()
        textBuffer.insert_with_tags(pos,
                                    _("Select a workspace\n\n"), bold_tag)
        pos = textBuffer.get_end_iter()
        textBuffer.insert_with_tags(pos,
                                    _("Netzob stores your projects in a folder called a workspace.\n"))
        pos = textBuffer.get_end_iter()
        textBuffer.insert_with_tags(pos,
                                    _("Choose a workspace folder to use."))

        # Input Box
        inputBox = Gtk.HBox(spacing=10)
        workLabel = Gtk.Label()
        workLabel.set_text(_("Workspace: "))
        self.workEntry = Gtk.Entry()
        self.workEntry.set_editable(False)
        self.workEntry.connect("changed", self.entryChanged)
        self.workEntry.connect("focus-in-event", self.entryFocused)
        self.workEntry.set_placeholder_text(_("Path"))
        self.browseButton = Gtk.Button(_("Browse"))
        self.browseButton.connect("clicked", self.openBrowseDialog)
        self.browseButton.set_can_default(True)

        inputBox.pack_start(workLabel, False, True, 0)
        inputBox.pack_start(self.workEntry, True, True, 0)
        inputBox.pack_start(self.browseButton, False, True, 0)
        inputBox.set_border_width(10)

        # Buttons
        self.okButton = Gtk.Button(stock=Gtk.STOCK_OK)
        self.okButton.connect("clicked", self.destroy)
        cancelButton = Gtk.Button(stock=Gtk.STOCK_CANCEL)
        cancelButton.connect("clicked", self.cancel)
        self.dialog.action_area.pack_end(cancelButton, False, True, 0)
        self.dialog.action_area.pack_end(self.okButton, False, True, 0)
        self.dialog.action_area.set_border_width(10)

        # Global VBox
        self.dialog.vbox.pack_start(instrTextView, False, True, 0)
        self.dialog.vbox.pack_start(inputBox, False, True, 0)
        self.dialog.vbox.pack_start(Gtk.Alignment.new(0, 1, 0, 0), True, True, 0)
        self.dialog.show_all()

        self._selectedWorkspace = None
        self.browseButton.grab_default()

    def run(self):
        Gtk.main()

    @property
    def selectedWorkspace(self):
        return self._selectedWorkspace

    def openBrowseDialog(self, widget, data=None):
        chooser = Gtk.FileChooserDialog(title=_("Select the workspace"),
                                        parent=self.dialog,
                                        action=Gtk.FileChooserAction.SELECT_FOLDER,
                                        buttons=(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                                 Gtk.STOCK_OPEN, Gtk.ResponseType.OK))

        if self.selectedWorkspace is not None:
            chooser.set_filename(self.selectedWorkspace)

        res = chooser.run()
        if res == Gtk.ResponseType.OK:
            self.workEntry.set_text(chooser.get_filename())

        if self.workEntry.get_text() == "":
            self.browseButton.grab_focus()
        else:
            self.okButton.grab_focus()

        chooser.destroy()

    def entryFocused(self, widget, data=None):
        self.openBrowseDialog(widget)

    def entryChanged(self, widget, data=None):
        textEntry = self.workEntry.get_text()
        if textEntry != "":
            self._selectedWorkspace = self.workEntry.get_text()
        else:
            self._selectedWorkspace = None

    def cancel(self, widget, data=None):
        self._selectedWorkspace = None
        self.dialog.destroy()
        Gtk.main_quit()

    def destroy(self, widget, data=None):
        self.dialog.destroy()
        Gtk.main_quit()
