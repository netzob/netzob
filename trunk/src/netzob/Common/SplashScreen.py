# -*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|         01001110 01100101 01110100 01111010 01101111 01100010             | 
#+---------------------------------------------------------------------------+
#| NETwork protocol modeliZatiOn By reverse engineering                      |
#| ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~+
#| @license      : GNU GPL v3                                                |
#| @copyright    : Georges Bossert and Frederic Guihery                      |
#| @url          : http://code.google.com/p/netzob/                          |
#| ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~+
#| @author       : {gbt,fgy}@amossys.fr                                      |
#| @organization : Amossys, http://www.amossys.fr                            |
#+---------------------------------------------------------------------------+

#+---------------------------------------------- 
#| Standard library imports
#+----------------------------------------------
import pygtk
pygtk.require('2.0')
import gtk
import os
import logging
#+---------------------------------------------- 
#| Related third party imports
#+----------------------------------------------

#+---------------------------------------------- 
#| Local application imports
#+----------------------------------------------
import ResourcesConfiguration
#+---------------------------------------------- 
#| SplashScreen :
#|    Manage a splashscreen for NETZOB startup
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.2
#+---------------------------------------------- 
class SplashScreen(object):
    def __init__(self):        
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_title('NETZOB')
        self.window.set_position(gtk.WIN_POS_CENTER)
        self.window.set_decorated(False)
        self.window.set_default_size(268, 501)
        self.window.set_events(gtk.gdk.ALL_EVENTS_MASK)
        
       
        
        # Retrieve static resources
        staticPath = ResourcesConfiguration.ResourcesConfiguration.getStaticResources()
        logoPath = os.path.abspath(os.path.join(staticPath, "logo.png"))


        hbox = gtk.HBox()
        hbox.show()
        self.window.add(hbox)

        self.image = gtk.Image()
        self.image.set_from_file(logoPath)
        self.image.show()
        
        main_vbox = gtk.VBox(False, 1) 
        
#        main_vbox.pack_start(self.image, True, True)
        
        
        
        workspace = ResourcesConfiguration.ResourcesConfiguration.getWorkspace()
        if workspace != None :
            self.lbl = gtk.Label("Current workspace : " + workspace)
        else :
            self.lbl = gtk.Label("Current workspace : NO WORKSPACE COMPUTED !")
        self.lbl.set_alignment(0, 0.5)
        
        
        main_vbox.pack_start(self.image, True, True, 2)
        
        self.window.add(main_vbox)
        self.window.show_all()
 
