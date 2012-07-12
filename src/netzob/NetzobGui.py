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
from gi.repository import Gtk, Gdk
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import GObject
import threading
import sys
import logging
import optparse
import locale

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.Plugins.NetzobPlugin import NetzobPlugin
from netzob.Common import DepCheck
from netzob.Common.Menu import Menu
from netzob.UI.Vocabulary.Controllers.VocabularyController import VocabularyController
from netzob.Inference.Grammar.UIGrammarInference import UIGrammarInference
from netzob.Common.LoggingConfiguration import LoggingConfiguration
from netzob.Simulator.UISimulator import UISimulator
from netzob.Common.ResourcesConfiguration import ResourcesConfiguration
from netzob.Common.Workspace import Workspace
from netzob.Common.Project import Project
from netzob.Common import CommandLine


actualview="vocabulary"    #default view when load netzob

#+----------------------------------------------
#| NetzobGUI:
#|     Graphical runtime class
#+----------------------------------------------
class NetzobGui(object):
    
    
    


    #+----------------------------------------------
    #| Constructor:
    #+----------------------------------------------
    def __init__(self, commandLineParser):

        locale.bindtextdomain("netzob", ResourcesConfiguration.getLocaleLocation())
        locale.textdomain("netzob")

        try:
            locale.getlocale()
        except:
            logging.exception("setlocale failed, resetting to C")
            locale.setlocale(locale.LC_ALL, "C")

        # First we initialize and verify all the resources
        if not ResourcesConfiguration.initializeResources():
            logging.fatal("Error while configuring the resources of Netzob")
            sys.exit()

        if commandLineParser.getOptions().workspace is None:
            workspace = str(ResourcesConfiguration.getWorkspaceFile())
        else:
            workspace = commandLineParser.getOptions().workspace

        logging.debug("The workspace: {0}".format(str(workspace)))

        # loading the workspace
        self.currentWorkspace = (Workspace.loadWorkspace(workspace))

        # the semi-automatic loading of the workspace has failed (second attempt)
        if self.currentWorkspace is None:
            # we force the creation (or specification) of the workspace
            if not ResourcesConfiguration.initializeResources(True):
                logging.fatal("Error while configuring the resources of Netzob")
                sys.exit()
            workspace = str(ResourcesConfiguration.getWorkspaceFile())
            logging.debug("The workspace: {0}".format(str(workspace)))
            # loading the workspace
            self.currentWorkspace = (Workspace.loadWorkspace(workspace))
            if self.currentWorkspace is None:
                logging.fatal("Stopping the execution (no workspace computed)!")
                sys.exit()

        self.currentProject = self.currentWorkspace.getLastProject()

        # Second we create the logging infrastructure
        LoggingConfiguration().initializeLogging(self.currentWorkspace)

        # Now we load all the available plugins
        NetzobPlugin.loadPlugins(self)

        # create logger with the given configuration
        self.log = logging.getLogger('netzob.py')
        self.log.info(_("Starting netzob"))

        # Main window definition
        try:
            #create window
            
                self.ressourceglade = str( ResourcesConfiguration.getStaticResources())
                self.builder = Gtk.Builder()
                self.builder.add_from_file(self.ressourceglade+"/ui/gtk3-2.3.glade")
                window = self.builder.get_object("window")
                window.show_all()
        except TypeError:
            Gtk.Window.__init__(self)
        #add menu
        self.addElement("box1","menu-vocabulary",0,False,False,True)
        self.addElement("box1","menu-grammar",0,False,False,False)
        self.addElement("box1","menu-traffic",0,False,False,False)
        
        #add toolbar
        self.addElement("box4","toolbar-vocabulary",0,True,True,True)
        self.addElement("box4","toolbar-grammar",0,True,True,False)
        self.addElement("box4","toolbar-traffic",0,True,True,False)
        
        #add toolbar style
        self.addToolbarStyle("toolbar-vocabulary")
        self.addToolbarStyle("toolbar-grammar")
        self.addToolbarStyle("toolbar-traffic")
        
        #add interface
        self.addElement("box1","interface-vocabulary",4,True,True,True)
        self.addElement("box1","interface-grammar",4,True,True,False)
        self.addElement("box1","interface-traffic",4,True,True,False)
                
        #combobox switch view
        combobox = self.builder.get_object("combobox1")
        combobox.set_active(0)    #see the default view "vocabulary" on the button
        combobox.connect("changed",self.combobox_changed_cb)
    
        #add 2 spreadsheet
        self.addSpreadSheet("Hello", 0)
        self.addSpreadSheet("ManualAjoutSymbol", 1)

        #load list symbol  
        pliste2 = self.getCurrentWorkspace().getProjects()        
        project = Project.loadProject(self.getCurrentWorkspace(), pliste2[2].getPath())
        symbols = project.getVocabulary().getSymbols()
        for sym in symbols:
            self.addRowSymbolList(False, sym.getName(), len(sym.getMessages()),  len(sym.getFields()), "imageProblem")
        
        #add select all button symbol list
        selectallbutton = self.builder.get_object("toolbutton1")
        selectallbutton.connect("clicked",self.button_selectAllSymbol_cb)
        
        #add unselect all button symbol list
        unselectallbutton = self.builder.get_object("toolbutton2")  
        unselectallbutton.connect("clicked",self.button_unSelectAllSymbol_cb)
         
        #create symbol
        createsymbolbutton = self.builder.get_object("toolbutton11")  
        createsymbolbutton.connect("clicked",self.button_createSymbol_cb)
        
              
        
        #run
        
        Gtk.main()


    #+----------------------------------------------
    #| Update each panels
    #+----------------------------------------------
    def update(self):
        for page in self.pageList:
            page[1].clear()
            page[1].update()

    #+----------------------------------------------
    #| Update the current panel
    #+----------------------------------------------
    def updateCurrentPanel(self):
        nameTab = (self.notebook.get_tab_label_text(
            self.notebook.get_nth_page(self.notebook.get_current_page())))
        for page in self.pageList:
            if page[0] == nameTab:
                page[1].update()

    def switchCurrentProject(self, project):
        self.log.debug(_("The current project is: {0}").format(project.getName()))
        self.currentProject = project
        for page in self.pageList:
            page[1].clear()
            page[1].update()
            page[1].new()
        self.update()

    def offerToSaveCurrentProject(self):
        questionMsg = (_("Do you want to save the current project (%s)") %
                       self.getCurrentProject().getName())
        md = (Gtk.MessageDialog(
            None, Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
            Gtk.MessageType.QUESTION, Gtk.ButtonsType.YES_NO, questionMsg))
        result = md.run()
        md.destroy()
        if result == Gtk.ResponseType.YES:
            logging.info("Saving the current project")
            self.getCurrentProject().saveConfigFile(self.getCurrentWorkspace())

    def startGui(self):
        Gtk.main()

    def evnmtDelete(self, widget, event, data=None):
        # Before exiting, we compute if its necessary to save
        # it means we simulate a save and compare the XML with the current one
        if (self.getCurrentProject() is not None and
            self.getCurrentProject().hasPendingModifications(
                self.getCurrentWorkspace())):
            self.offerToSaveCurrentProject()

        return False

    def destroy(self, widget, data=None):
        for page in self.pageList:
            page[1].kill()
        Gtk.main_quit()

    #+-------------   34       def callback(self, widget, data=None):---------------------------------
    #| Called when user select a notebook
    #+----------------------------------------------
    def notebookFocus(self, notebook, page, pagenum):
        nameTab = notebook.get_tab_label_text(notebook.get_nth_page(pagenum))
        for page in self.pageList:
            if page[0] == nameTab:
                page[1].update()

    def getCurrentProject(self):
        return self.currentProject

    def getCurrentWorkspace(self):
        return self.currentWorkspace

    def getMenu(self):
        return self.menu

    def getCurrentNotebookPage(self):
        res = None
        nameTab = (self.notebook.get_tab_label_text(self.notebook.get_nth_page(
            self.notebook.get_current_page())))
        for page in self.pageList:
            if page[0] == nameTab:
                res = page[1]
        return res
    
    def addElement(self,box,widget,position,expand,fill,visible):
        """
        Add an external widget on the builder 
        @type  box: string
        @param box: The hbox/vbox where add the widget
        @type  widget: string
        @param widget: The widget to add 
        @type  position: number
        @param position: The position to add the widget on the hbox/vbox
        @type  expand: gboolean
        @param expand: Set the expand properties
        """
        box = self.builder.get_object(box)
        widget = self.builder.get_object(widget)
        box.pack_start(widget, expand, fill, 0)
        box.reorder_child(widget, position) 
        if not visible:
            widget.hide()
            
    def addSpreadSheet(self,symbolname,position):
        """
        Add an external spreadsheet on the builder 
        @type  box: string
        @param box: The hbox/vbox where add the widget
        @type  widget: string
        @param widget: The widget to add 
        @type  position: number
        @param position: The position to add the widget on the hbox/vbox
        @type  expand: gboolean
        @param expand: Set the expand properties
        """
        #create a new builder to extract the widget
        builder2 = Gtk.Builder()
        builder2.add_from_file(self.ressourceglade+"/ui/gtk3-2.3.glade")
        #set the name of the symbol
        label = builder2.get_object("label1")
        label.set_text(symbolname)
        #add the spreadsheet to the main builder
        spreadsheet = builder2.get_object("spreadsheet")
        box = self.builder.get_object("box5")
        box.pack_start(spreadsheet, True, True, 0)
        box.reorder_child(spreadsheet, position) 
        #add the message for the treeview
        #add the close button
        #todo

    def switchWidget(self,widget,newwidget):
        """
        @type  widget: string
        @param widget: The widget actual to switch
        @type  newwidget: string
        @param newwidget: The new widget
        """
        widget= self.builder.get_object(widget)
        widget.hide()
        newwidget= self.builder.get_object(newwidget)
        newwidget.show()
    
    def addToolbarStyle(self,toolbar) :
        """
        @type  toolbar: string
        @param toolbar: The toolbar name
        """
        toolbar = self.builder.get_object(toolbar)
        styleContext = toolbar.get_style_context()
        styleContext.add_class("primary-toolbar")
    
    
    def switchView(self,newview):
        """
        @type  newview: string
        @param newview: Switch for the view. Value available: "vocabulary", "grammar" and "traffic"
        """
        global actualview
        self.switchWidget("menu-"+actualview,"menu-"+newview)
        self.switchWidget("toolbar-"+actualview,"toolbar-"+newview)
        self.switchWidget("interface-"+actualview,"interface-"+newview)
        actualview=newview
    
    def combobox_changed_cb(self,combobox):
        """
        callback to change the view
        @type  combobox: string
        @param combobox: self
        """
        index = combobox.get_active()
        if (index == 0):
            self.switchView("vocabulary")
        if (index == 1):
            self.switchView("grammar")
        if (index == 2):
            self.switchView("traffic")
            
    def addRowSymbolList(self,selection,name,message,field,image):
        """
        @type  selection: boolean
        @param selection: if selected symbol
        @type  name: string
        @param name: name of the symbol
        @type  message: string
        @param message: number of message in the symbol
        @type  field: string
        @param field: number of field in the symbol   
        @type  image: string
        @param image: image of the lock button (freeze partitioning)
        """
        model = self.builder.get_object("liststore1")
        i = model.append()
        model.set(i, 0, selection)
        model.set(i, 1, name)
        model.set(i, 2, message)
        model.set(i, 3, field)
        model.set(i, 4, image)

    def button_selectAllSymbol_cb(self,widget):
        """
        select all the symbol in the symbol list
        """
        model = self.builder.get_object("liststore1")
        #todo a continuer
        for s in model:
            s[0]= True
            
    def button_unSelectAllSymbol_cb(self,widget):
        """
        unselect all the symbol in the symbol list
        """
        model = self.builder.get_object("liststore1")
        #todo a continuer
        for s in model:
            s[0]= False
    
    def button_createSymbol_cb(self,widget):
        builder2 = Gtk.Builder()
        builder2.add_from_file(self.ressourceglade+"/ui/dialogbox.glade")
        createsymbol = self.builder.get_object("createsymbol")
        createsymbol.run()
        
        
  
>>>>>>> 5af44a1... Added more callbacks for symbol list toolbar
