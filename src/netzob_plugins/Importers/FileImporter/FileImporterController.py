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
from gi.repository import Gtk
import gi
gi.require_version('Gtk', '3.0')
import logging
import os
from gettext import gettext as _

#+----------------------------------------------
#| Local Imports
#+----------------------------------------------
from netzob.Common.Type.TypeConvertor import TypeConvertor
from netzob_plugins.Importers.FileImporter.FileImporter import FileImporter
from netzob_plugins.Importers.FileImporter.FileImporterView import FileImporterView

#+----------------------------------------------
#| FileImporter:
#|     GUI for capturing messages
#+----------------------------------------------
class FileImporterController(object):

    def new(self):
        pass

    def update(self):
        pass

    def clear(self):
        pass

    def kill(self):
        pass

    #+----------------------------------------------
    #| Constructor:
    #+----------------------------------------------
    def __init__(self, netzob):
        self.netzob = netzob
        self.log = logging.getLogger('netzob.Capturing.File.py')
        self.model = FileImporter()
        self.view = FileImporterView()
        self.initCallbacks()

    def initCallbacks(self):
        self.view.butSelectFiles.connect("clicked", self.selectFiles_cb)
        self.view.entrySeparator.connect("activate", self.applySeparator_cb)
        self.view.lineView.connect('button-press-event', self.buttonPressOnMessage_cb)
        self.view.butValidateMessages.connect("clicked", self.importFile_cb)

    def buttonPressOnMessage_cb(self, treeview, event):
        x = int(event.x)
        y = int(event.y)

        info = treeview.get_path_at_pos(x, y)
        idMessage = None
        if info is not None:
            path = info[0]
            iter = treeview.get_model().get_iter(path)
            idMessage = str(treeview.get_model().get_value(iter, 0))
        if idMessage == None:
            return

        # Search for the selected message
        selectedMessage = self.model.getMessageByID(idMessage)
        if selectedMessage == None:
            self.log.warn(_("Impossible to retrieve the message the user clicked on. Hum?"))
            return

        self.displayMessage(selectedMessage)

    #+----------------------------------------------
    #| Called when user select a list of file
    #+----------------------------------------------
    def importFile_cb(self, button):
        # We ask the confirmation
        dialog = Gtk.MessageDialog(None,
                                   Gtk.DialogFlags.DESTROY_WITH_PARENT,
                                   Gtk.MessageType.QUESTION,
                                   Gtk.ButtonsType.OK_CANCEL,
                                   _("Are you sure to import the {0} computed messages in project {1}?").format(str(len(self.model.messages)), self.netzob.getCurrentProject().getName()))

        # Checkbox for session
        vbox = Gtk.VBox()
        vbox.show()
        hbox = Gtk.HBox()
        hbox.show()
        vbox.pack_start(hbox, True, True, 0)
        isSession = Gtk.CheckButton(_("Check if this trace is a session"))
        isSession.set_active(False)
        isSession.show()
#        hbox.pack_start(isSession, True, True, 0)

        dialog.vbox.pack_end(vbox, True, True, 0)
        resp = dialog.run()
        dialog.destroy()

        if resp == Gtk.ResponseType.OK:
            self.model.saveMessages()
            self.view.dialog.destroy()
            # We update the gui
            self.netzob.update()

    #+----------------------------------------------
    #| Called when user import files
    #+----------------------------------------------
    def selectFiles_cb(self, button):
        aFile = ""
        chooser = Gtk.FileChooserDialog(title=_("Select one or multiple file"), action=Gtk.FileChooserAction.OPEN,
                                        buttons=(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
        chooser.set_select_multiple(True)

        self.model.filesToBeImported = []

        # Computes the selected file(s)
        res = chooser.run()
        if res == Gtk.ResponseType.OK:
            for filename in chooser.get_filenames():
                filename = unicode(filename, "utf-8")
                if filename != None and filename != "" and os.path.isfile(filename):
                    self.model.filesToBeImported.append(filename)
        chooser.destroy()

        # We update the label with the list of the selected files
        self.view.entryFilepath.set_text(";".join(self.model.filesToBeImported))

        # Retrieve the selected files
        self.model.retrieveMessagesFromFiles()
        self.displayMessageList()

    def applySeparator_cb(self, widget):
        entry_text = widget.get_text()
        lineSeparator = entry_text
        self.model.applySeparatorOnFiles(lineSeparator)
        self.displayMessageList()

    def displayMessageList(self):
        self.view.lineView.get_model().clear()
        for message in self.model.messages:
            self.view.lineView.get_model().append(None, [str(message.getID()), str(message.getData())])
        self.view.textview.get_buffer().delete(self.view.textview.get_buffer().get_start_iter(), self.view.textview.get_buffer().get_end_iter())

    def displayMessage(self, message):
        # Clean the hexdump view
        self.view.textview.get_buffer().delete(self.view.textview.get_buffer().get_start_iter(), self.view.textview.get_buffer().get_end_iter())
        # Fecth the content of the message to display
        hexContent = TypeConvertor.hexdump(TypeConvertor.netzobRawToPythonRaw(message.getData()))
        # Update the hexdump
        self.view.textview.get_buffer().insert_with_tags_by_name(self.view.textview.get_buffer().get_start_iter(), hexContent, "normalTag")

    #+----------------------------------------------
    #| GETTERS
    #+----------------------------------------------
    def getPanel(self):
        return self.view
