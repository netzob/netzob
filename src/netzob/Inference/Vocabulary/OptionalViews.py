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
import logging
import gtk
import pygtk
import uuid
pygtk.require('2.0')

#+---------------------------------------------------------------------------+
#| Local Imports
#+---------------------------------------------------------------------------+
from netzob.Inference.Vocabulary.Searcher import Searcher
from netzob.Common.Type.Format import Format


#+---------------------------------------------------------------------------+
#| OptionalViews:
#|     Class dedicated to host the notebook of optional views
#+---------------------------------------------------------------------------+
class OptionalViews(object):

    #+-----------------------------------------------------------------------+
    #| Constructor:
    #+-----------------------------------------------------------------------+
    def __init__(self):
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Inference.Vocabulary.OptionalViews.py')
        self.notebook = gtk.Notebook()
        self.views = []

    def registerView(self, view):
        self.views.append(view)

    def getPanel(self):
        self.notebook.set_tab_pos(gtk.POS_TOP)

        for view in self.views:
            viewLabel = gtk.Label(view.getName())
            self.notebook.prepend_page(view.getWidget(), viewLabel)
        self.notebook.show_all()
        return self.notebook

    def update(self):
        isActive = False
        for view in self.views:
            if view.isActive():
                self.notebook.show()
                return
        self.notebook.hide()
