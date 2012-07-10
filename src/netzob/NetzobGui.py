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
from netzob.Common.Plugins.NetzobPlugin import NetzobPlugin
from netzob.Common.Plugins.ImporterPlugin import ImporterPlugin
gi.require_version('Gtk', '3.0')
from gi.repository import GObject
import threading
import sys
import logging
import optparse

import locale
import gettext

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common import DepCheck
from netzob.Common.Menu import Menu
from netzob.Inference.Vocabulary.UImodelization import UImodelization
from netzob.Inference.Grammar.UIGrammarInference import UIGrammarInference
from netzob.Common.LoggingConfiguration import LoggingConfiguration
from netzob.Simulator.UISimulator import UISimulator
from netzob.Common.ResourcesConfiguration import ResourcesConfiguration
from netzob.Common.Workspace import Workspace
from netzob.Common import CommandLine


#+----------------------------------------------
#| NetzobGUI:
#|     Graphical runtime class
#+----------------------------------------------
class NetzobGui(Gtk.Window):

    #+----------------------------------------------
    #| Constructor:
    #+----------------------------------------------
    def __init__(self):

        # Command line commands
        parser = CommandLine.get_parser()
        opts, args = parser.parse_args()

        gettext.bindtextdomain("netzob", ResourcesConfiguration.getLocaleLocation())
        gettext.textdomain("netzob")

        try:
            locale.getlocale()
        except:
            logging.exception("setlocale failed, resetting to C")
            locale.setlocale(locale.LC_ALL, "C")

        # First we initialize and verify all the resources
        if not ResourcesConfiguration.initializeResources():
            logging.fatal("Error while configuring the resources of Netzob")
            sys.exit()

        if opts.workspace == None:
            workspace = str(ResourcesConfiguration.getWorkspaceFile())
        else:
            workspace = opts.workspace

        logging.debug("The workspace: {0}".format(str(workspace)))

        # loading the workspace
        self.currentWorkspace = (Workspace.loadWorkspace(workspace))

        # the semi-automatic loading of the workspace has failed (second attempt)
        if self.currentWorkspace == None:
            # we force the creation (or specification) of the workspace
            if not ResourcesConfiguration.initializeResources(True):
                logging.fatal("Error while configuring the resources of Netzob")
                sys.exit()
            workspace = str(ResourcesConfiguration.getWorkspaceFile())
            logging.debug("The workspace: {0}".format(str(workspace)))
            # loading the workspace
            self.currentWorkspace = (Workspace.loadWorkspace(workspace))
            if self.currentWorkspace == None:
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
            Gtk.Window.__init__(self, Gtk.WindowType.TOPLEVEL)
        except TypeError:
            Gtk.Window.__init__(self)

        self.set_default_size(800, 600)
        self.set_title(_("Netzob: Inferring communication protocols"))

        self.set_icon_from_file(("%s/logo.png" %
                                 ResourcesConfiguration.getStaticResources()))
        self.connect("delete_event", self.evnmtDelete)
        self.connect("destroy", self.destroy)
        main_vbox = Gtk.VBox(False, spacing=0)

        # Create and display the menu

        self.menu = Menu(self)
        menubar = self.menu.getMenuBar(self)
        menubar.show()
        self.menu.update()
        main_vbox.pack_start(menubar, False, True, 0)

        # Notebook definition
        self.notebook = Gtk.Notebook()
        self.notebook.set_tab_pos(Gtk.PositionType.TOP)
        self.notebook.connect("switch-page", self.notebookFocus)
        main_vbox.pack_start(self.notebook, True, True, 0)

        self.pageList = []
        # Adding the different notebook
        self.modelization = UImodelization(self)
        self.grammarInference = UIGrammarInference(self)
#        self.fuzzing = UIfuzzing(self)
        self.simulator = UISimulator(self)

        self.pageList.append([_("Vocabulary inference"), self.modelization])
        self.pageList.append([_("Grammar inference"), self.grammarInference])
#        self.pageList.append(["Fuzzing", self.fuzzing])
        self.pageList.append([_("Simulator"), self.simulator])

        for page in self.pageList:
            self.notebook.append_page(page[1].panel, Gtk.Label(label=page[0]))

        # Initialize a clipboard object
        self.clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)

        # Show every widgets
        self.notebook.show()
        main_vbox.show()
        self.add(main_vbox)
        self.show()

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
        if (self.getCurrentProject() != None and
            self.getCurrentProject().hasPendingModifications(
                self.getCurrentWorkspace())):
            self.offerToSaveCurrentProject()

        return False

    def destroy(self, widget, data=None):
        for page in self.pageList:
            page[1].kill()
        Gtk.main_quit()

    #+----------------------------------------------
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
