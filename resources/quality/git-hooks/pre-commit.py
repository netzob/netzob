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
import subprocess
import sys

def stash():
    # -u : include untracked files in the stashing process
    # --keep-index : all changes already added to the index are left intact.
    subprocess.call(['git', 'stash', 'save', '-u', '--keep-index', 'pre-commit stash'], stdout=subprocess.PIPE)

def unstash():
    # Unstash changes to the working tree that we had stashed
    subprocess.call(['git', 'reset', '--hard'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    subprocess.call(['git', 'stash', 'pop', '-q'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
def getFiles():
    files = []
    regexToGetFile = re.compile('^(?:M|A)(\s+)(?P<name>.*)')
    p = subprocess.Popen(['git', 'status', '--porcelain'], stdout=subprocess.PIPE)
    out, err = p.communicate()
    for line in out.splitlines():
        match = regexToGetFile.match(line)
        if match:
            files.append(match.group('name'))
    return files

def checkPEP8(file) :
    localResult = []
    p = subprocess.Popen(['pep8', '--ignore=E501', file], stdout=subprocess.PIPE)
    out, err = p.communicate()
    for line in out.splitlines():
        localResult.append(line)
    return localResult

def checkFile(file):
    results = dict()    
        
    # First we check against PEP8 rules
    results['PEP8'] = checkPEP8(file)

    # ADD rules here


    
    return results
    
def verifyResults(results) :
    result = 0
    for file in results.keys() :
        resultFile = results[file]
        if len(resultFile) > 0 :
            print file
            for ruleName in resultFile.keys() :
                ruleErrors = resultFile[ruleName]
                for ruleError in ruleErrors :
                    print "\t %s : %s" % (ruleName, ruleError)

            result = 1
    return result


def analyze():
    # First we stash the current modifications
    print "[I] Stashing the current modifications."
    stash()
    
    # Retrieve all the files to analyze
    print "[I] Retrieve all the files to analyze."
    files = getFiles()
    
    print "[I] %d files will be analyzed." % (len(files))
    globalResults = dict()
    for file in files :
        globalResults[file] = checkFile(file)
    unstash()

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


