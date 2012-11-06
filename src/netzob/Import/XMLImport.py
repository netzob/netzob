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
from gi.repository import Gtk
import gi
import uuid
import datetime
from bitarray import bitarray
gi.require_version('Gtk', '3.0')
import logging
import os
import random
from lxml.etree import ElementTree
from lxml import etree

#+----------------------------------------------
#| Local Imports
#+----------------------------------------------
from netzob.Common.Type.TypeConvertor import TypeConvertor
from netzob.Common.Models.Factories.AbstractMessageFactory import AbstractMessageFactory
from netzob.Common.ProjectConfiguration import ProjectConfiguration
from netzob.Common.EnvironmentalDependencies import EnvironmentalDependencies
from netzob.Import.AbstractImporter import AbstractImporter
from netzob.Common import Project
from netzob.Common.Workspace import Workspace


#+----------------------------------------------
#| XMLImport:
#|     GUI for importing XML traces
#+----------------------------------------------
class XMLImport(AbstractImporter):

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
        AbstractImporter.__init__(self, "XML IMPORT",
                                  netzob.getCurrentWorkspace(), netzob.getCurrentProject())
        self.netzob = netzob

        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Import.XMLImport.py')
        self.messages = []

        self.init()

        self.dialog = Gtk.Dialog(title=("Import XML file"), flags=0, buttons=None)
        self.dialog.show()
        self.dialog.vbox.pack_start(self.getPanel(), True, True, 0)
        self.dialog.set_size_request(1000, 600)

    def init(self):
        # create the environmental dependancy object
        self.envDeps = EnvironmentalDependencies()

        # Default line separator is <CR>
        self.fileName = ""

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Main panel
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        self.panel = Gtk.Table(rows=10, columns=8, homogeneous=True)
        self.panel.show()

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Select a file
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        but = Gtk.Button(_("Select file(s)"))
        but.show()
        entry_filepath = Gtk.Entry()
#        entry_filepath.set_width_chars(50)
        entry_filepath.set_text("")
        entry_filepath.show()
        but.connect("clicked", self.selectFiles, entry_filepath)
        self.panel.attach(but, 0, 2, 0, 1, xoptions=Gtk.AttachOptions.FILL | Gtk.AttachOptions.EXPAND, yoptions=Gtk.AttachOptions.FILL | Gtk.AttachOptions.EXPAND, xpadding=5, ypadding=5)

        self.panel.attach(entry_filepath, 2, 6, 0, 1, xoptions=Gtk.AttachOptions.FILL | Gtk.AttachOptions.EXPAND, yoptions=Gtk.AttachOptions.FILL | Gtk.AttachOptions.EXPAND, xpadding=5, ypadding=5)

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Extracted data
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        scroll2 = Gtk.ScrolledWindow()
        self.lineView = Gtk.TreeView(Gtk.TreeStore(str, str, str))  # id message, type, content
        self.lineView.get_selection().set_mode(Gtk.SelectionMode.SINGLE)
        #self.lineView.connect('button-press-event', self.button_press_on_message)
        cell = Gtk.CellRendererText()
        # Col file descriptor
        column = Gtk.TreeViewColumn(_("Message ID"))
        column.pack_start(cell, True)
        column.add_attribute(cell, "text", 0)
        self.lineView.append_column(column)
        column = Gtk.TreeViewColumn(_("Type"))
        column.pack_start(cell, True)
        column.add_attribute(cell, "text", 1)
        self.lineView.append_column(column)
        column = Gtk.TreeViewColumn(_("Content"))
        column.pack_start(cell, True)
        column.add_attribute(cell, "text", 2)
        self.lineView.append_column(column)
        self.lineView.show()

        scroll2.add(self.lineView)
        scroll2.show()
        scroll2.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.panel.attach(scroll2, 0, 6, 1, 10, xoptions=Gtk.AttachOptions.FILL, yoptions=Gtk.AttachOptions.FILL | Gtk.AttachOptions.EXPAND, xpadding=5, ypadding=5)

        # Button select packets for further analysis
        but = Gtk.Button(label=_("Import"))
        but.show()
        but.connect("clicked", self.import_file)
        self.panel.attach(but, 2, 3, 10, 11, xoptions=0, yoptions=0, xpadding=5, ypadding=5)

    def button_press_on_message(self, treeview, event):
        x = int(event.x)
        y = int(event.y)

        info = treeview.get_path_at_pos(x, y)
        idMessage = None
        if info is not None:
            path = info[0]
            iter = treeview.get_model().get_iter(path)
            idMessage = str(treeview.get_model().get_value(iter, 0))

        if idMessage is None:
            return

        # Search for the selected message
        selectedMessage = None
        for message in self.messages:
            if str(message.getID()) == idMessage:
                selectedMessage = message

        if selectedMessage is None:
            self.log.warn("Impossible to retrieve the message the user clicked on. Hum?")
            return

        self.displayMessage(selectedMessage)

    #+----------------------------------------------
    #| Called when user select a list of packet
    #+----------------------------------------------
    def import_file(self, button):
        currentProject = self.netzob.getCurrentProject()

        # We ask the confirmation
        dialog = Gtk.MessageDialog(None,
                                   Gtk.DialogFlags.DESTROY_WITH_PARENT,
                                   Gtk.MessageType.QUESTION,
                                   Gtk.ButtonsType.OK_CANCEL,
                                   _("Are you sure to import the {0} computed messages in project {1}?").format(str(len(self.messages)), currentProject.getName()))

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
            self.saveMessagesInProject(self.netzob.getCurrentWorkspace(), currentProject, self.messages)
            self.dialog.destroy()
            # We update the gui
            self.netzob.update()

    #+----------------------------------------------
    #| Called when user import files
    #+----------------------------------------------
    def selectFiles(self, button, label):
        aFile = ""
        chooser = Gtk.FileChooserDialog(title=_("Select one or multiple file"), action=Gtk.FileChooserAction.OPEN,
                                        buttons=(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
        chooser.set_select_multiple(True)

        self.filesToBeImported = []

        # Computes the selected file(s)
        res = chooser.run()
        if res == Gtk.ResponseType.OK:
            for filename in chooser.get_filenames():
                filename = unicode(filename, "utf-8")
                if filename is not None and filename != "" and os.path.isfile(filename):
                    self.filesToBeImported.append(filename)
        chooser.destroy()

        # We update the label with the list of the selected files
        label.set_text(";".join(self.filesToBeImported))

        # Retrieve the selected files
        self.retrieveMessagesFromFiles()

    #+----------------------------------------------
    #| Retrieve messages from files
    #+----------------------------------------------
    def retrieveMessagesFromFiles(self):
        # We read each file and create one message for each file
        self.messages = []
        self.lineView.get_model().clear()

        for file in self.filesToBeImported:

            from netzob.Common.ResourcesConfiguration import ResourcesConfiguration
            xmlSchemaPath = os.path.join(ResourcesConfiguration.getStaticResources(), "xsds/0.1/common.xsd")
            # If we find a version which validates the XML, we parse with the associated function
            if not Workspace.isSchemaValidateXML(xmlSchemaPath, file):
                logging.error("The specified XML file {0} is not valid according to the XSD ({1}).".format(str(file), str(xmlSchemaPath)))
            else:
                logging.debug("XML file valid according to the XSD schema")

                # Parse the XML Document as 0.1 version
                tree = ElementTree()
                tree.parse(file)
                xmlFile = tree.getroot()

                for xmlMessage in xmlFile.findall("{" + Project.COMMON_NAMESPACE + "}message"):
                    message = AbstractMessageFactory.loadFromXML(xmlMessage, Project.COMMON_NAMESPACE, "0.1")
                    logging.debug("XML String data: {0}".format(message.getStringData()))
                    self.messages.append(message)
                    self.lineView.get_model().append(None, [str(message.getID()), message.getType(), message.getStringData()])

    #+----------------------------------------------
    #| GETTERS
    #+----------------------------------------------
    def getPanel(self):
        return self.panel
