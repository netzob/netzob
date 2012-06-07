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
import gtk
import pygtk
import pango
import logging
pygtk.require('2.0')

class WorkspaceSelector(object):
    """Workspace selection dialog"""

    def __init__(self):
            # Set up GTK Window
        self.dialog = gtk.Dialog(title="Select Workspace", flags=0,
            buttons=None)
        self.dialog.set_size_request(600, 220)
        self.dialog.connect("destroy", self.destroy)

        # Instructions text view
        instrTextView = gtk.TextView()
        instrTextView.set_editable(False)
        instrTextView.set_cursor_visible(False)
        instrTextView.set_left_margin(10)
        textBuffer = instrTextView.get_buffer()
        bold_tag = textBuffer.create_tag("bold", weight=pango.WEIGHT_BOLD)
        pos = textBuffer.get_end_iter()
        textBuffer.insert_with_tags(pos,
                "Select a workspace\n\n", bold_tag)
        pos = textBuffer.get_end_iter()
        textBuffer.insert_with_tags(pos,
                "Netzob stores your projects in a folder called a workspace.\n")
        pos = textBuffer.get_end_iter()
        textBuffer.insert_with_tags(pos,
                "Choose a workspace folder to use.")
        #textBuffer.insert_with_tags(pos,
        #        "Choose a workspace folder to use for this session.")

        # Input Box
        inputBox = gtk.HBox(spacing=10)
        workLabel = gtk.Label()
        workLabel.set_text("Workspace: ")
        self.workEntry = gtk.Entry()
        self.workEntry.connect("changed", self.entryChanged)
        workButton = gtk.Button("Browse...")
        workButton.connect("clicked", self.openBrowseDialog)
        inputBox.pack_start(workLabel, expand=False)
        inputBox.pack_start(self.workEntry)
        inputBox.pack_start(workButton, expand=False)
        inputBox.set_border_width(10)

        # Default checkbox
        #self.defaultCheck = gtk.CheckButton(
        #        "Use this as default and do not ask again")
        #self.defaultCheck.set_active(True)
        #self.defaultCheck.set_border_width(10)

        # Buttons
        okButton = gtk.Button(stock=gtk.STOCK_OK)
        okButton.connect("clicked", self.destroy)
        cancelButton = gtk.Button(stock=gtk.STOCK_CANCEL)
        cancelButton.connect("clicked", self.cancel)
        self.dialog.action_area.pack_end(cancelButton, expand=False)
        self.dialog.action_area.pack_end(okButton, expand=False)
        self.dialog.action_area.set_border_width(10)

        # Global VBox
        self.dialog.vbox.pack_start(instrTextView, expand=False)
        self.dialog.vbox.pack_start(inputBox, expand=False)
        self.dialog.vbox.pack_start(gtk.Alignment(0, 1, 0, 0), expand=True)
        #self.dialog.vbox.pack_start(self.defaultCheck, expand=False)
        self.dialog.show_all()

        self._selectedWorkspace = None

    def run(self):
        gtk.main()

    @property
    def selectedWorkspace(self):
        return self._selectedWorkspace;

    #@property
    #def makeDefault(self):
    #    return self.defaultCheck.get_active()

    def openBrowseDialog(self, widget, data=None):
        chooser = gtk.FileChooserDialog(title="Select the workspace",
                    action=gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
                    buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                             gtk.STOCK_OPEN, gtk.RESPONSE_OK))

        res = chooser.run()
        if res == gtk.RESPONSE_OK:
            self.workEntry.set_text(chooser.get_filename())
        chooser.destroy()

    def entryChanged(self, widget, data=None):
        self._selectedWorkspace = self.workEntry.get_text()

    def cancel(self, widget, data=None):
        self._selectedWorkspace = None
        self.dialog.destroy()
        gtk.main_quit()

    def destroy(self, widget, data=None):
        self.dialog.destroy()
        gtk.main_quit()
