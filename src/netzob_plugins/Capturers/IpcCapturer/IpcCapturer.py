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
import re
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
from netzob.Common.Plugins.Capturers.AbstractCapturer import AbstractCapturer


#+----------------------------------------------
#| IpcCapturer:
#|     Ensures the capture of information through IPC proxing
#+----------------------------------------------
class IpcCapturer(AbstractCapturer):

    def kill(self):
        if self.stracePid is not None and self.stracePid.poll() is not None:
            self.stracePid.kill()
        if self.aSniffThread is not None and self.aSniffThread.isAlive():
            self.aSniffThread._Thread__stop()

    #+----------------------------------------------
    #| Constructor:
    #+----------------------------------------------
    def __init__(self, netzob):
        super(IpcCapturer, self).__init__("IPC CAPTURER", netzob)
        self.netzob = netzob

        self.packets = []
        self.pid = None
        self.stracePid = None
        self.aSniffThread = None
        self.doSniff = False
        self.selected_fds = set()
        self.sniffOption = None

    def getProcessList(self):
        """getProcessList:
                Return the process list
        """
        processList = []
        for pid in readProcesses():
            processList.append(str(pid) + "\t" + str(readProcessCmdline(pid)[0]))
        return processList

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
        if self.pid is None:
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
    def fdSelected_cb(self, selection):
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
        md = Gtk.MessageDialog(None,
                               Gtk.DialogFlags.DESTROY_WITH_PARENT, Gtk.MessageType.QUESTION,
                               Gtk.ButtonsType.OK_CANCEL, (_("Are you sure to import the %s selected packets in project %s?") % (str(len(messages)), currentProject.getName())))
#        md.add_button(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL)
        resp = md.run()
        md.destroy()

        if resp == Gtk.ResponseType.OK:
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

        if self.stracePid is not None:
            self.stracePid.kill()
        self.stracePid = None
        if self.aSniffThread is not None and self.aSniffThread.isAlive():
            self.aSniffThread._Thread__stop()
        self.aSniffThread = None

    #+----------------------------------------------
    #| Thread for sniffing a process
    #+----------------------------------------------
    def sniffThread(self):
        self.log.info(_("Launching sniff process"))
        self.stracePid = subprocess.Popen(["/usr/bin/strace", "-xx", "-s", "65536", "-e", "read,write", "-p", str(self.pid)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        GObject.io_add_watch(self.stracePid.stderr, GObject.IO_IN | GObject.IO_HUP, self.handle_new_pkt)

    #+----------------------------------------------
    #| Handle new packet received by strace
    #+----------------------------------------------
    def handle_new_pkt(self, src, event):
        # Retrieve details from the captured paket
        data = src.readline()
        compiledRegex = re.compile("(read|write)\((\d+), \"(.*)\", \d+\)[ \t]*=[ \t]*(\d+)")
        m = compiledRegex.match(data)
        if m is None:
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
