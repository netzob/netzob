#!/usr/bin/env python
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
import os
import re
import sys
import subprocess
from git import *
    
def getFiles():
    currentPath = os.getcwd()
    # First we initialize the repository object
    repository = Repo(currentPath)    

    listFile = []
    repositoryIndex = repository.index
    for d in repositoryIndex.diff('HEAD') :
        # Added path
        if d.deleted_file:
            path = d.a_blob.path
            if not path in listFile :
                listFile.append(path)
        elif not d.new_file :
            path = d.a_blob.path
            if not path in listFile :
                listFile.append(path)
    return listFile


def checkPEP8(file) :
    localResult = []
    p = subprocess.Popen(['pep8', '--ignore=E501', file], stdout=subprocess.PIPE)
    out, err = p.communicate()
    for line in out.splitlines():
        localResult.append(line)
    return localResult

def searchForPattern(file, pattern, errorName) :
    localResult = []
    fileObject = open(file)
    lineNumber = 0
    for line in fileObject :
        lineNumber += 1
        if re.search(pattern, line):
            localResult.append(str(errorName) + " found at line " + str(lineNumber))
    return localResult

def checkFile(file):
    results = dict()    
    
    # Verify no '<<<' and or conflicts info are commited
    results['Conflicts'] = searchForPattern(file, '<<<<<<', 'hints of untreated conflicts')

    # Check against PEP8 rules for python files
    if os.path.splitext(file)[-1] == ".py" :
        results['PEP8'] = checkPEP8(file)
    
    return results
    
def verifyResults(results) :
    result = 0
    for file in results.keys() :
        resultFile = results[file]
        if len(resultFile) > 0 :
            print "[I] File %s :" % (file)
            for ruleName in resultFile.keys() :
                ruleErrors = resultFile[ruleName]
                for ruleError in ruleErrors :
                    print "[I]\t %s : %s" % (ruleName, ruleError)

            result = 1
    return result


def analyze():
   # Retrieve all the files to analyze
   print "[I] Retrieve all the files to analyze."
   files = getFiles()
   
   print "[I] %d files will be analyzed." % (len(files))
   globalResults = dict()
   for file in files :
       globalResults[file] = checkFile(file)

   # Compute the final result (0=sucess, 1=cannot commit)
   result = verifyResults(globalResults)
   if result == 0 :
       print "[I] No error found, commit allowed."
   else :
       print "[E] Errors founds, commit not allowed."
   sys.exit(result)


if __name__ == '__main__' :
    # Execute the analysis
    analyze()


