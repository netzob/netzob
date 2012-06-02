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
    for d in repositoryIndex.diff('HEAD'):
        # Added path
        if d.deleted_file:
            path = d.a_blob.path
            if not path in listFile:
                listFile.append(path)
        elif not d.new_file:
            path = d.a_blob.path
            if not path in listFile:
                listFile.append(path)
    return listFile


def checkPEP8(file):
    localResult = []
    p = subprocess.Popen(['pep8', '--repeat', '--ignore=E501', file], stdout=subprocess.PIPE)
    out, err = p.communicate()
    for line in out.splitlines():
        localResult.append(line)
    return localResult


def searchForPattern(file, pattern, errorName):
    localResult = []
    fileObject = open(file)
    lineNumber = 0
    for line in fileObject:
        lineNumber += 1
        if re.search(pattern, line) and not re.search('Thisisnotaconflict', line):
            localResult.append(str(errorName) + " found at line " + str(lineNumber))
    fileObject.close()
    return localResult


# Verifies only LF ('\n') ended files are committed (no CRLF '\r\n').
def checkForCRLF(file):
    localResult = []
    with open(file, 'rb') as f:
        lineNumber = 0
        for line in f:
            lineNumber += 1
            if line.endswith(b"\r\n"):
                localResult.append("A CRLF ending patterns found at line " + str(lineNumber))
    return localResult


def checkHeader(file):
    header = """#+---------------------------------------------------------------------------+
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
#+---------------------------------------------------------------------------+"""
    header2 = header.replace("#", "//")  # For C files
    header3 = header.replace("#", "")     # For other
    with open(file, 'rb') as f:
        data = f.read()
    if not header in data and not header2 in data and not header3 in data:
        return ["The header has not been found in file"]
    return []


def checkFile(file):
    results = dict()

    if file.endswith("__init__.py"):
        return results

    # Verify no '<<<' and or conflicts info are commited
    results['Conflicts'] = searchForPattern(file, '<<<<<<', 'hints of untreated conflicts')  # Thisisnotaconflict

    if file.endswith(".txt"):
        return results

    # Verify no CRLF is used in source
    results['CRLF'] = checkForCRLF(file)

    # Verify the header is valid
    results['Header'] = checkHeader(file)

    # Check against PEP8 rules for python files
    if os.path.splitext(file)[-1] == ".py":
        results['PEP8'] = checkPEP8(file)

    return results


def verifyResults(results):
    result = 0
    for file in results.keys():
        resultFile = results[file]
        if len(resultFile) > 0:
            print "[I] File %s:" % (file)
            ruleNames = resultFile.keys()
            localResult = 0
            for ruleName in ruleNames:
                ruleErrors = resultFile[ruleName]
                if ruleErrors != None and len(ruleErrors) > 0:
                    for ruleError in ruleErrors:
                        print "[E]\t %s : %s" % (ruleName, ruleError)
                    result = 1
                    localResult = 1
            if localResult == 0:
                print "[I]\t no error found."
    return result


def analyze(filesToAnalyze):

    if filesToAnalyze == None:
        # Retrieve all the files to analyze
        print "[I] Retrieve all the files to analyze from the staged area."
        files = getFiles()
    else:
        print "[I] Retrieve all the file to analyze from the command line arguments."
        files = []
        for fileToAnalyze in filesToAnalyze:
            if os.path.isfile(fileToAnalyze):
                try:
                    test = open(fileToAnalyze)
                    test.close()
                    files.append(fileToAnalyze)
                except:
                    print "[E] File %s exists but is not readable." % fileToAnalyze

    print "[I] %d files will be analyzed." % (len(files))
    globalResults = dict()
    for file in files:
        globalResults[file] = checkFile(file)

    # Compute the final result (0=sucess, 1=cannot commit)
    result = verifyResults(globalResults)
    if result == 0:
        print "[I] No error found, commit allowed."
    else:
        print "[E] Errors founds, commit not allowed."
    sys.exit(result)


if __name__ == '__main__':

    filesToAnalyze = None
    if (len(sys.argv) > 1):
        filesToAnalyze = sys.argv[1:]

    # Execute the analysis
    analyze(filesToAnalyze)
