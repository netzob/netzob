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
import logging.config

#+---------------------------------------------- 
#| Related third party imports
#+----------------------------------------------

#+---------------------------------------------- 
#| Local application imports
#+----------------------------------------------
from netzob.Common.ConfigurationParser import ConfigurationParser


#+---------------------------------------------- 
#| LoggingConfiguration :
#|    Configure the logging layer of Netzob
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.2
#+---------------------------------------------- 
class LoggingConfiguration(object):
    
    @staticmethod
    #+---------------------------------------------- 
    #| initializeLogging :
    #+---------------------------------------------- 
    def initializeLogging():
        # First we extract the normal logging config file
        loggingFilePath = ConfigurationParser().get("logging", "path")
        if (loggingFilePath != "") :
            logging.debug("Logging config file : " + loggingFilePath)
            logging.config.fileConfig(loggingFilePath)
        else :
            logging.info("No logging config file found, create a default one.")
            # Make a global logging object.
            logger = logging.getLogger("")
            logger.setLevel(logging.INFO)
            h = logging.StreamHandler()
            f = logging.Formatter("[%(threadName)s]%(asctime)s - %(module)s - %(levelname)s - %(message)s")
            h.setFormatter(f)
            logger.addHandler(h)

        
