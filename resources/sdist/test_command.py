# -*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|          01001110 01100101 01110100 01111010 01101111 01100010            |
#|                                                                           |
#|               Netzob : Inferring communication protocols                  |
#+---------------------------------------------------------------------------+
#| Copyright (C) 2011-2016 Georges Bossert and Frédéric Guihéry              |
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

#+----------------------------------------------------------------------------
#| Global Imports
#+----------------------------------------------------------------------------
from distutils.core import Command
import os
import sys
import unittest


class test_command(Command):
    description = "Test Netzob"

    user_options = [('reportfile=', None, 'name of the generated XML report file (not required)') ]

    def initialize_options(self):
        self.reportfile = None
        self._dir = os.getcwd()

    def finalize_options(self):
        pass

    def run(self):
        '''
        Finds all the tests modules in test/, and runs them.
        '''
        sys.path.insert(0, 'src/')

        #insert in the path the directory where _libNeedleman.pyd is
        if os.name == 'nt':
            sys.path.insert(0, 'lib/libNeedleman/')

        try:
            # Verify that libNeedleman is in the path
            from netzob import _libNeedleman
        except:
            # Else, assume the path is gotten from the 'python setup.py build' command
            arch = os.uname()[-1]
            python_version = sys.version[:3]
            build_lib_path = "build/lib.linux-" + arch + "-" + python_version
            sys.path.append(build_lib_path)

        sys.path.insert(0, 'test/src/')

        from common.xmlrunner import XMLTestRunner
        from test_netzob import suite_global
        #import netzob.NetzobGui as NetzobGui

        # We retrieve the current test suite
        currentTestSuite = suite_global.getSuite()

        testResults = None
    
        if self.reportfile is None or len(self.reportfile) == 0:
            runner = unittest.TextTestRunner(verbosity = 1)
            testResults = runner.run(currentTestSuite)
        else:
            # We execute the test suite
            with open(self.reportfile, 'w') as fd:
                fd.write('<?xml version="1.0" encoding="utf-8"?>\n')
                reporter = XMLTestRunner(fd)
                testResults = reporter.run(currentTestSuite)

            self.cleanFile(self.reportfile)

        if testResults is None:
            sys.exit(False)
        else:
            sys.exit(bool(testResults.failures))            

    def cleanFile(self, filePath):
        """Clean the file to handle non-UTF8 bytes.
        """

        with open(filePath, 'r') as aFile:
            data = aFile.read()

        cleanData = ""
        for c in data:
            if (0x1f < ord(c) < 0x80) or (ord(c) == 0x9) or (ord(c) == 0xa) or (ord(c) == 0xd):
                cleanData += c
            else:
                cleanData += repr(c)

        with open(filePath, 'w') as aFile:
            aFile.write(cleanData)
