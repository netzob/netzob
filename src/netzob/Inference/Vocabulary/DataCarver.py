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
import re
from netzob.Common.Type.TypeConvertor import TypeConvertor
from netzob.Common.Type.Format import Format
from netzob.Inference.Vocabulary.SearchResult import SearchResult
from netzob.Inference.Vocabulary.SearchTask import SearchTask
#+----------------------------------------------
#| Local Imports
#+----------------------------------------------


#+----------------------------------------------
#| DataCarver:
#|     Provides multiple algorithms to search for types of data
#+----------------------------------------------
class DataCarver(object):

    #+----------------------------------------------
    #| Constructor:
    #| @param project : the project where the search will be executed
    #+----------------------------------------------
    def __init__(self, project):
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Inference.Vocabulary.DataCarver.py')
        self.project = project

    #+----------------------------------------------
    #| execute:
    #| @param symbol : if not None, the operation will be limited to provided symbol
    #+----------------------------------------------
    def execute(self, symbol):
        results = []
        toBeAnalyzed = []
        if symbol != None:
            toBeAnalyzed.append(symbol)
        else:
            toBeAnalyzed.extend(self.project.getVocabulary().getSymbols())

        for symbol in toBeAnalyzed:
            searchTask = SearchTask("URL Data Carver", "((http:\/\/|https:\/\/)?(www\.)?(([a-z0-9\-]){2,}\.){1,4}([a-z]){2,6}(\/([a-z\-_\/\.0-9#:?+%=&;,])*)?)", "URL")

            ## TODO: put this things in a dedicated class
            infoCarvers = {
                           'url': re.compile("((http:\/\/|https:\/\/)?(www\.)?(([a-z0-9\-]){2,}\.){1,4}([a-z]){2,6}(\/([a-z\-_\/\.0-9#:?+%=&;,])*)?)"),
                           'email': re.compile("[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,4}"),
                           'ip': re.compile("(((?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?))")
            }
            foundValues = []

            tasks = []
            # Execute the search operation in String mode
            for (carver, regex) in infoCarvers.items():
                currentTask = SearchTask(carver, None, carver)
                taskResults = []
                for message in symbol.getMessages():
                    strData = TypeConvertor.netzobRawToString(message.getReducedStringData())
                    for match in regex.finditer(strData):
                        if match == None:
                            taskResult = SearchResult(message, "Data Carving : {0}".format(carver))
                            taskResult.addSegment(0, len(message.getReducedStringData()))
                            taskResults.append(taskResult)
                        else:
                            taskResult = SearchResult(message, "Data Carving : {0}".format(carver))
                            taskResult.addSegment(match.start(0) * 2, match.end(0) * 2)
                            taskResults.append(taskResult)
                if len(taskResults) > 0:
                    currentTask.registerResults(taskResults, "Data Carving : {0}".format(carver))
                    tasks.append(currentTask)
            results.append(tasks)

        return results
