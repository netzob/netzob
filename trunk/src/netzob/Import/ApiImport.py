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
import pygtk
import tempfile
pygtk.require('2.0')
import logging
import os
import time
import threading

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.ConfigurationParser import ConfigurationParser
from netzob.Common.ExecutionContext import ExecutionContext
from netzob.Import.GOTPoisoning.PrototypesRepositoryParser import PrototypesRepositoryParser
from netzob.Import.GOTPoisoning.ParasiteGenerator import ParasiteGenerator
from netzob.Import.GOTPoisoning.InjectorGenerator import InjectorGenerator
from netzob.Import.GOTPoisoning.GOTPoisoner import GOTPoisoner

#+---------------------------------------------------------------------------+
#| Api :
#|     GUI for capturing messages from api hooking
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.2
#+---------------------------------------------------------------------------+
class ApiImport:
    
    #+-----------------------------------------------------------------------+ 
    #| Called when user select a new trace
    #+-----------------------------------------------------------------------+
    def new(self):
        pass

    def update(self):
        pass

    def clear(self):
        pass

    def kill(self):
        pass
    
    #+-----------------------------------------------------------------------+
    #| Constructor :
    #| @param groups: list of all groups 
    #+-----------------------------------------------------------------------+ 
    def __init__(self, zob):        
        self.zob = zob
        self.listOfProcess = []
        
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Capturing.api.py')
        self.packets = []
        
        # First we parse the repository
        repositoryFile = ConfigurationParser().get("import", "repository_prototypes")
        if repositoryFile == "" or not os.path.isfile(repositoryFile) :
            self.log.warn("Unable to find a repository file for API injector.")
        else :
            self.repositoryOfSharedLib = PrototypesRepositoryParser.loadFromXML(repositoryFile)
        
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Main panel
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        self.panel = gtk.Table(rows=6, columns=5, homogeneous=False)
        self.panel.show()
        
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # List of processes
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        but = gtk.Button("Update processes list")
        but.show()
        but.connect("clicked", self.updateProcessList_cb)
        self.processStore = gtk.combo_box_entry_new_text()
        self.processStore.show()
        self.processStore.set_size_request(500, -1)
        self.processStore.set_model(gtk.ListStore(str))
        self.panel.attach(but, 0, 1, 0, 1, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        self.panel.attach(self.processStore, 1, 5, 0, 1, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        
        self.handlerID = self.processStore.connect("changed", self.processSelected_cb)
        
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # List of DLL
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        scroll = gtk.ScrolledWindow()
        self.dllTreeview = gtk.TreeView(gtk.TreeStore(str, str, str)) # file descriptor, type, name
        self.dllTreeview.get_selection().set_mode(gtk.SELECTION_SINGLE)
        cell = gtk.CellRendererText()
        # Col file descriptor
        column = gtk.TreeViewColumn('Name')
        column.pack_start(cell, True)
        column.set_attributes(cell, text=0)
        self.dllTreeview.append_column(column)
        # Col type
        column = gtk.TreeViewColumn('Version')
        column.pack_start(cell, True)
        column.set_attributes(cell, text=1)
        self.dllTreeview.append_column(column)
        # Col name
        column = gtk.TreeViewColumn('Path')
        column.pack_start(cell, True)
        column.set_attributes(cell, text=2)
        self.dllTreeview.append_column(column)
        self.dllTreeview.show()
        
        self.dllTreeview.connect("cursor-changed", self.dllSelected_cb)
#        self.dllHandlerID = self.dllTreeview.connect("changed", self.dllSelected_cb)        
        
        scroll.add(self.dllTreeview)
        scroll.show()
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.panel.attach(scroll, 0, 5, 2, 3, xoptions=gtk.FILL, yoptions=gtk.FILL | gtk.EXPAND, xpadding=5, ypadding=5)

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # List of prototypes
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        self.dllStore = gtk.combo_box_entry_new_text()
        self.dllStore.show()
        self.dllStore.set_size_request(300, -1)
        self.dllStore.set_model(gtk.ListStore(str))
        
        self.dllStore.connect("changed", self.prototypeSelected_cb)
        
        self.panel.attach(self.dllStore, 0, 3, 4, 5, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        
        self.butAddPrototype = gtk.Button("Create prototype")
        self.butAddPrototype.show()
        self.butAddPrototype.connect("clicked", self.updateProcessList_cb)
        self.panel.attach(self.butAddPrototype, 3, 4, 4, 5, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        
        self.butRemovePrototype = gtk.Button("Delete prototype")
        self.butRemovePrototype.show()
        self.butRemovePrototype.connect("clicked", self.updateProcessList_cb)
        self.panel.attach(self.butRemovePrototype, 4, 5, 4, 5, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        
        
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # List of buttons (start and stop capture)
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        self.startCapture = gtk.Button("Start capture")
        self.startCapture.show()
        self.startCapture.connect("clicked", self.startCaptureFunction)
        self.panel.attach(self.startCapture, 3, 4, 6, 7, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        
        self.stopCapture = gtk.Button("Stop capture")
        self.stopCapture.show()
        self.stopCapture.connect("clicked", self.stopCaptureFunction)
        self.panel.attach(self.stopCapture, 4, 5, 6, 7, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        
        
        # Packet list
        scroll = gtk.ScrolledWindow()
        self.pktTreestore = gtk.TreeStore(int, str, str, str, int) # pktID, Function, Parameter, data, timestamp
        treeview = gtk.TreeView(self.pktTreestore)
        treeview.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
        cell = gtk.CellRendererText()
        # Col fd
        column = gtk.TreeViewColumn('Function')
        column.pack_start(cell, True)
        column.set_attributes(cell, text=1)
        treeview.append_column(column)
        # Col direction
        column = gtk.TreeViewColumn('Parameter')
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
        self.panel.attach(scroll, 6, 7, 0, 5, xoptions=gtk.FILL | gtk.EXPAND, yoptions=gtk.FILL | gtk.EXPAND, xpadding=5, ypadding=5)

    
    #+---------------------------------------------- 
    #| Called when user wants to update the process list
    #+----------------------------------------------
    def updateProcessList_cb(self, button):
        self.processStore.handler_block(self.handlerID)
        # clear the list of process
        self.processStore.get_model().clear()
        
        # retrieves the list of process
        self.listOfProcess = ExecutionContext.getCurrentProcesses()
        
        # add in the list all the process
        for process in self.listOfProcess :
            self.processStore.append_text(str(process.getPid()) + "\t" + process.getName())        
        self.processStore.handler_unblock(self.handlerID)

    #+---------------------------------------------- 
    #| Called when user select a process
    #+----------------------------------------------
    def processSelected_cb(self, widget):        
        # Updates the list of shared lib
        strProcessSelected = self.processStore.get_active_text()        
        pid = int(strProcessSelected.split()[0])
        self.selectedProcess = None
        
        for process in self.listOfProcess :
            if process.getPid() == pid :
                self.selectedProcess = process
                
        if self.selectedProcess != None :
            libs = self.selectedProcess.getSharedLibs()  
            self.dllTreeview.get_model().clear()
            for lib in libs :
                self.dllTreeview.get_model().append(None, [lib.getName(), lib.getVersion(), lib.getPath()])        
            
        else :
            self.log.error("A selected process cannot be found !")
        
    #+---------------------------------------------- 
    #| Called when user select a a DLL
    #+----------------------------------------------
    def dllSelected_cb(self, treeview): 
        # Retrieve the dll selected    
        treeselection = treeview.get_selection()
        (model, pathlist) = treeselection.get_selected_rows()
        iter = model.get_iter(pathlist[0])
        
        found = False
        
        self.selectedDLL = None
        
        if(model.iter_is_valid(iter)):
            libName = model.get_value(iter, 0)
            libVersion = model.get_value(iter, 1)
            libPath = model.get_value(iter, 2)
            found = True
        
        if found == False :
            self.log.error("The selected process cannot be find !")
            return
        
        self.dllStore.get_model().clear()
        
        # search for available prototypes given lib in repository
        for lib in self.repositoryOfSharedLib :
            if lib.getName() == libName :
                self.selectedDLL = lib
                for func in lib.getFunctions() :
                    self.dllStore.append_text(func.getPrototype())        
  
    #+---------------------------------------------- 
    #| Called when user select a prototype
    #+----------------------------------------------
    def prototypeSelected_cb(self, widget):     
        if self.selectedProcess == None :
            self.log.warning("You have to select a process if you want to capture it")        
            return
        if self.selectedDLL == None :
            self.log.warning("You have to select a DLL if you want to capture it")        
            return
        
           
        # Updates the list of shared lib
        prototype = self.dllStore.get_active_text()        
        self.selectedFunction = None
        
        for function in self.selectedDLL.getFunctions():
            if function.getPrototype() == prototype :
                self.selectedFunction = function
        
        if self.selectedFunction == None :
            self.log.error("Impossible to retrieve the selected function")
        else :
            self.log.info("Selected function done!")
            
    #+---------------------------------------------- 
    #| Called when launching sniffing process
    #+----------------------------------------------
    def startCaptureFunction(self, button):
        if self.selectedProcess == None :
            self.log.warning("You have to select a process if you want to capture it")        
            return
        if self.selectedDLL == None :
            self.log.warning("You have to select a DLL if you want to capture it")        
            return
        if self.selectedFunction == None :
            self.log.warning("You have to select a function if you want to capture it")        
            return
        
        # Create a temporary folder (secure way) <- hihihihi
        tmpFolder = tempfile.mkdtemp()
        self.log.info("Temporary folder : " + tmpFolder)
        
        parasiteGenerator = ParasiteGenerator(tmpFolder)
        parasiteGenerator.addAnHijackedFunctions(self.selectedFunction)
        
        parasiteGenerator.writeParasiteToFile()
        parasiteGenerator.compileParasite()
        parasiteGenerator.linkParasite()
        
        injectorGenerator = InjectorGenerator(tmpFolder, parasiteGenerator)
        injectorGenerator.writeInjectorToFile()    
        injectorGenerator.compileInjector()
        
        poisoner = GOTPoisoner(parasiteGenerator, injectorGenerator) 
        poisoner.injectProcess(self.selectedProcess.getPid())
        
        
        self.fifoFile = parasiteGenerator.getFifoFile()
        
        self.aSniffThread = threading.Thread(None, self.sniffThread, None, (), {})
        self.aSniffThread.start()
                
        self.log.info("Starting the capture of [{0}]".format(self.selectedProcess.getPid()))
        self.log.info("DLL [{0}]".format(self.selectedDLL.getName()))
        self.log.info("Function [{0}]".format(self.selectedFunction.getPrototype()))
    
    
    def readFromFifo(self):
        self.fifo = open(self.fifoFile, 'r')
        receivedMessage = self.readline(self.fifo)
        self.log.info("FIFO : " + receivedMessage)
        while (receivedMessage != "STOP\n") :
            self.pktTreestore.append(None, [len(self.packets), "NONE", "NC", receivedMessage, int(time.time())])
            receivedMessage = self.readline(self.fifo)
            self.log.info("FIFO : " + receivedMessage)
            
        
    
        
    def createFifo(self):
        self.log.info("Creating the FIFO file : " + self.fifoFile)
        # Create the fifo
        try :
            os.mkfifo(self.fifoFile)
        except OSError, e:
            self.log.error("Failed to create FIFO: %s" % e)
            return False
        else :
            self.log.info("The fifo has been created...")
            return True
    
    def readline(self, f):
        s = f.readline()
        while s == "":
            time.sleep(0.0001)
            s = f.readline()
        return s  
    
    def sniffThread(self):
        # Create the receptor (FIFO creation)
        if not self.createFifo() :
            self.log.error("Cannot execute GOT Poisoning since FIFO file was not created !")
            return
        
        # Read from the fifo
        self.readFromFifo()
        
    #+---------------------------------------------- 
    #| Called when launching sniffing process
    #+----------------------------------------------
    def stopCaptureFunction(self, button):
        self.log.debug("Stoping the capture...")
        
        # We first stop the thread
        if self.aSniffThread != None and self.aSniffThread.isAlive():
            self.aSniffThread._Thread__stop()
        self.aSniffThread = None
        
        # now we clean everything
        print "Reading finish, we close the FIFO."
        # Close and remove fifo
        self.fifo.close()
        os.remove(self.fifoFile)
    
        

    
    #+---------------------------------------------- 
    #| GETTERS
    #+----------------------------------------------
    def getPanel(self):
        return self.panel
