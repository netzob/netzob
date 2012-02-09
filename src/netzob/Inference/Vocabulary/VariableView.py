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
import logging
import gtk
import pygtk
import uuid
from netzob.Common.MMSTD.Dictionary.Variables.AggregateVariable import AggregateVariable
from netzob.Common.MMSTD.Dictionary.Variables.WordVariable import WordVariable
from netzob.Common.MMSTD.Dictionary.Variables.AlternateVariable import AlternateVariable
from netzob.Common.MMSTD.Dictionary.Variables.ReferencedVariable import ReferencedVariable
pygtk.require('2.0')

#+----------------------------------------------
#| Local Imports
#+----------------------------------------------


#+----------------------------------------------
#| VariableView:
#|     Class dedicated to host the creation of a variable
#+----------------------------------------------
class VariableView(object):

    #+----------------------------------------------
    #| Constructor:
    #+----------------------------------------------
    def __init__(self, netzob, field, variableId, variableName, variableIsMutable):
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Inference.Vocabulary.VariableView.py')
        self.netzob = netzob
        self.project = self.netzob.getCurrentProject()
        self.varId = variableId
        self.varName = variableName
        self.varIsMutable = variableIsMutable
        self.field = field

        # Add the initial Aggregate
        self.rootVariable = AggregateVariable(self.varId, self.varName, None)
        self.datas = dict()
        self.datas[str(self.rootVariable.getID())] = self.rootVariable

    def display(self):
        # We display the dedicated dialog for the creation of a variable
        self.dialog = gtk.Dialog(title="Creation of a variable", flags=0, buttons=None)

        # Create the main panel
        self.panel = gtk.Table(rows=2, columns=3, homogeneous=False)

        self.treestore = gtk.TreeStore(str, str)  # id of the data, description
        self.treeview = gtk.TreeView(self.treestore)
        self.treeview.connect('button-press-event', self.showMenu)
        # messages list
        self.scroll = gtk.ScrolledWindow()
        self.scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.scroll.show()
        self.scroll.set_size_request(200, 300)
        self.scroll.add(self.treeview)
        self.scroll.show()

        self.lvcolumn = gtk.TreeViewColumn('Description of the variable')
        self.lvcolumn.set_sort_column_id(1)
        cell = gtk.CellRendererText()
        self.lvcolumn.pack_start(cell, True)
        self.lvcolumn.set_attributes(cell, text=1)
        self.treeview.append_column(self.lvcolumn)
        self.treeview.show()

        self.panel.attach(self.scroll, 0, 2, 0, 2, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        self.panel.show()

        # Create button
        createButton = gtk.Button("Create")
        createButton.show()
        createButton.connect("clicked", self.createVariable)

        self.panel.attach(createButton, 0, 2, 2, 3, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        self.treestore.append(None, [str(self.rootVariable.getID()), "Root"])

        self.dialog.vbox.pack_start(self.panel, True, True, 0)
        self.dialog.show()

    def createVariable(self, button):

        # We register the root variable as the variable of specified field
        self.field.setVariable(self.rootVariable)
        self.dialog.destroy()

        # Update UI
        page = self.netzob.getCurrentNotebookPage()
        if page != None:
            page.update()

    def showMenu(self, treeview, event):
        target = treeview.get_path_at_pos(int(event.x), int(event.y))
        rootVariable = None
        if event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
            x = int(event.x)
            y = int(event.y)
            (path, treeviewColumn, x, y) = treeview.get_path_at_pos(x, y)

            # Retrieve the selected variable
            variable_id = None
            aIter = treeview.get_model().get_iter(path)
            if aIter:
                if treeview.get_model().iter_is_valid(aIter):
                    variable_id = treeview.get_model().get_value(aIter, 0)

                    for varid in self.datas.keys():
                        if varid == variable_id:
                            rootVariable = self.datas[varid]

        if rootVariable == None:
            self.log.debug("Impossible to find the selected variable.")
            return

        # We display the menu for the insertion of sub-elements if its an Aggregate or an Alternative
        menu = gtk.Menu()

        subElementMenu = gtk.Menu()

        # Word Variable
        itemWord = gtk.MenuItem("Word")
        itemWord.show()
        itemWord.connect("activate", self.addWord, rootVariable, aIter)
        subElementMenu.append(itemWord)

        # Binary Variable
        itemBinary = gtk.MenuItem("Binary")
        itemBinary.show()
        itemBinary.connect("activate", self.addBinary, rootVariable, aIter)
        subElementMenu.append(itemBinary)

        # Aggregate Variable
        itemAggregate = gtk.MenuItem("Aggregate")
        itemAggregate.show()
        itemAggregate.connect("activate", self.addAggregate, rootVariable, aIter)
        subElementMenu.append(itemAggregate)

        # Alternate Variable
        itemAlternate = gtk.MenuItem("Alternative")
        itemAlternate.show()
        itemAlternate.connect("activate", self.addAlternate, rootVariable, aIter)
        subElementMenu.append(itemAlternate)

        # Referenced Variable
        itemAlternate = gtk.MenuItem("Referenced Variable")
        itemAlternate.show()
        itemAlternate.connect("activate", self.addReferencedVariable, rootVariable, aIter)
        subElementMenu.append(itemAlternate)

        item = gtk.MenuItem("Add a sub-element")
        item.set_submenu(subElementMenu)
        item.show()

        menu.append(item)
        menu.popup(None, None, None, event.button, event.time)

    def addBinary(self, event, rootVariable, rootEntry):
        pass
    def addAlternate(self, event, rootVariable, rootEntry):
        # Display the form for the creation of a word variable
        dialog = gtk.MessageDialog(None, gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_QUESTION, gtk.BUTTONS_OK, None)
        dialog.set_markup('Definition of the Alternative')

        # Create the ID of the new variable
        variableID = str(uuid.uuid4())

        mainTable = gtk.Table(rows=3, columns=2, homogeneous=False)
        # parent id of the variable
        variablePIDLabel = gtk.Label("Parent ID :")
        variablePIDLabel.show()
        variablePIDValueLabel = gtk.Label(str(rootVariable.getID()))
        variablePIDValueLabel.set_sensitive(False)
        variablePIDValueLabel.show()
        mainTable.attach(variablePIDLabel, 0, 1, 0, 1, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        mainTable.attach(variablePIDValueLabel, 1, 2, 0, 1, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        # id of the variable
        variableIDLabel = gtk.Label("ID :")
        variableIDLabel.show()
        variableIDValueLabel = gtk.Label(variableID)
        variableIDValueLabel.set_sensitive(False)
        variableIDValueLabel.show()
        mainTable.attach(variableIDLabel, 0, 1, 1, 2, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        mainTable.attach(variableIDValueLabel, 1, 2, 1, 2, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        # name of the variable
        variableValueLabel = gtk.Label("Name : ")
        variableValueLabel.show()
        variableValueEntry = gtk.Entry()
        variableValueEntry.show()
        mainTable.attach(variableValueLabel, 0, 1, 2, 3, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        mainTable.attach(variableValueEntry, 1, 2, 2, 3, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        dialog.vbox.pack_end(mainTable, True, True, 0)
        dialog.show_all()
        result = dialog.run()

        if result != gtk.RESPONSE_OK:
            dialog.destroy()
            return

        # We retrieve the name of the variable
        varName = variableValueEntry.get_text()

        # Creation of the aggregate id, name, mutable, value):
        alternateVariable = AlternateVariable(variableID, varName, None)
        rootVariable.addChild(alternateVariable)

        self.datas[str(alternateVariable.getID())] = alternateVariable

        self.treestore.append(rootEntry, [str(alternateVariable.getID()), "Alternate"])

        # We close the current dialog
        dialog.destroy()
    def addAggregate(self, event, rootVariable, rootEntry):
        # Display the form for the creation of a word variable
        dialog = gtk.MessageDialog(None, gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_QUESTION, gtk.BUTTONS_OK, None)
        dialog.set_markup('Definition of the Aggregate')

        # Create the ID of the new variable
        variableID = str(uuid.uuid4())

        mainTable = gtk.Table(rows=3, columns=2, homogeneous=False)
        # parent id of the variable
        variablePIDLabel = gtk.Label("Parent ID :")
        variablePIDLabel.show()
        variablePIDValueLabel = gtk.Label(str(rootVariable.getID()))
        variablePIDValueLabel.set_sensitive(False)
        variablePIDValueLabel.show()
        mainTable.attach(variablePIDLabel, 0, 1, 0, 1, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        mainTable.attach(variablePIDValueLabel, 1, 2, 0, 1, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        # id of the variable
        variableIDLabel = gtk.Label("ID :")
        variableIDLabel.show()
        variableIDValueLabel = gtk.Label(variableID)
        variableIDValueLabel.set_sensitive(False)
        variableIDValueLabel.show()
        mainTable.attach(variableIDLabel, 0, 1, 1, 2, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        mainTable.attach(variableIDValueLabel, 1, 2, 1, 2, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        # name of the variable
        variableValueLabel = gtk.Label("Name : ")
        variableValueLabel.show()
        variableValueEntry = gtk.Entry()
        variableValueEntry.show()
        mainTable.attach(variableValueLabel, 0, 1, 2, 3, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        mainTable.attach(variableValueEntry, 1, 2, 2, 3, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        dialog.vbox.pack_end(mainTable, True, True, 0)
        dialog.show_all()
        result = dialog.run()

        if result != gtk.RESPONSE_OK:
            dialog.destroy()
            return

        # We retrieve the name of the variable
        varName = variableValueEntry.get_text()

        # Creation of the aggregate id, name, mutable, value):
        aggregateVariable = AggregateVariable(variableID, varName, None)
        rootVariable.addChild(aggregateVariable)

        self.datas[str(aggregateVariable.getID())] = aggregateVariable

        self.treestore.append(rootEntry, [str(aggregateVariable.getID()), "Aggregate"])

        # We close the current dialog
        dialog.destroy()

    def addWord(self, event, rootVariable, rootEntry):
        # Display the form for the creation of a word variable
        dialog = gtk.MessageDialog(None, gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_QUESTION, gtk.BUTTONS_OK, None)
        dialog.set_markup('Definition of the WORD')

        # Create the ID of the new variable
        variableID = str(uuid.uuid4())

        mainTable = gtk.Table(rows=3, columns=2, homogeneous=False)
        # parent id of the variable
        variablePIDLabel = gtk.Label("Parent ID :")
        variablePIDLabel.show()
        variablePIDValueLabel = gtk.Label(str(rootVariable.getID()))
        variablePIDValueLabel.set_sensitive(False)
        variablePIDValueLabel.show()
        mainTable.attach(variablePIDLabel, 0, 1, 0, 1, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        mainTable.attach(variablePIDValueLabel, 1, 2, 0, 1, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        # id of the variable
        variableIDLabel = gtk.Label("ID :")
        variableIDLabel.show()
        variableIDValueLabel = gtk.Label(variableID)
        variableIDValueLabel.set_sensitive(False)
        variableIDValueLabel.show()
        mainTable.attach(variableIDLabel, 0, 1, 1, 2, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        mainTable.attach(variableIDValueLabel, 1, 2, 1, 2, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        # value of the variable
        variableValueLabel = gtk.Label("Value : ")
        variableValueLabel.show()
        variableValueEntry = gtk.Entry()
        variableValueEntry.show()
        mainTable.attach(variableValueLabel, 0, 1, 2, 3, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        mainTable.attach(variableValueEntry, 1, 2, 2, 3, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        dialog.vbox.pack_end(mainTable, True, True, 0)
        dialog.show_all()
        result = dialog.run()

        if result != gtk.RESPONSE_OK:
            dialog.destroy()
            return

        # We retrieve the value of the variable
        varValue = variableValueEntry.get_text()

        # Creation of the word id, name, mutable, value):
        wordVariable = WordVariable(variableID, varValue, False, varValue)
        rootVariable.addChild(wordVariable)

        self.datas[str(wordVariable.getID())] = wordVariable

        self.treestore.append(rootEntry, [str(wordVariable.getID()), wordVariable.getDescription()])

        # We close the current dialog
        dialog.destroy()

    def addReferencedVariable(self, event, rootVariable, rootEntry):
        # Display the form for the creation of a word variable
        dialog = gtk.MessageDialog(None, gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_QUESTION, gtk.BUTTONS_OK, None)
        dialog.set_markup('Definition of the ReferencedVariable')

        # Create the ID of the new variable
        variableID = str(uuid.uuid4())

        mainTable = gtk.Table(rows=3, columns=2, homogeneous=False)
        # parent id of the variable
        variablePIDLabel = gtk.Label("Parent ID :")
        variablePIDLabel.show()
        variablePIDValueLabel = gtk.Label(str(rootVariable.getID()))
        variablePIDValueLabel.set_sensitive(False)
        variablePIDValueLabel.show()
        mainTable.attach(variablePIDLabel, 0, 1, 0, 1, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        mainTable.attach(variablePIDValueLabel, 1, 2, 0, 1, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        # id of the variable
        variableIDLabel = gtk.Label("ID :")
        variableIDLabel.show()
        variableIDValueLabel = gtk.Label(variableID)
        variableIDValueLabel.set_sensitive(False)
        variableIDValueLabel.show()
        mainTable.attach(variableIDLabel, 0, 1, 1, 2, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        mainTable.attach(variableIDValueLabel, 1, 2, 1, 2, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        # Selection of the variable
        varLabel = gtk.Label("Referenced Variable :")
        varLabel.show()
        self.varCombo = gtk.combo_box_entry_new_text()
        self.varCombo.show()
        self.varStore = gtk.ListStore(str, str)  # description, id,
        self.varCombo.set_model(self.varStore)

        # We retrieve all the existing variables in the project
        existingVariables = self.project.getVocabulary().getVariables()
        for existingVariable in existingVariables:
            self.varCombo.get_model().append([existingVariable.getDescription(), existingVariable.getID()])

        mainTable.attach(varLabel, 0, 1, 2, 3, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        mainTable.attach(self.varCombo, 1, 2, 2, 3, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        dialog.vbox.pack_end(mainTable, True, True, 0)
        dialog.show_all()
        result = dialog.run()

        if result != gtk.RESPONSE_OK:
            dialog.destroy()
            return

        idReferencedVariable = self.varCombo.get_model().get_value(self.varCombo.get_active_iter(), 1)

        referencedVariable = ReferencedVariable(uuid.uuid4(), "Ref", True, idReferencedVariable)
        rootVariable.addChild(referencedVariable)

        self.datas[str(referencedVariable.getID())] = referencedVariable
        self.treestore.append(rootEntry, [str(referencedVariable.getID()), referencedVariable.getDescription()])

        # We close the current dialog
        dialog.destroy()
