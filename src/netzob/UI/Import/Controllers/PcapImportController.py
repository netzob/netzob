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
import uuid
import errno
from netzob.UI.NetzobWidgets import NetzobErrorMessage
pygtk.require('2.0')
import logging
import time

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+
import pcapy
import impacket.ImpactDecoder as Decoders
import impacket.ImpactPacket as Packets

#+----------------------------------------------
#| Local Imports
#+----------------------------------------------
from netzob.Common.Type.TypeConvertor import TypeConvertor
from netzob.Import.PcapImport import PcapImport
from netzob.UI.Import.Views.PcapImportView import PcapImportView


#+----------------------------------------------
#| PcapImportController:
#|     GUI for capturing messages imported through a provided PCAP
#+----------------------------------------------
class PcapImportController():

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
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.UI.Import.PcapImportController.py')
        self.model = PcapImport(netzob)
        self.view = PcapImportView()
        self.initCallbacks()

    def initCallbacks(self):
        self.view.butSelectFile.connect("clicked", self.selectFile_cb, self.view.labelFile)
        self.view.butLaunchSniff.connect("clicked", self.launchSniff_cb, self.view.entryScapyFilter, self.view.labelFile)
        self.view.treeviewPackets.connect("cursor-changed", self.packetDetails_cb)
        self.view.butSaveSelectedPackets.connect("clicked", self.savePackets_cb, self.view.treeviewPackets)

    #+----------------------------------------------
    #| Called when user import a pcap file
    #+----------------------------------------------
    def selectFile_cb(self, button, label):
        chooser = gtk.FileChooserDialog(title=None, action=gtk.FILE_CHOOSER_ACTION_OPEN,
                                        buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        res = chooser.run()
        if res == gtk.RESPONSE_OK:
            label.set_text(chooser.get_filename())
        chooser.destroy()

    #+----------------------------------------------
    #| Called when launching sniffing process
    #+----------------------------------------------
    def launchSniff_cb(self, button, aFilter, label_file):
        self.view.textview.get_buffer().set_text("")

        # retrieve the choosen pcap file
        pcapFile = label_file.get_text()

        self.view.treestore.clear()
        button.set_sensitive(False)
        (errorCode, errorMessage) = self.model.launchSniff(pcapFile, aFilter, self.packetHandlerCallback_cb)

        if errorCode == False:
            button.set_sensitive(True)
            md = gtk.MessageDialog(None,
                                   gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_ERROR,
                                   gtk.BUTTONS_CLOSE, errorMessage)
            md.run()
            md.destroy()
            return

        button.set_sensitive(True)

    def packetHandlerCallback_cb(self, dataRow):
        self.view.treestore.append(None, dataRow)

    #+----------------------------------------------
    #| Called when user select a list of packet
    #+----------------------------------------------
    def savePackets_cb(self, button, treeview):
        currentProject = self.netzob.getCurrentProject()
        packetsToSave = []
        selection = treeview.get_selection()
        (model, paths) = selection.get_selected_rows()
        for path in paths:
            iter = model.get_iter(path)
            if(model.iter_is_valid(iter)):
                packetID = model.get_value(iter, 0)
                proto = model.get_value(iter, 1)
                timestamp = str(model.get_value(iter, 6))
                packetPayload = self.model.messages[packetID - 1]
                packetsToSave.append((packetPayload, proto, timestamp))

        # We ask the confirmation
        md = gtk.MessageDialog(None,
                               gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_QUESTION,
                               gtk.BUTTONS_OK_CANCEL, _("Are you sure to import the {0} selected packets in project {0}.").format(str(len(packetsToSave)), currentProject.getName()))

#        md.add_button(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
        resp = md.run()
        md.destroy()

        if resp == gtk.RESPONSE_OK:
            messages = self.model.buildMessages(packetsToSave)
            self.model.saveMessagesInProject(self.netzob.getCurrentWorkspace(), currentProject, messages, False)
        self.view.dialog.destroy()

        # We update the gui
        self.netzob.update()

    #+----------------------------------------------
    #| Called when user select a packet for details
    #+----------------------------------------------
    def packetDetails_cb(self, treeview):
        (model, paths) = treeview.get_selection().get_selected_rows()
        decoder = Decoders.EthDecoder()
        for path in paths[:1]:
            iter = model.get_iter(path)
            if(model.iter_is_valid(iter)):
                packetID = model.get_value(iter, 0)
                payload = self.model.messages[packetID - 1]
                content = str(decoder.decode(payload))
                self.view.textview.get_buffer().insert_with_tags_by_name(self.view.textview.get_buffer().get_start_iter(), content, "normalTag")

    #+----------------------------------------------
    #| GETTERS
    #+----------------------------------------------
    def getPanel(self):
        return self.view
