#!/usr/bin/python
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
import gtk
import cairo
from math import pi

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
        
        color = gtk.gdk.color_parse('#ffffff')
        self.window.modify_bg(gtk.STATE_NORMAL, color)
        
        self.image = gtk.Image()
        self.image.set_from_file("resources/static/logo.png")
        self.image.show()
        
        main_vbox = gtk.VBox(False, 1) 
        self.window.add(main_vbox)
        main_vbox.pack_start(self.image, True, True)
        hbox = gtk.HBox(False, 0)
        
        workspace = ResourcesConfiguration.ResourcesConfiguration.getWorkspace()
        if workspace != None :
            self.lbl = gtk.Label("Current workspace : " + workspace)
        else :
            self.lbl = gtk.Label("Current workspace : NO WORKSPACE COMPUTED !")
        self.lbl.set_alignment(0, 0.5)
        main_vbox.pack_start(self.lbl, True, True)
        self.window.show_all()
 
