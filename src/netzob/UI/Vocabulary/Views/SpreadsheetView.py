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

from gi.repository import Gtk, Gdk

'''
Created on 17 juil. 2012

@author: heyler
'''

class SpreadSheetView(object):
    '''
    classdocs
    '''


    def __init__(self,vocabularyView,idSymbol):
        """
        Constructor add an external spreadsheet on the builder 
        @type  box: string
        @param box: The hbox/vbox where add the widget
        @type  widget: string
        @param widget: The widget to add 
        @type  position: number
        @param position: The position to add the widget on the hbox/vbox
        @type  expand: gboolean
        @param expand: Set the expand properties
        """
        self.idSymbol = idSymbol
        self.vocabularyView = vocabularyView
        #create a new builder to extract the widget
        builder2 = Gtk.Builder()
        builder2.add_from_file(self.ressourceglade+"/ui/spreadsheet.glade")   
        #set the name of the symbol
        self.label = builder2.get_object("label1")
        if (idSymbol==None):
            self.label.set_text("Empty")
        else:
            self.label.set_text(vocabularyView.getCurrentProject().getVocabulary().getSymbolByID(idSymbol))
        #add the spreadsheet to the main builder
        self.spreadsheet = builder2.get_object("spreadsheet")
        box = vocabularyView.builder.get_object("box5")
        box.pack_start(self.spreadsheet, True, True, 0)
        box.reorder_child(self.spreadsheet, 0) 
        #add the message for the treeview
        self.treeview = builder2.get_object("treemessage")
        
        #add the close button
        self.closebutton = builder2.get_object("button4")
        self.closebutton.connect("clicked",self.button_closeview_cb,self.spreadsheet)
        #focus
        self.focusbutton = builder2.get_object("button1")
        self.focusbutton.connect("clicked",self.button_focusview_cb,builder2)
        
   
    def setName(self,newName):
        self.label.set_text(newName)

    def refresh(self):
        pass

    def setWidget(self):
        pass
    
    def destroy(self):
        self.widget.destroy()