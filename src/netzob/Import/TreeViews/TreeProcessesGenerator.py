# coding: utf8

#+----------------------------------------------
#| Global Imports
#+----------------------------------------------
import logging
import gtk
import os

#+----------------------------------------------
#| Local Imports
#+----------------------------------------------
from netzob.Common.ExecutionContext import ExecutionContext

#+----------------------------------------------
#| TreeProcessGenerator :
#|     update and generates the treestore
#|     dedicated to the processes
#+----------------------------------------------
class TreeProcessesGenerator():

    #+----------------------------------------------
    #| Constructor :
    #| @param processes : the processes
    #+----------------------------------------------
    def __init__(self, processes):
        self.processes = processes
        self.treestore = None
        self.treeview = None
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Capturing.TreeViews.TreeProcessesGenerator.py')

    #+----------------------------------------------
    #| initialization :
    #| builds and configures the treeview
    #+----------------------------------------------
    def initialization(self):
        # Tree store contains :
        # str : text ( process Command )
        # str : text ( process PID )
        # str : color foreground
        # str : color background
        self.treestore = gtk.TreeStore(str, str, str, str)
        self.treeview = gtk.TreeView(self.treestore)

        # messages list
        self.scroll = gtk.ScrolledWindow()
        self.scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.scroll.show()
        self.scroll.set_size_request(200, 300)
        self.scroll.add(self.treeview)

        lvcolumn = gtk.TreeViewColumn('Processes')
        lvcolumn.set_sort_column_id(1)
        cell = gtk.CellRendererText()
        lvcolumn.pack_start(cell, True)
        cell.set_property('background-set' , True)
        cell.set_property('foreground-set' , True)
        lvcolumn.set_attributes(cell, text=0, foreground=2, background=3)
        self.treeview.append_column(lvcolumn)
        self.treeview.show()

    #+----------------------------------------------
    #| clear :
    #|         Clear the class
    #+----------------------------------------------
    def clear(self):
        del self.processes[:]

    #+----------------------------------------------
    #| default :
    #|         Update the treestore in normal mode
    #+----------------------------------------------
    def default(self):
        self.log.debug("Updating the treestore of the processes in default mode")
        self.treestore.clear()

        self.updateProcessesList()

        for process in self.processes :
            iter = self.treestore.append(None, [process.getName(), process.getPid(), '#000000', '#FFFFFF'])


    def updateProcessesList(self):
        self.log.debug("Updating the list of executing processes.")
        self.processes = ExecutionContext.getCurrentProcesses()




    #+----------------------------------------------
    #| GETTERS :
    #+----------------------------------------------
    def getTreeview(self):
        return self.treeview
    def getScrollLib(self):
        return self.scroll
    def getProcesses(self):
        return self.processes

    #+----------------------------------------------
    #| SETTERS :
    #+----------------------------------------------
    def setProcess(self, processes):
        self.processes = processes

