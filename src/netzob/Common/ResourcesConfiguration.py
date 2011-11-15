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
import os.path
import logging
import gtk
import shutil

#+---------------------------------------------- 
#| Related third party imports
#+----------------------------------------------

#+---------------------------------------------- 
#| Local application imports
#+----------------------------------------------
from netzob import NetzobResources

#+---------------------------------------------- 
#| ResourcesConfiguration :
#|    Configure and verify all the resources
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.2
#+---------------------------------------------- 
class ResourcesConfiguration(object):
    
    LOCALFILE = ".netzob"
    
    @staticmethod
    #+---------------------------------------------- 
    #| initializeResources :
    #+---------------------------------------------- 
    def initializeResources():
        # We search for the
        # STATIC resources (images, documentations, ...)
        # USER resources (workspaces, configurations, ...)
        
        # Normaly, on first execution only the static path exists (created
        # during the installation process)
        # While, on everyday execution, both the static and the userpath should exists
        
        staticPath = ResourcesConfiguration.verifyStaticResources()
        if staticPath == None :
            logging.fatal("The static resources were not found !")
            return False
        
        userPath = ResourcesConfiguration.verifyUserResources()
        if userPath == None :
            logging.info("The user resources were not found, we ask to the user its NETZOB home directory")
            userPath = ResourcesConfiguration.askForUserDir()
            if userPath == None :
                return False
            else :
                # the user has specified its home directory so we store it in 
                # a dedicated local file
                localFilePath = os.path.join(os.path.expanduser("~"), ResourcesConfiguration.LOCALFILE)
                # create or update the content
                localFile = open(localFilePath, 'w')
                localFile.write("workspace={0}".format(os.path.abspath(userPath)))
                localFile.close()
                return True
        return True
                    
                
    @staticmethod
    def askForUserDir():
        workspacePath = None
        chooser = gtk.FileChooserDialog(title="Select the workspace", action=gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
                                        buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        
        res = chooser.run()
        if res == gtk.RESPONSE_OK:
            workspacePath = chooser.get_filename()
        chooser.destroy()
        
        if workspacePath != None :
            ResourcesConfiguration.createWorkspace(workspacePath)
        
        return workspacePath
    
    @staticmethod
    def createWorkspace(path):
        # we do nothing if a global config file already exists
        if os.path.isfile(os.path.join(path, "global.conf")) :
            return 
        else :
            # we create a "traces" directory if it doesn't yet exist
            tracesPath = os.path.join(path, "traces")
            if not os.path.isdir(tracesPath) :
                os.mkdir(tracesPath)
            
            # we create a "automaton" directory if it doesn't yet exist
            automatonPath = os.path.join(path, "automaton")
            if not os.path.isdir(automatonPath) :
                os.mkdir(automatonPath)
                
            # we create the "prototypes" directory if it doesn't yet exist
            prototypesPath = os.path.join(path, "prototypes")
            if not os.path.isdir(prototypesPath) :
                os.mkdir(prototypesPath)
                # we upload in it the default repository file
                staticRepositoryPath = os.path.join(os.path.join(ResourcesConfiguration.getStaticResources(), "defaults"), "repository.xml.default")
                shutil.copy(staticRepositoryPath, os.path.join(prototypesPath, "repository.xml"))
                
            
            
        
    
      
    @staticmethod
    def verifyStaticResources():
        staticPath = NetzobResources.STATIC_DIR
        if staticPath == "" :
            return None
        
        logging.debug("Static path declared : " + staticPath)
        if (os.path.isdir(staticPath)) :
            return staticPath
        
        return None
    
    @staticmethod
    def verifyUserResources():
        # the user has specified its home directory so we store it in 
        # a dedicated local file
        localFilePath = os.path.join(os.path.expanduser("~"), ResourcesConfiguration.LOCALFILE)
        if os.path.isfile(localFilePath) :
            localFile = open(localFilePath, 'r')
            userDir = localFile.readline().split("=")[1]  # arf... i know ! A chocolate for finding it :)
            localFile.close()
            return userDir
        return None            
        
    @staticmethod        
    def getStaticResources():
        return NetzobResources.STATIC_DIR
    @staticmethod        
    def getWorkspace():
        if NetzobResources.WORKSPACE_DIR == None :
            return ResourcesConfiguration.verifyUserResources()
        else :
            return NetzobResources.WORKSPACE_DIR

        
