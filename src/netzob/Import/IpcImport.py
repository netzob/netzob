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
import gtk
import gobject
import re
import pygtk
pygtk.require('2.0')
import logging
import threading
import os
import time
from ptrace.linux_proc import readProcesses, readProcessCmdline
import subprocess

#+----------------------------------------------
#| Local Imports
#+----------------------------------------------
from netzob.Common.Models.IPCMessage import IPCMessage
from netzob.Common.Models.Factories.IPCMessageFactory import IPCMessageFactory
from netzob.Import.AbstractImporter import AbstractImporter


#+----------------------------------------------
#| IPpc:
#|     ensures the capture of informations through IPC proxing
#+----------------------------------------------
class IpcImport(AbstractImporter):

    def new(self):
        pass

    def update(self):
        pass

    def clear(self):
        pass

    def kill(self):
        if self.stracePid != None and self.stracePid.poll() != None:
            self.stracePid.kill()
        if self.aSniffThread != None and self.aSniffThread.isAlive():
            self.aSniffThread._Thread__stop()

    #+----------------------------------------------
    #| Constructor:
    #+----------------------------------------------
    def __init__(self, zob):
        AbstractImporter.__init__(self, "IPC IMPORT")
        self.zob = zob

        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Capturing.ipc.py')

        self.packets = []
        self.init()

        self.dialog = gtk.Dialog(title="Capture IPC flow", flags=0, buttons=None)
        self.dialog.show()
        self.dialog.vbox.pack_start(self.getPanel(), True, True, 0)
        self.dialog.set_size_request(900, 700)

    def init(self):
        self.pid = None
        self.stracePid = None
        self.aSniffThread = None
        self.doSniff = False
        self.selected_fds = set()
        self.sniffOption = None

        # Network Capturing Panel
        self.panel = gtk.Table(rows=6, columns=4, homogeneous=False)
        self.panel.show()

        # Processfilter
        but = gtk.Button("Update processes list")
        but.show()
        but.connect("clicked", self.updateProcessList_cb)
        self.processStore = gtk.combo_box_entry_new_text()
        self.processStore.show()
        self.processStore.set_size_request(300, -1)
        self.processStore.set_model(gtk.ListStore(str))
        self.panel.attach(but, 0, 1, 0, 1, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        self.panel.attach(self.processStore, 1, 2, 0, 1, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        # FD filter
        hbox = gtk.HBox(False, spacing=10)
        hbox.show()
        self.filter1 = gtk.CheckButton("File system")
        self.filter2 = gtk.CheckButton("Network")
        self.filter3 = gtk.CheckButton("Interprocess")
        self.filter1.set_active(True)
        self.filter2.set_active(True)
        self.filter3.set_active(True)
        self.filter1.set_sensitive(False)
        self.filter2.set_sensitive(False)
        self.filter3.set_sensitive(False)
        self.filter1.show()
        self.filter2.show()
        self.filter3.show()
        hbox.pack_start(self.filter1, False, False, 0)
        hbox.pack_start(self.filter2, False, False, 0)
        hbox.pack_start(self.filter3, False, False, 0)
        self.butUpdateFlows = gtk.Button("Update flows")
        self.butUpdateFlows.show()
        self.butUpdateFlows.set_sensitive(False)
        self.butUpdateFlows.connect("clicked", self.processSelected_cb)
        hbox.pack_start(self.butUpdateFlows, False, False, 0)
        self.panel.attach(hbox, 0, 2, 1, 2, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        self.handlerID = self.processStore.connect("changed", self.processSelected_cb)
        self.updateProcessList_cb(None)

        # File descriptor list
        scroll = gtk.ScrolledWindow()
        self.fdTreeview = gtk.TreeView(gtk.TreeStore(str, str, str))  # file descriptor, type, name
        self.fdTreeview.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
        cell = gtk.CellRendererText()
        # Col file descriptor
        column = gtk.TreeViewColumn('FD')
        column.pack_start(cell, True)
        column.set_attributes(cell, text=0)
        self.fdTreeview.append_column(column)
        # Col type
        column = gtk.TreeViewColumn('Type')
        column.pack_start(cell, True)
        column.set_attributes(cell, text=1)
        self.fdTreeview.append_column(column)
        # Col name
        column = gtk.TreeViewColumn('Name')
        column.pack_start(cell, True)
        column.set_attributes(cell, text=2)
        self.fdTreeview.append_column(column)
        self.fdTreeview.show()
        scroll.add(self.fdTreeview)
        scroll.show()
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.panel.attach(scroll, 0, 2, 2, 3, xoptions=gtk.FILL, yoptions=gtk.FILL | gtk.EXPAND, xpadding=5, ypadding=5)

        # Sniff launching button : all sniff
        self.butSniffAll = gtk.Button(label="Sniff on every flows")
        self.butSniffAll.show()
        self.butSniffAll.set_sensitive(False)
        self.panel.attach(self.butSniffAll, 0, 1, 5, 6, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        self.butSniffAll.connect("clicked", self.startSniff_cb, "all")

        # Sniff launching button : FS sniff
        self.butSniffFS = gtk.Button(label="Sniff on FS flows")
        self.butSniffFS.show()
        self.butSniffFS.set_sensitive(False)
        self.panel.attach(self.butSniffFS, 0, 1, 6, 7, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        self.butSniffFS.connect("clicked", self.startSniff_cb, "fs")

        # Sniff launching button : network sniff
        self.butSniffNetwork = gtk.Button(label="Sniff on network flows")
        self.butSniffNetwork.show()
        self.butSniffNetwork.set_sensitive(False)
        self.panel.attach(self.butSniffNetwork, 0, 1, 7, 8, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        self.butSniffNetwork.connect("clicked", self.startSniff_cb, "network")

        # Sniff launching button ; interprocess sniff
        self.butSniffIPC = gtk.Button(label="Sniff on IPC flows")
        self.butSniffIPC.show()
        self.butSniffIPC.set_sensitive(False)
        self.panel.attach(self.butSniffIPC, 0, 1, 8, 9, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        self.butSniffIPC.connect("clicked", self.startSniff_cb, "ipc")

        # Sniff launching button ; filtered sniff
        self.butSniffFiltered = gtk.Button(label="Sniff on selected flows")
        self.butSniffFiltered.show()
        self.butSniffFiltered.set_sensitive(False)
        self.panel.attach(self.butSniffFiltered, 0, 1, 9, 10, xoptions=0, yoptions=0, xpadding=5, ypadding=5)
        self.butSniffFiltered.connect("clicked", self.startSniff_cb, "filtered")

        # Sniff stopping button
        self.butStop = gtk.Button(label="Stop sniffing")
        self.butStop.show()
        self.butStop.set_sensitive(False)
        self.butStop.connect("clicked", self.stopSniff_cb)
        self.panel.attach(self.butStop, 1, 2, 7, 8, xoptions=0, yoptions=0, xpadding=5, ypadding=5)

        self.fdTreeview.connect("cursor-changed", self.fdSelected_cb)

        # Packet list
        scroll = gtk.ScrolledWindow()
        self.pktTreestore = gtk.TreeStore(int, int, str, str, int)  # pktID, fd, direction (read/write), data, timestamp
        treeview = gtk.TreeView(self.pktTreestore)
        treeview.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
        cell = gtk.CellRendererText()
        # Col fd
        column = gtk.TreeViewColumn('FD')
        column.pack_start(cell, True)
        column.set_attributes(cell, text=1)
        treeview.append_column(column)
        # Col direction
        column = gtk.TreeViewColumn('Direction')
        column.pack_start(cell, True)
        column.set_attributes(cell, text=2)
        treeview.append_column(column)
        # Col Data
        column = gtk.TreeViewColumn('Data')
        column.pack_start(cell, True)
        column.set_attributes(cell, text=3)
        treeview.append_column(column)
        treeview.show()
        scroll.add(treeview)
        scroll.show()
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.panel.attach(scroll, 2, 4, 0, 5, xoptions=gtk.FILL | gtk.EXPAND, yoptions=gtk.FILL | gtk.EXPAND, xpadding=5, ypadding=5)

        # Button save selected packets
        but = gtk.Button(label="Save selected packets")
        but.show()
        but.connect("clicked", self.save_packets, treeview)
        self.panel.attach(but, 2, 4, 5, 6, xoptions=0, yoptions=0, xpadding=5, ypadding=5)

    #+----------------------------------------------
    #| Called when user wants to update the process list
    #+----------------------------------------------
    def updateProcessList_cb(self, button):
        self.processStore.handler_block(self.handlerID)
        self.processStore.get_model().clear()
        for pid in readProcesses():
            self.processStore.append_text(str(pid) + "\t" + readProcessCmdline(pid)[0])
        self.processStore.handler_unblock(self.handlerID)

    #+----------------------------------------------
    #| Called when user select a process
    #+----------------------------------------------
    def processSelected_cb(self, widget):
        self.butSniffAll.set_sensitive(True)
        self.butSniffNetwork.set_sensitive(True)
        self.butSniffFS.set_sensitive(True)
        self.butSniffIPC.set_sensitive(True)
        self.filter1.set_sensitive(True)
        self.filter2.set_sensitive(True)
        self.filter3.set_sensitive(True)
        self.butUpdateFlows.set_sensitive(True)

        self.fdTreeview.get_model().clear()
        processSelected = self.processStore.get_active_text()
        self.pid = int(processSelected.split()[0])
        name = processSelected.split()[1]
        fds = self.retrieveFDs(self.filter1.get_active(), self.filter2.get_active(), self.filter3.get_active())
        for fd in fds:
            self.fdTreeview.get_model().append(None, fd)

    #+----------------------------------------------
    #| Retrieve the filtered FD
    #+----------------------------------------------
    def retrieveFDs(self, f_fs=True, f_net=True, f_proc=True):
        if self.pid == None:
            return []
        if False:  # f_net and (not f_fs) and (not f_proc): # -i for optimization
            cmd = "/usr/bin/lsof -i -a -d 0-1024 -a -p " + str(self.pid) + " | grep -v \"SIZE/OFF\" |awk -F \" \" {' print $5 \" \" $8 \" \" $9 \" \" $7'}"
        else:
            grep = "."
            if f_fs:
                grep += "DIR\|REG\|"
            if f_net:
                grep += "IPv4\|IPv6\|"
            if f_proc:
                grep += "CHR\|unix\|FIFO\|"
            grep = grep[:-2]
            cmd = "/usr/bin/lsof -d 0-1024 -a -p " + str(self.pid) + " | grep -v \"SIZE/OFF\" |awk -F \" \" {' print $4 \"##\" $5 \"##\" $9'} | grep \"" + grep + "\""

        lines = os.popen(cmd).readlines()
        fdescrs = []
        for fd in lines:
            elts = fd[:-1].split("##")
            fdescrs.append(elts)
        return fdescrs

    #+----------------------------------------------
    #| Called when user select a fd
    #+----------------------------------------------
    def fdSelected_cb(self, treeview):
        self.butSniffFiltered.set_sensitive(True)

    #+----------------------------------------------
    #| Called when user select a list of packet
    #+----------------------------------------------
    def save_packets(self, button, treeview):

        currentProject = self.zob.getCurrentProject()
        selection = treeview.get_selection()
        messages = []

        (model, paths) = selection.get_selected_rows()
        for path in paths:
            iter = model.get_iter(path)
            if(model.iter_is_valid(iter)):
                packetID = model.get_value(iter, 0)
                msg_fd = model.get_value(iter, 1)
                msg_direction = model.get_value(iter, 2)
                msg_timestamp = str(model.get_value(iter, 4))
                msg_rawPayload = self.packets[packetID]
                if msg_rawPayload == "":
                    continue

                #Compute the messages
                message = IPCMessage(msg_fd, msg_timestamp, msg_rawPayload.replace("\\x", ""), "none", msg_fd, msg_direction)
                messages.append(message)

        # We ask the confirmation
        md = gtk.MessageDialog(None,
            gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_QUESTION,
            gtk.BUTTONS_OK_CANCEL, "Are you sure to import the " + str(len(messages)) + " selected packets in project " + currentProject.getName() + ".")
#        md.add_button(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
        resp = md.run()
        md.destroy()

        if resp == gtk.RESPONSE_OK:
            self.saveMessagesInProject(self.zob.getCurrentWorkspace(), currentProject, messages, False)
        self.dialog.destroy()

        # We update the gui
        self.zob.update()

    #+----------------------------------------------
    #| Called when launching sniffing process
    #+----------------------------------------------
    def startSniff_cb(self, button, sniffOption):
        self.sniffOption = sniffOption
        self.selected_fds.clear()
        self.doSniff = True
        self.butStop.set_sensitive(True)
        self.butSniffAll.set_sensitive(False)
        self.butSniffNetwork.set_sensitive(False)
        self.butSniffFS.set_sensitive(False)
        self.butSniffIPC.set_sensitive(False)
        self.butSniffFiltered.set_sensitive(False)

        if self.sniffOption == "filtered":
            (model, paths) = self.fdTreeview.get_selection().get_selected_rows()
            for path in paths:
                iter = model.get_iter(path)
                if(model.iter_is_valid(iter)):
                    # Extract the fd number
                    self.selected_fds.add(int(re.match("(\d+)", model.get_value(iter, 0)).group(1)))
        self.packets = []
        self.pktTreestore.clear()
        self.aSniffThread = threading.Thread(None, self.sniffThread, None, (), {})
        self.aSniffThread.start()

    #+----------------------------------------------
    #| Called when stopping sniffing process
    #+----------------------------------------------
    def stopSniff_cb(self, button):
        self.doSniff = False
        self.butStop.set_sensitive(False)
        self.butSniffAll.set_sensitive(True)
        self.butSniffNetwork.set_sensitive(True)
        self.butSniffFS.set_sensitive(True)
        self.butSniffIPC.set_sensitive(True)
        self.butSniffFiltered.set_sensitive(True)

        if self.stracePid != None:
            self.stracePid.kill()
        self.stracePid = None
        if self.aSniffThread != None and self.aSniffThread.isAlive():
            self.aSniffThread._Thread__stop()
        self.aSniffThread = None

    #+----------------------------------------------
    #| Thread for sniffing a process
    #+----------------------------------------------
    def sniffThread(self):
        self.log.info("Launching sniff process")
        self.stracePid = subprocess.Popen(["/usr/bin/strace", "-xx", "-s", "65536", "-e", "read,write", "-p", str(self.pid)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        gobject.io_add_watch(self.stracePid.stderr, gobject.IO_IN | gobject.IO_HUP, self.handle_new_pkt)

    #+----------------------------------------------
    #| Handle new packet received by strace
    #+----------------------------------------------
    def handle_new_pkt(self, src, event):
        # Retrieve details from the captured paket
        data = src.readline()
        compiledRegex = re.compile("(read|write)\((\d+), \"(.*)\", \d+\)[ \t]*=[ \t]*(\d+)")
        m = compiledRegex.match(data)
        if m == None:
            return self.doSniff
        direction = data[m.start(1): m.end(1)]
        fd = int(data[m.start(2): m.end(2)])
        pkt = data[m.start(3): m.end(3)]
        returnCode = int(data[m.start(4): m.end(4)])

        # Apply filter
        if self.sniffOption == "fs":
            if not self.getTypeFromFD(int(fd)) == "fs":
                return self.doSniff
        elif self.sniffOption == "network":
            if not self.getTypeFromFD(int(fd)) == "network":
                return self.doSniff
        elif self.sniffOption == "ipc":
            if not self.getTypeFromFD(int(fd)) == "ipc":
                return self.doSniff
        elif self.sniffOption == "filtered":
            if not fd in self.selected_fds:
                return self.doSniff

        # Add packet
        if returnCode > 256:
            tmp_pkt = pkt[:255] + "..."
        else:
            tmp_pkt = pkt
        self.pktTreestore.append(None, [len(self.packets), fd, direction, tmp_pkt.replace("\\x", ""), int(time.time())])
        self.packets.append(pkt)
        return self.doSniff

    #+----------------------------------------------
    #| GETTERS
    #+----------------------------------------------
    def getTypeFromFD(self, fd):
        path = "/proc/" + str(self.pid) + "/fd/" + str(fd)
        if os.path.realpath(path).find("socket:[", 0) != -1:
            return "network"
        elif os.path.isfile(os.path.realpath(path)) or os.path.isdir(os.path.realpath(path)):
            return "fs"
        else:
            return "ipc"

    def getPanel(self):
        return self.panel
