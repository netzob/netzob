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
import logging.config
import os

#+----------------------------------------------
#| Related third party imports
#+----------------------------------------------

#+----------------------------------------------
#| Local application imports
#+----------------------------------------------


#+----------------------------------------------
#| LoggingConfiguration:
#|    Configure the logging layer of Netzob
#+----------------------------------------------
class LoggingConfiguration(object):

    @staticmethod
    #+----------------------------------------------
    #| initializeLogging:
    #+----------------------------------------------
    def initializeLogging(workspace):
        # First we extract the normal logging config file
        loggingFilePath = os.path.join(workspace.getPath(), workspace.getPathOfLogging())
        if (loggingFilePath != "" and os.path.isfile(loggingFilePath)):
            logging.debug("Logging config file : " + loggingFilePath)
            logging.config.fileConfig(loggingFilePath)
        else:
            logging.info("No logging config file found, create a default one.")
            # Make a global logging object.
            logger = logging.getLogger("")
            logger.setLevel(logging.INFO)
            h = logging.StreamHandler()
            f = logging.Formatter("[%(threadName)s]%(asctime)s - %(module)s - %(levelname)s - %(message)s")
            h.setFormatter(f)
            logger.addHandler(h)
