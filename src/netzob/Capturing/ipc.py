#!/usr/bin/python
# -*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|         01001110 01100101 01110100 01111010 01101111 01100010             | 
#+---------------------------------------------------------------------------+
#| NETwork protocol modeliZatiOn By reverse engineering                      |
#| ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~+
#| @license      : GNU GPL v3                                                |
#| @copyright    : Georges Bossert and Frederic Guihery                      |
#| @url          : http://code.google.com/p/netzob/                          |
#| ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~+
#| @author       : {gbt,fgy}@amossys.fr                                      |
#| @organization : Amossys, http://www.amossys.fr                            |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+ 
#| Standard library imports
#+---------------------------------------------------------------------------+
import gtk
import pango
import gobject
import re
import pygtk
pygtk.require('2.0')
import logging
import threading
import os
import time
import random
from ptrace.linux_proc import readProcesses, readProcessCmdline
import subprocess

#+---------------------------------------------- 
#| Local Imports
#+----------------------------------------------
from ..Common import ConfigurationParser
import scapyy.all as scapyy

#+---------------------------------------------- 
#| Configuration of the logger
#+----------------------------------------------
loggingFilePath = ConfigurationParser.ConfigurationParser().get("logging", "path")
logging.config.fileConfig(loggingFilePath)

#+---------------------------------------------- 
#| IPC :
#|     ensures the capture of informations through IPC proxing
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.2
#+---------------------------------------------- 
class IPC:
    
    #+---------------------------------------------- 
    #| Called when user select a new trace
    #+----------------------------------------------
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
    #| Constructor :
    #| @param groups: list of all groups 
    #+----------------------------------------------   
    def __init__(self, zob):
        self.zob = zob
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Capturing.ipc.py')
        self.packets = []
        self.pid = None
        self.stracePid = None
        self.aSniffThread = None
        self.doSniff = False
        self.selected_fds = set()
        
        # Network Capturing Panel
        self.panel = gtk.Table(rows=6, columns=4, homogeneous=False)
        self.panel.show()

        ## TODO: add update_process_list button

        # Processfilter
        label = gtk.Label("Chose process to trace")
        label.show()
        self.processStore = gtk.combo_box_entry_new_text()
        self.processStore.show()
        self.processStore.set_size_request(300, -1)
        self.processStore.set_model(gtk.ListStore(str))
        for pid in readProcesses():
            self.processStore.append_text(str(pid) + "\t" + readProcessCmdline(pid)[0])
        self.panel.attach(label, 0, 1, 0, 1, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        self.panel.attach(self.processStore, 1, 2, 0, 1, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        # FD filter
        hbox = gtk.HBox(False, spacing=10)        
        hbox.show()
        f1 = gtk.CheckButton("File system")
        f2 = gtk.CheckButton("Network")
        f3 = gtk.CheckButton("Interprocess")
        f1.set_active(True)
        f2.set_active(True)
        f3.set_active(True)
        f1.show()
        f2.show()
        f3.show()
        hbox.pack_start(f1, False, False, 0)
        hbox.pack_start(f2, False, False, 0)
        hbox.pack_start(f3, False, False, 0)
        self.panel.attach(hbox, 0, 2, 1, 2, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        self.processStore.connect("changed", self.showFileDescriptors_cb, f1, f2, f3)

        # File descriptor list
        scroll = gtk.ScrolledWindow()
        self.fdTreeview = gtk.TreeView(gtk.TreeStore(str, str, str)) # file descriptor, type, name
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
       
        # Sniff launching button
        butStart = gtk.Button(label="Start sniffing")
        butStart.show()
        butStart.set_sensitive(False)
        self.panel.attach(butStart, 0, 1, 5, 6, xoptions=0, yoptions=0, xpadding=5, ypadding=5)
        self.fdTreeview.connect("cursor-changed", self.fd_selected, butStart)

        # Sniff stopping button
        butStop = gtk.Button(label="Stop sniffing")
        butStop.show()
        butStop.set_sensitive(False)
        butStop.connect("clicked", self.stop_sniff, butStart)
        butStart.connect("clicked", self.start_sniff, butStop)
        self.panel.attach(butStop, 1, 2, 5, 6, xoptions=0, yoptions=0, xpadding=5, ypadding=5)

        # Packet list
        scroll = gtk.ScrolledWindow()
        self.pktTreestore = gtk.TreeStore(int, int, str, str, int) # pktID, fd, direction (read/write), data, timestamp
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
    #| Called when user wants to see the FD opened by a process
    #+----------------------------------------------
    def showFileDescriptors_cb(self, widget, f1, f2, f3):
        self.fdTreeview.get_model().clear()
        processSelected = self.processStore.get_active_text()        
        self.pid = int(processSelected.split()[0])
        name = processSelected.split()[1]
        fds = self.retrieveFDs(f1.get_active(), f2.get_active(), f3.get_active())
        for fd in fds:
            self.fdTreeview.get_model().append(None, fd)

    #+---------------------------------------------- 
    #| Retrieve the filtered FD
    #+----------------------------------------------
    def retrieveFDs(self, f_fs=True, f_net=True, f_proc=True):
        if False: # f_net and (not f_fs) and (not f_proc): # -i for optimization
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
    def fd_selected(self, treeview, butStart):
        butStart.set_sensitive(True)

    #+---------------------------------------------- 
    #| Called when user select a list of packet
    #+----------------------------------------------
    def save_packets(self, button, treeview):
        dialog = gtk.Dialog(title="Save selected packet as a new trace", flags=0, buttons=None)
        dialog.show()
        table = gtk.Table(rows=2, columns=3, homogeneous=False)
        table.show()
        # Add to an existing trace
        label = gtk.Label("Add to an existing trace")
        label.show()
        entry = gtk.combo_box_entry_new_text()
        entry.show()
        entry.set_size_request(300, -1)
        entry.set_model(gtk.ListStore(str))
        tracesDirectoryPath = ConfigurationParser.ConfigurationParser().get("traces", "path")
        for tmpDir in os.listdir(tracesDirectoryPath):
            if tmpDir == '.svn':
                continue
            entry.append_text(tmpDir)
        but = gtk.Button("Save")
        but.connect("clicked", self.add_packets_to_existing_trace, entry, treeview.get_selection(), dialog)
        but.show()
        table.attach(label, 0, 1, 0, 1, xoptions=0, yoptions=0, xpadding=5, ypadding=5)
        table.attach(entry, 1, 2, 0, 1, xoptions=0, yoptions=0, xpadding=5, ypadding=5)
        table.attach(but, 2, 3, 0, 1, xoptions=0, yoptions=0, xpadding=5, ypadding=5)

        # Create a new trace
        label = gtk.Label("Create a new trace")
        label.show()
        entry = gtk.Entry()
        entry.show()
        but = gtk.Button("Save")
        but.connect("clicked", self.create_new_trace, entry, treeview.get_selection(), dialog)
        but.show()
        table.attach(label, 0, 1, 1, 2, xoptions=0, yoptions=0, xpadding=5, ypadding=5)
        table.attach(entry, 1, 2, 1, 2, xoptions=0, yoptions=0, xpadding=5, ypadding=5)
        table.attach(but, 2, 3, 1, 2, xoptions=0, yoptions=0, xpadding=5, ypadding=5)

        dialog.action_area.pack_start(table, True, True, 0)

    #+---------------------------------------------- 
    #| Add a selection of packets to an existing trace
    #+----------------------------------------------
    def add_packets_to_existing_trace(self, button, entry, selection, dialog):
        tracesDirectoryPath = ConfigurationParser.ConfigurationParser().get("traces", "path")
        existingTraceDir = tracesDirectoryPath + "/" + entry.get_active_text()
        # Create the new XML structure
        res = "<datas>\n"
        (model, paths) = selection.get_selected_rows()
        for path in paths:
            iter = model.get_iter(path)
            if(model.iter_is_valid(iter)):
                packetID = model.get_value(iter, 0)
                timestamp = str(model.get_value(iter, 4))
                rawPayload = self.packets[packetID]
                if rawPayload == "":
                    continue
                res += "<data proto=\"ipc\" sourceIp=\"local\" sourcePort=\"local\" targetIp=\"local\" targetPort=\"local\" timestamp=\"" + timestamp + "\">\n"
                res += rawPayload.replace("\\x", "") + "\n"
                res += "</data>\n"
        res += "</datas>\n"
        # Dump into a random XML file
        fd = open(existingTraceDir + "/" + str(random.randint(100000, 9000000)) + ".txt"  , "w")
        fd.write(res)
        fd.close()
        dialog.destroy()

    #+---------------------------------------------- 
    #| Creation of a new trace from a selection of packets
    #+----------------------------------------------
    def create_new_trace(self, button, entry, selection, dialog):
        tracesDirectoryPath = ConfigurationParser.ConfigurationParser().get("traces", "path")
        for tmpDir in os.listdir(tracesDirectoryPath):
            if tmpDir == '.svn':
                continue
            if entry.get_text() == tmpDir:
                dialogBis = gtk.Dialog(title="This trace already exists", flags=0, buttons=None)
                dialogBis.set_size_request(250, 50)
                dialogBis.show()
                return

        # Create the dest Dir
        newTraceDir = tracesDirectoryPath + "/" + entry.get_text()
        os.mkdir(newTraceDir)
        # Create the new XML structure
        res = "<datas>\n"
        (model, paths) = selection.get_selected_rows()
        for path in paths:
            iter = model.get_iter(path)
            if(model.iter_is_valid(iter)):
                packetID = model.get_value(iter, 0)
                timestamp = str(model.get_value(iter, 4))
                rawPayload = self.packets[packetID]
                if rawPayload == "":
                    continue
                res += "<data proto=\"ipc\" sourceIp=\"local\" sourcePort=\"local\" targetIp=\"local\" targetPort=\"local\" timestamp=\"" + timestamp + "\">\n"
                res += rawPayload.replace("\\x", "") + "\n"
                res += "</data>\n"
        res += "</datas>\n"
        # Dump into a random XML file
        fd = open(newTraceDir + "/" + str(random.randint(100000, 9000000)) + ".txt"  , "w")
        fd.write(res)
        fd.close()
        dialog.destroy()
        self.zob.updateListOfAvailableTraces()

    #+---------------------------------------------- 
    #| Called when launching sniffing process
    #+----------------------------------------------
    def start_sniff(self, butStart, butStop):
        self.selected_fds.clear()
        self.doSniff = True
        butStop.set_sensitive(True)
        butStart.set_sensitive(False)
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
    def stop_sniff(self, butStop, butStart):
        self.doSniff = False
        butStop.set_sensitive(False)
        butStart.set_sensitive(True)

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
        self.log.info("Launching sniff process with : fd=" + str(self.selected_fds))
        self.stracePid = subprocess.Popen(["/usr/bin/strace", "-xx", "-s", "65536", "-e", "read,write", "-p", str(self.pid)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        gobject.io_add_watch(self.stracePid.stderr, gobject.IO_IN | gobject.IO_HUP, self.handle_new_pkt)

    #+---------------------------------------------- 
    #| Handle new packet received by strace
    #+----------------------------------------------
    def handle_new_pkt(self, src, event):
        data = src.readline()
        compiledRegex = re.compile("(read|write)\((\d+), \"(.*)\", \d+\)[ ]*=[ ]*(\d+)")
        m = compiledRegex.match(data)
        if m == None:
            return self.doSniff
        direction = data[ m.start(1) : m.end(1) ]
        fd = int(data[ m.start(2) : m.end(2) ])
        pkt = data[ m.start(3) : m.end(3) ]
        returnCode = int(data[ m.start(4) : m.end(4) ])

        if fd in self.selected_fds:
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
    def getPanel(self):
        return self.panel
