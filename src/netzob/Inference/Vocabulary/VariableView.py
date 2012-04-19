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
from netzob.Common.MMSTD.Dictionary.Variables.IPv4Variable import IPv4Variable
from netzob.Common.Type.Format import Format
from netzob.Common.MMSTD.Dictionary.Variables.BinaryVariable import BinaryVariable
from netzob.Common.MMSTD.Dictionary.Variables.HexVariable import HexVariable
from netzob.Common.MMSTD.Dictionary.Variables.DecimalWordVariable import DecimalWordVariable
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
    def __init__(self, netzob, field, variableId, variableName, defaultValue=None):
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Inference.Vocabulary.VariableView.py')
        self.netzob = netzob
        self.project = self.netzob.getCurrentProject()
        self.varId = variableId
        self.varName = variableName
        self.field = field
        self.defaultValue = defaultValue
        self.datas = dict()

        # Add the initial Aggregate
        self.rootVariable = AggregateVariable(variableId, self.varName, None)
        if self.defaultValue != None:
            self.rootVariable.addChild(self.defaultValue)

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

        # We register the default values
        self.registerVariable(None, self.rootVariable, "Root")

    def registerVariable(self, rootEntry, variable, name):
        self.log.debug("Register : " + str(name))
        self.datas[str(variable.getID())] = variable
        newEntry = self.treestore.append(rootEntry, [str(variable.getID()), name])
        if variable.getTypeVariable() == AggregateVariable.TYPE or variable.getTypeVariable() == AlternateVariable.TYPE:
            for child in variable.getChildren():
                self.registerVariable(newEntry, child, child.getName())

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

        # Decimal Word Variable
        itemDecimalWord = gtk.MenuItem("Decimal Word")
        itemDecimalWord.show()
        itemDecimalWord.connect("activate", self.addDecimalWord, rootVariable, aIter)
        subElementMenu.append(itemDecimalWord)

        # IPv4 Variable
        itemIPv4 = gtk.MenuItem("IPv4")
        itemIPv4.show()
        itemIPv4.connect("activate", self.addIPv4, rootVariable, aIter)
        subElementMenu.append(itemIPv4)

        # Binary Variable
        itemBinary = gtk.MenuItem("Binary")
        itemBinary.show()
        itemBinary.connect("activate", self.addBinary, rootVariable, aIter)
        subElementMenu.append(itemBinary)

        # Hexadecimal Variable
        itemBinary = gtk.MenuItem("Hexadecimal")
        itemBinary.show()
        itemBinary.connect("activate", self.addHexadecimal, rootVariable, aIter)
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
        # Display the form for the creation of a Binary variable
        dialog = gtk.MessageDialog(None, gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_QUESTION, gtk.BUTTONS_OK, None)
        dialog.set_markup('Definition of the Binary Variable')

        # Create the ID of the new variable
        varID = uuid.uuid4()
        variableID = str(varID)

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

        # Original Value
        originalValueLabel = gtk.Label("Original value : ")
        originalValueLabel.show()
        originalValueEntry = gtk.Entry()
        originalValueEntry.show()
        mainTable.attach(originalValueLabel, 0, 1, 2, 3, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        mainTable.attach(originalValueEntry, 1, 2, 2, 3, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        # Constraints label
        constraintsLabel = gtk.Label("Constraints when parsing / generating")
        constraintsLabel.show()
        mainTable.attach(constraintsLabel, 0, 2, 3, 4, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        # start Value
        minBitsLabel = gtk.Label("Minimum number of bits : ")
        minBitsLabel.show()
        minBitsEntry = gtk.Entry()
        minBitsEntry.show()
        mainTable.attach(minBitsLabel, 0, 1, 4, 5, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        mainTable.attach(minBitsEntry, 1, 2, 4, 5, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        # end Value
        maxBitsLabel = gtk.Label("Maximum number of bits : ")
        maxBitsLabel.show()
        maxBitsEntry = gtk.Entry()
        maxBitsEntry.show()
        mainTable.attach(maxBitsLabel, 0, 1, 5, 6, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        mainTable.attach(maxBitsEntry, 1, 2, 5, 6, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        dialog.vbox.pack_end(mainTable, True, True, 0)
        dialog.show_all()
        result = dialog.run()

        if result != gtk.RESPONSE_OK:
            dialog.destroy()
            return

        # Creation of the variable (binary)
        # original value :
        originalValue = originalValueEntry.get_text()
        if len(originalValue) == 0:
            originalValue = None

        # constraints
        minSize = int(minBitsEntry.get_text())
        maxSize = int(maxBitsEntry.get_text())

        binVariable = BinaryVariable(varID, "binary", originalValue, minSize, maxSize)
        rootVariable.addChild(binVariable)

        self.datas[str(binVariable.getID())] = binVariable

        self.treestore.append(rootEntry, [str(binVariable.getID()), binVariable.getUncontextualizedDescription()])

        # We close the current dialog
        dialog.destroy()

    def addHexadecimal(self, event, rootVariable, rootEntry):
        # Display the form for the creation of an Hexadecimal variable
        dialog = gtk.MessageDialog(None, gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_QUESTION, gtk.BUTTONS_OK, None)
        dialog.set_markup('Definition of the Hexadecimal Variable')

        # Create the ID of the new variable
        varID = uuid.uuid4()
        variableID = str(varID)

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

        # Original Value
        originalValueLabel = gtk.Label("Original value : ")
        originalValueLabel.show()
        originalValueEntry = gtk.Entry()
        originalValueEntry.show()
        mainTable.attach(originalValueLabel, 0, 1, 2, 3, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        mainTable.attach(originalValueEntry, 1, 2, 2, 3, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        # Constraints label
        constraintsLabel = gtk.Label("Constraints when parsing / generating")
        constraintsLabel.show()
        mainTable.attach(constraintsLabel, 0, 2, 3, 4, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        # start Value
        minBitsLabel = gtk.Label("Minimum number of hex (0xf=1) : ")
        minBitsLabel.show()
        minBitsEntry = gtk.Entry()
        minBitsEntry.show()
        mainTable.attach(minBitsLabel, 0, 1, 4, 5, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        mainTable.attach(minBitsEntry, 1, 2, 4, 5, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        # end Value
        maxBitsLabel = gtk.Label("Maximum number of hex : ")
        maxBitsLabel.show()
        maxBitsEntry = gtk.Entry()
        maxBitsEntry.show()
        mainTable.attach(maxBitsLabel, 0, 1, 5, 6, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        mainTable.attach(maxBitsEntry, 1, 2, 5, 6, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        dialog.vbox.pack_end(mainTable, True, True, 0)
        dialog.show_all()
        result = dialog.run()

        if result != gtk.RESPONSE_OK:
            dialog.destroy()
            return

        # Creation of the variable (binary)
        # original value :
        originalValue = originalValueEntry.get_text()
        if len(originalValue) == 0:
            originalValue = None

        # constraints
        minSize = int(minBitsEntry.get_text())
        maxSize = int(maxBitsEntry.get_text())

        hexVariable = HexVariable(varID, "hexadecimal", originalValue, minSize, maxSize)
        rootVariable.addChild(hexVariable)

        self.datas[str(hexVariable.getID())] = hexVariable

        self.treestore.append(rootEntry, [str(hexVariable.getID()), hexVariable.getUncontextualizedDescription()])

        # We close the current dialog
        dialog.destroy()

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

        # name of the variable
        variableNameLabel = gtk.Label("Name : ")
        variableNameLabel.show()
        variableNameEntry = gtk.Entry()
        variableNameEntry.show()
        mainTable.attach(variableNameLabel, 0, 1, 2, 3, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        mainTable.attach(variableNameEntry, 1, 2, 2, 3, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        # value of the variable
        variableValueLabel = gtk.Label("Value : ")
        variableValueLabel.show()
        variableValueEntry = gtk.Entry()
        variableValueEntry.show()
        mainTable.attach(variableValueLabel, 0, 1, 3, 4, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        mainTable.attach(variableValueEntry, 1, 2, 3, 4, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        dialog.vbox.pack_end(mainTable, True, True, 0)
        dialog.show_all()
        result = dialog.run()

        if result != gtk.RESPONSE_OK:
            dialog.destroy()
            return

        # We retrieve the value of the variable
        varName = variableNameEntry.get_text()
        varValue = variableValueEntry.get_text()

        if len(varValue) == 0:
            varValue = None

        # Creation of the word id, name, mutable, value):
        wordVariable = WordVariable(variableID, varName, varValue)
        rootVariable.addChild(wordVariable)

        self.datas[str(wordVariable.getID())] = wordVariable

        self.treestore.append(rootEntry, [str(wordVariable.getID()), wordVariable.getUncontextualizedDescription()])

        # We close the current dialog
        dialog.destroy()

    def addDecimalWord(self, event, rootVariable, rootEntry):
        # Display the form for the creation of a word variable
        dialog = gtk.MessageDialog(None, gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_QUESTION, gtk.BUTTONS_OK, None)
        dialog.set_markup('Definition of the Decimal WORD')

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
        decimalwordVariable = DecimalWordVariable(variableID, varValue, None)
        rootVariable.addChild(decimalwordVariable)

        self.datas[str(decimalwordVariable.getID())] = decimalwordVariable

        self.treestore.append(rootEntry, [str(decimalwordVariable.getID()), decimalwordVariable.getUncontextualizedDescription()])

        # We close the current dialog
        dialog.destroy()

    def addIPv4(self, event, rootVariable, rootEntry):
        # Display the form for the creation of an IPv4 variable
        dialog = gtk.MessageDialog(None, gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_QUESTION, gtk.BUTTONS_OK, None)
        dialog.set_markup('Definition of the IPv4 Variable')

        # Create the ID of the new variable
        varID = uuid.uuid4()
        variableID = str(varID)

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

        # Original Value
        originalValueLabel = gtk.Label("Original value : ")
        originalValueLabel.show()
        originalValueEntry = gtk.Entry()
        originalValueEntry.show()
        mainTable.attach(originalValueLabel, 0, 1, 2, 3, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        mainTable.attach(originalValueEntry, 1, 2, 2, 3, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        # Constraints label
        constraintsLabel = gtk.Label("Constraints when parsing / generating")
        constraintsLabel.show()
        mainTable.attach(constraintsLabel, 0, 2, 3, 4, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        # start Value
        startValueLabel = gtk.Label("Start : ")
        startValueLabel.show()
        startValueEntry = gtk.Entry()
        startValueEntry.show()
        mainTable.attach(startValueLabel, 0, 1, 4, 5, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        mainTable.attach(startValueEntry, 1, 2, 4, 5, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        # end Value
        endValueLabel = gtk.Label("End : ")
        endValueLabel.show()
        endValueEntry = gtk.Entry()
        endValueEntry.show()
        mainTable.attach(endValueLabel, 0, 1, 5, 6, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        mainTable.attach(endValueEntry, 1, 2, 5, 6, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        # Format label
        hdrFormatLabel = gtk.Label("Representation")
        hdrFormatLabel.show()
        mainTable.attach(hdrFormatLabel, 0, 2, 7, 8, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        # Format Value
        formatValueLabel = gtk.Label("Format : ")
        formatValueLabel.show()
        formatValueCombo = gtk.combo_box_entry_new_text()
        formatValueCombo.show()
        formatValueComboStore = gtk.ListStore(str)  # format name
        formatValueCombo.set_model(formatValueComboStore)
        # We retrieve all the existing variables in the project
        formatValueCombo.get_model().append([Format.HEX])
        formatValueCombo.get_model().append([Format.ASCII])
        mainTable.attach(formatValueLabel, 0, 1, 8, 9, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        mainTable.attach(formatValueCombo, 1, 2, 8, 9, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        dialog.vbox.pack_end(mainTable, True, True, 0)
        dialog.show_all()
        result = dialog.run()

        if result != gtk.RESPONSE_OK:
            dialog.destroy()
            return

        # Creation of the variable (ipv4)
        # original value :
        originalValue = originalValueEntry.get_text()
        if len(originalValue) == 0:
            originalValue = None

        # constraints
        startValue = startValueEntry.get_text()
        if len(startValue) == 0:
            startValue = None
        endValue = endValueEntry.get_text()
        if len(endValue) == 0:
            endValue = None

        # format
        format = formatValueCombo.get_model().get_value(formatValueCombo.get_active_iter(), 0)
        ipVariable = IPv4Variable(varID, "ipv4", originalValue, startValue, endValue, format)
        rootVariable.addChild(ipVariable)

        self.datas[str(ipVariable.getID())] = ipVariable

        self.treestore.append(rootEntry, [str(ipVariable.getID()), ipVariable.getUncontextualizedDescription()])

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
            self.varCombo.get_model().append([existingVariable.getUncontextualizedDescription(), existingVariable.getID()])

        mainTable.attach(varLabel, 0, 1, 2, 3, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        mainTable.attach(self.varCombo, 1, 2, 2, 3, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        dialog.vbox.pack_end(mainTable, True, True, 0)
        dialog.show_all()
        result = dialog.run()

        if result != gtk.RESPONSE_OK:
            dialog.destroy()
            return

        idReferencedVariable = self.varCombo.get_model().get_value(self.varCombo.get_active_iter(), 1)
        referencedVariable = ReferencedVariable(uuid.uuid4(), "Ref", idReferencedVariable)
        rootVariable.addChild(referencedVariable)

        self.datas[str(referencedVariable.getID())] = referencedVariable
        self.treestore.append(rootEntry, [str(referencedVariable.getID()), referencedVariable.getUncontextualizedDescription()])

        # We close the current dialog
        dialog.destroy()
