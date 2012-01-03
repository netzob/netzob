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
#| Standard library imports
#+----------------------------------------------
import pygtk
pygtk.require('2.0')
import gtk
import os

#+---------------------------------------------- 
#| Related third party imports
#+----------------------------------------------

#+---------------------------------------------- 
#| Local application imports
#+----------------------------------------------
from netzob.Common.ResourcesConfiguration import ResourcesConfiguration

#+---------------------------------------------- 
#| SplashScreen :
#|    Manage a splashscreen for Netzob startup
#+---------------------------------------------- 
class SplashScreen(object):
    def __init__(self):        
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_title('Netzob')
        self.window.set_position(gtk.WIN_POS_CENTER)
        self.window.set_decorated(False)
        self.window.set_default_size(268, 501)
        self.window.set_events(gtk.gdk.ALL_EVENTS_MASK)
        
       
        
        # Retrieve static resources
        staticPath = ResourcesConfiguration.getStaticResources()
        logoPath = os.path.abspath(os.path.join(staticPath, "logo.png"))


        hbox = gtk.HBox()
        hbox.show()
        self.window.add(hbox)

        self.image = gtk.Image()
        self.image.set_from_file(logoPath)
        self.image.show()
        
        main_vbox = gtk.VBox(False, 1) 
        
#        main_vbox.pack_start(self.image, True, True)
        
        
        
        workspace = ResourcesConfiguration.getWorkspace()
        if workspace != None :
            self.lbl = gtk.Label("Current workspace : " + workspace)
        else :
            self.lbl = gtk.Label("Current workspace : NO WORKSPACE COMPUTED !")
        self.lbl.set_alignment(0, 0.5)
        
        
        main_vbox.pack_start(self.image, True, True, 2)
        
        self.window.add(main_vbox)
        self.window.show_all()
 
