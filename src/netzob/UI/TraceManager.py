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
import logging
pygtk.require('2.0')

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+


#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+



#+---------------------------------------------------------------------------+ 
#| TraceManager :
#|     This class displays the GUI to manage all the manipulated traces in a 
#|     workspace
#+---------------------------------------------------------------------------+
class TraceManager():
    
    #+-----------------------------------------------------------------------+
    #| Constructor :
    #| @param workspace : the current workspace
    #+-----------------------------------------------------------------------+  
    def __init__(self, workspace):
        self.workspace = workspace
        
        self.createDialog()
        
        self.updateContent()
        
    def createDialog(self):
        self.dialog = gtk.Dialog(title="Trace Manager", flags=0, buttons=None)
        self.dialog.set_default_size(800, 600)
        mainTable = gtk.Table(rows=2, columns=1, homogeneous=False)
        
        scroll = gtk.ScrolledWindow()
        self.treestoreTraces = gtk.TreeStore(str, str, str, str, str, int) # id, date, type, project name, description, nb message,
        treeview = gtk.TreeView(self.treestoreTraces)
        treeview.get_selection().set_mode(gtk.SELECTION_SINGLE)
        treeview.connect("cursor-changed", self.trace_selected)

        cell = gtk.CellRendererText()
        # Col Date
        column = gtk.TreeViewColumn('Date')
        column.pack_start(cell, True)
        column.set_attributes(cell, text=1)
        treeview.append_column(column)
        # Col Type
        column = gtk.TreeViewColumn('Type')
        column.pack_start(cell, True)
        column.set_attributes(cell, text=2)
        treeview.append_column(column)
        # Col project name
        column = gtk.TreeViewColumn('Original project')
        column.pack_start(cell, True)
        column.set_attributes(cell, text=3)
        treeview.append_column(column)
        # Col Description
        column = gtk.TreeViewColumn('Description')
        column.pack_start(cell, True)
        column.set_attributes(cell, text=4)
        treeview.append_column(column)
        # Col Nb message
        column = gtk.TreeViewColumn('Nb messages')
        column.pack_start(cell, True)
        column.set_attributes(cell, text=5)
        treeview.append_column(column)
        treeview.show()
        scroll.add(treeview)
        scroll.show()
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        mainTable.attach(scroll, 0, 1, 0, 1, xoptions=gtk.FILL | gtk.EXPAND, yoptions=gtk.FILL | gtk.EXPAND, xpadding=5, ypadding=5)
        
        
        scroll2 = gtk.ScrolledWindow()
        self.treestoreMessages = gtk.TreeStore(str, str, str) # id, timestamp, data,
        treeviewMessage = gtk.TreeView(self.treestoreMessages)
        treeviewMessage.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
#        treeview.connect("cursor-changed", self.packet_details)

        cell = gtk.CellRendererText()
        # Col ID
        column = gtk.TreeViewColumn('ID')
        column.pack_start(cell, True)
        column.set_attributes(cell, text=0)
        treeviewMessage.append_column(column)
        # Col Type
        column = gtk.TreeViewColumn('Timestamp')
        column.pack_start(cell, True)
        column.set_attributes(cell, text=1)
        treeviewMessage.append_column(column)
        # Col project name
        column = gtk.TreeViewColumn('Data')
        column.pack_start(cell, True)
        column.set_attributes(cell, text=2)
        treeviewMessage.append_column(column)
        
        treeviewMessage.show()
        scroll2.add(treeviewMessage)
        scroll2.show()
        scroll2.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        mainTable.attach(scroll2, 0, 1, 1, 2, xoptions=gtk.FILL | gtk.EXPAND, yoptions=gtk.FILL | gtk.EXPAND, xpadding=5, ypadding=5)
        
        
        self.dialog.vbox.pack_end(mainTable, True, True, 0)
        self.dialog.show_all()
    
    def trace_selected(self, treeview):
        (model, iter) = treeview.get_selection().get_selected()
        trace_id = None
        if(iter):
            if(model.iter_is_valid(iter)):
                trace_id = model.get_value(iter, 0)
        if trace_id == None :
            logging.warn("Impossible to find the selected trace")
            return
        selectedTrace = None
        for trace in self.workspace.getImportedTraces() :
            if str(trace.getImportID()) == trace_id :
                selectedTrace = trace
        if selectedTrace == None :
            logging.warn("The provided ID do not match any trace.")
            return
        self.updateContentMessage(selectedTrace)        
        
    def updateContentMessage(self, trace):
        self.treestoreMessages.clear()
        for message in trace.getMessages() :
            self.treestoreMessages.append(None, [str(message.getID()), str(message.getTimestamp()), str(message.getData())])
        
    def updateContent(self):
        self.treestoreTraces.clear()
        for trace in self.workspace.getImportedTraces() :
            id = str(trace.getImportID())
            date = str(trace.getDate())
            type = str(trace.getDataType())
            projectName = str(trace.getProjectName())
            description = str(trace.getDescription())
            nbMessage = len(trace.getMessages())
            self.treestoreTraces.append(None, [id, date, type, projectName, description, nbMessage])
    
