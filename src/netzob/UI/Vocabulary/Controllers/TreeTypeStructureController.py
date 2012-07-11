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
import logging
from gi.repository import Gtk
import uuid

#+----------------------------------------------
#| Local Imports
#+----------------------------------------------
from netzob.Common.MMSTD.Dictionary.Memory import Memory
from netzob.UI.Vocabulary.Views.TreeTypeStructureView import TreeTypeStructureView
from netzob.Common.ProjectConfiguration import ProjectConfiguration


#+----------------------------------------------
#| TreeTypeStructureController:
#|     update and generates the treeview and its
#|     treestore dedicated to the type structure
#+----------------------------------------------
class TreeTypeStructureController(object):

    #+----------------------------------------------
    #| Constructor:
    #| @param vbox : where the treeview will be hold
    #+----------------------------------------------
    def __init__(self, netzob, vocabularyController):
        self.netzob = netzob
        self.vocabularyController = vocabularyController
        self.symbol = self.getSelectedSymbol()
        self.log = logging.getLogger('netzob.UI.Vocabulary.Controllers.TreeTypeStructureController.py')
        self.view = TreeTypeStructureView(self.netzob)
        self.initCallbacks()

    def initCallbacks(self):
        pass

    def getView(self):
        return self.view

    #+----------------------------------------------
    #| default:
    #|         Update the treestore in normal mode
    #+----------------------------------------------
    def update(self):
        if self.netzob.getCurrentProject() is not None:
            isActive = self.netzob.getCurrentProject().getConfiguration().getVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_DISPLAY_SYMBOL_STRUCTURE)
            if isActive:
                self.view.show()
            else:
                self.view.hide()
                return

        if self.getSelectedSymbol() is None:
            logging.debug("No symbol provided")
            self.clear()
            return

        self.view.treestore.clear()
        for field in self.getSelectedSymbol().getFields():
            tab = ""
            for k in range(field.getEncapsulationLevel()):
                tab += "        "
            if field.getName() == "__sep__":  # Do not show the delimiter fields
                continue

            # Define the background color
            if field.getBackgroundColor() is not None:
                backgroundColor = 'background="' + field.getBackgroundColor() + '"'
            else:
                backgroundColor = ""

            # Compute the associated variable (specified or automatically computed)
            variableDescription = "-"
            if field.getVariable() is not None:
                variableDescription = field.getVariable().getUncontextualizedDescription()
            elif field.getDefaultVariable(self.getSelectedSymbol()) is not None:
                variableDescription = field.getDefaultVariable(self.getSelectedSymbol()).getUncontextualizedDescription()

            self.view.treestore.append(None, [field.getIndex(), tab + field.getName() + ":", field.getDescription(), '<span ' + backgroundColor + ' font_family="monospace">' + variableDescription + '</span>'])

    #+----------------------------------------------
    #| initialization:
    #| builds and configures the treeview
    #+----------------------------------------------
    def initialization(self):
        # creation of the treestore
        self.view.treestore = Gtk.TreeStore(int, str, str, str)  # iCol, Name, Description, Variable
        # creation of the treeview
        self.view.treeview = Gtk.TreeView(self.view.treestore)
        self.view.treeview.set_reorderable(True)
        # Creation of a cell rendered and of a column
        cell = Gtk.CellRendererText()
        cell.set_property("size-points", 9)
        columns = [_("iCol"), _("Name"), _("Description"), _("Variable")]
        for i in range(1, len(columns)):
            column = Gtk.TreeViewColumn(columns[i])
            column.set_resizable(True)
            column.pack_start(cell, True)
            column.add_attribute(cell, "markup", i)
            self.view.treeview.append_column(column)
        self.view.treeview.show()
        self.view.treeview.get_selection().set_mode(Gtk.SelectionMode.MULTIPLE)
        self.scroll = Gtk.ScrolledWindow()
        self.scroll.set_size_request(-1, 250)
        self.scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.scroll.add(self.view.treeview)
        self.scroll.show()

    #+----------------------------------------------
    #| clear:
    #|         Clear the class
    #+----------------------------------------------
    def clear(self):
        self.symbol = None
        self.view.treestore.clear()

    #+----------------------------------------------
    #| error:
    #|         Update the treestore in error mode
    #+----------------------------------------------
    def error(self):
        self.log.warning(_("The treeview for the symbol is in error mode"))
        # TODO : delete pass statement if useless
        #pass

    #+----------------------------------------------
    #| button_press_on_treeview_typeStructure:
    #|   operation when the user click on the treeview.
    #|   mainly to open a contextual menu
    #+----------------------------------------------
    def button_press_on_treeview_typeStructure(self, treeview, event):
        # Popup a menu
        if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 3:
            self.log.debug(_("User requested a contextual menu (on treeview typeStructure)"))
            x = int(event.x)
            y = int(event.y)
            (path, treeviewColumn, x, y) = treeview.get_path_at_pos(x, y)
            (iField,) = path

            selectedField = None
            for field in self.vocabularyController.treeMessageController.getSymbol().getFields():
                if field.getIndex() == iField:
                    selectedField = field
            if selectedField is None:
                self.log.warn(_("Impossible to retrieve the clicked field!"))
                return

            self.menu = Gtk.Menu()

            # Add entry to edit field
            item = Gtk.MenuItem(_("Edit field"))
            item.show()
            item.connect("activate", self.displayPopupToEditField, selectedField)
            self.menu.append(item)

            # Add sub-entries to change the type of a specific field
            subMenu = self.build_encoding_submenu(selectedField, None)
            item = Gtk.MenuItem(_("Field visualization"))
            item.set_submenu(subMenu)
            item.show()
            self.menu.append(item)

            # Add entries to concatenate fields
            concatMenu = Gtk.Menu()
            item = Gtk.MenuItem(_("with precedent field"))
            item.show()
            item.connect("activate", self.rightClickToConcatColumns, selectedField, "left")
            concatMenu.append(item)
            item = Gtk.MenuItem(_("with all precedent field"))
            item.show()
            item.connect("activate", self.rightClickToConcatColumns, selectedField, "allleft")
            concatMenu.append(item)

            item = Gtk.MenuItem(_("with next field"))
            item.show()
            item.connect("activate", self.rightClickToConcatColumns, selectedField, "right")
            concatMenu.append(item)
            item = Gtk.MenuItem(_("with all next field"))
            item.show()
            item.connect("activate", self.rightClickToConcatColumns, selectedField, "allright")
            concatMenu.append(item)

            item = Gtk.MenuItem(_("personalize selection"))
            item.show()
            item.connect("activate", self.ConcatChosenColumns)
            concatMenu.append(item)

            item = Gtk.MenuItem(_("Concatenate field"))
            item.set_submenu(concatMenu)
            item.show()
            self.menu.append(item)

            # Add entry to split the field
            item = Gtk.MenuItem(_("Split field"))
            item.show()
            item.connect("activate", self.rightClickToSplitColumn, selectedField)
            self.menu.append(item)

            # Add entry to retrieve the field domain of definition
            item = Gtk.MenuItem(_("Field's domain of definition"))
            item.show()
            item.connect("activate", self.rightClickDomainOfDefinition, selectedField)
            self.menu.append(item)

            # Add sub-entries to change the variable of a specific column
            if selectedField.getVariable() is None:
                typeMenuVariable = Gtk.Menu()
                itemVariable = Gtk.MenuItem(_("Create a variable"))
                itemVariable.show()
                itemVariable.connect("activate", self.rightClickCreateVariable, self.vocabularyController.treeMessageController.getSymbol(), selectedField)
                typeMenuVariable.append(itemVariable)
            else:
                typeMenuVariable = Gtk.Menu()
                itemVariable = Gtk.MenuItem(_("Edit variable"))
                itemVariable.show()
                itemVariable.connect("activate", self.rightClickEditVariable, selectedField)
                typeMenuVariable.append(itemVariable)

            if selectedField.getVariable() is not None:
                itemVariable3 = Gtk.MenuItem(_("Remove variable"))
                itemVariable3.show()
                itemVariable3.connect("activate", self.rightClickRemoveVariable, selectedField)
                typeMenuVariable.append(itemVariable3)

            item = Gtk.MenuItem(_("Configure variation of field"))
            item.set_submenu(typeMenuVariable)
            item.show()
            self.menu.append(item)

            # Add entry to export fields
            item = Gtk.MenuItem(_("Export selected fields"))
            item.show()
            item.connect("activate", self.exportSelectedFields_cb)
            self.menu.append(item)

            self.menu.popup(None, None, None, None, event.button, event.time)

    #+----------------------------------------------
    #| exportSelectedFields_cb:
    #|   Callback to export the selected fields
    #|   as a new trace
    #+----------------------------------------------
    def exportSelectedFields_cb(self, event):
        # Retrieve associated messages of selected fields
        aggregatedCells = {}
        (model, paths) = self.getTreeview().get_selection().get_selected_rows()
        for path in paths:
            aIter = model.get_iter(path)
            if(model.iter_is_valid(aIter)):
                iField = model.get_value(aIter, 0)

                selectedField = None
                for field in self.vocabularyController.treeMessageController.getSymbol().getFields():
                    if field.getIndex() == iField:
                        selectedField = field
                if selectedField is None:
                    self.log.warn(_("Impossible to retrieve the clicked field !"))
                    return

                cells = self.getSelectedSymbol().getCellsByField(selectedField)
                for i in range(len(cells)):
                    if not i in aggregatedCells:
                        aggregatedCells[i] = ""
                    aggregatedCells[i] += str(cells[i])

        # Popup a menu to save the data
        dialog = Gtk.Dialog(title=_("Save selected data"), flags=0, buttons=None)
        dialog.show()
        table = Gtk.Table(rows=2, columns=3, homogeneous=False)
        table.show()

        # Add to an existing trace
        label = NetzobLabel(_("Add to an existing trace"))
        entry = Gtk.ComboBoxText.new_with_entry()
        entry.show()
        entry.set_size_request(300, -1)
        entry.set_model(Gtk.ListStore(str))
        projectsDirectoryPath = self.netzob.getCurrentWorkspace().getPath() + os.sep + "projects" + os.sep + self.netzob.getCurrentProject().getPath()
        for tmpDir in os.listdir(projectsDirectoryPath):
            if tmpDir == '.svn':
                continue
            entry.append_text(tmpDir)
        but = NetzobButton(_("Save"))
        but.connect("clicked", self.add_packets_to_existing_trace, entry, aggregatedCells, dialog)
        table.attach(label, 0, 1, 0, 1, xoptions=0, yoptions=0, xpadding=5, ypadding=5)
        table.attach(entry, 1, 2, 0, 1, xoptions=0, yoptions=0, xpadding=5, ypadding=5)
        table.attach(but, 2, 3, 0, 1, xoptions=0, yoptions=0, xpadding=5, ypadding=5)

        # Create a new trace
        label = NetzobLabel(_("Create a new trace"))
        entry = Gtk.Entry()
        entry.show()
        but = NetzobButton(_("Save"))
        but.connect("clicked", self.create_new_trace, entry, aggregatedCells, dialog)
        table.attach(label, 0, 1, 1, 2, xoptions=0, yoptions=0, xpadding=5, ypadding=5)
        table.attach(entry, 1, 2, 1, 2, xoptions=0, yoptions=0, xpadding=5, ypadding=5)
        table.attach(but, 2, 3, 1, 2, xoptions=0, yoptions=0, xpadding=5, ypadding=5)

        dialog.action_area.pack_start(table, True, True, 0)

    #+----------------------------------------------
    #| Add a selection of packets to an existing trace
    #+----------------------------------------------
    def add_packets_to_existing_trace(self, button, entry, messages, dialog):
        logging.warn("Not yet implemented")
        return

        # projectsDirectoryPath = self.netzob.getCurrentWorkspace().getPath() + os.sep + "projects" + os.sep + self.netzob.getCurrentProject().getPath()
        # existingTraceDir = projectsDirectoryPath + os.sep + entry.get_active_text()
        # # Create the new XML structure
        # res = "<datas>\n"
        # for message in messages:
        #     res += "<data proto=\"ipc\" sourceIp=\"local\" sourcePort=\"local\" targetIp=\"local\" targetPort=\"local\" timestamp=\"" + str(time.time()) + "\">\n"
        #     res += message + "\n"
        #     res += "</data>\n"
        # res += "</datas>\n"
        # # Dump into a random XML file
        # fd = open(existingTraceDir + os.sep + str(random.randint(100000, 9000000)) + ".xml"  , "w")
        # fd.write(res)
        # fd.close()
        # dialog.destroy()

    #+----------------------------------------------
    #| Creation of a new trace from a selection of packets
    #+----------------------------------------------
    def create_new_trace(self, button, entry, messages, dialog):
        logging.warn(_("Not yet implemented"))
        return

        # projectsDirectoryPath = self.netzob.getCurrentWorkspace().getPath() + os.sep + "projects" + os.sep + self.netzob.getCurrentProject().getPath()
        # for tmpDir in os.listdir(projectsDirectoryPath):
        #     if tmpDir == '.svn':
        #         continue
        #     if entry.get_text() == tmpDir:
        #         dialogBis = Gtk.Dialog(title="This trace already exists", flags=0, buttons=None)
        #         dialogBis.set_size_request(250, 50)
        #         dialogBis.show()
        #         return

        # # Create the dest Dir
        # newTraceDir = projectsDirectoryPath + os.sep + entry.get_text()
        # os.mkdir(newTraceDir)
        # # Create the new XML structure
        # res = "<datas>\n"
        # for message in messages.values():
        #     res += "<data proto=\"ipc\" sourceIp=\"local\" sourcePort=\"local\" targetIp=\"local\" targetPort=\"local\" timestamp=\"" + str(time.time()) + "\">\n"
        #     res += message + "\n"
        #     res += "</data>\n"
        # res += "</datas>\n"
        # # Dump into a random XML file
        # fd = open(newTraceDir + os.sep + str(random.randint(100000, 9000000)) + ".xml"  , "w")
        # fd.write(res)
        # fd.close()
        # dialog.destroy()
        # self.netzob.updateListOfAvailableProjects()

    #+----------------------------------------------
    #| GETTERS:
    #+----------------------------------------------
    def getTreeview(self):
        return self.view.treeview

    def getScrollLib(self):
        return self.view.scroll

    def getWidget(self):
        return self.view.scroll

    def getSelectedSymbol(self):
        return self.vocabularyController.treeSymbolController.selectedSymbol

    #+----------------------------------------------
    #| SETTERS:
    #+----------------------------------------------
    def setTreeview(self, treeview):
        self.view.treeview = treeview

    def setScrollLib(self, scroll):
        self.view.scroll = scroll

    def setSymbol(self, symbol):
        self.symbol = symbol
