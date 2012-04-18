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

#+----------------------------------------------------------------------------
#| Global Imports
#+----------------------------------------------------------------------------
import sys
import os
sys.path.insert(0, 'src/')
from setuptools import setup, Extension, find_packages
from netzob import release
from resources.sdist.manpage_command import manpage_command


#+----------------------------------------------------------------------------
#| Definition of the extensions
#+----------------------------------------------------------------------------
moduleLibNeedleman = Extension('_libNeedleman',
                               sources=['lib/libNeedleman/libNeedleman.c'])

CMD_CLASS = {
             'build_manpage': manpage_command
             }



#+----------------------------------------------------------------------------
#| Definition of Netzob for setup
#+----------------------------------------------------------------------------
setup(
    name=release.name,
    packages=find_packages(where='src'),
    package_dir={"netzob": "src" + os.sep + "netzob"},
    ext_modules=[moduleLibNeedleman],
    data_files=[
        ('share/netzob', ['resources/static/logo.png']),
        ('share/applications/', ['resources/static/netzob.desktop']),
        ('share/icons/hicolor/22x22/apps/', ["resources/static/icons/22x22/netzob.png"]),
        ('share/icons/hicolor/48x48/apps/', ["resources/static/icons/48x48/netzob.png"]),
        ('share/icons/hicolor/64x64/apps/', ["resources/static/icons/64x64/netzob.png"]),
        ('share/netzob/defaults', ["resources/static/defaults/repository.xml.default"]),
        ('share/netzob/defaults', ["resources/static/defaults/logging.conf.default"]),
        ('share/netzob/xsds/0.1/', ["resources/static/xsds/0.1/Workspace.xsd",
                                    "resources/static/xsds/0.1/Project.xsd",
                                    "resources/static/xsds/0.1/common.xsd"]),
        ],
    scripts=["netzob"],
    version=release.version,
    license=release.licenseName,
    description=release.description,
    platforms=release.platforms,
    author=release.author,
    author_email=release.author_email,
    url=release.url,
    download_url=release.download_url,
    keywords=release.keywords,
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Development Status :: 4 - Beta",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Natural Language :: English",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
        "Topic :: Security",
        "Topic :: System :: Networking",
        ],
    long_description=release.long_description,
    cmdclass=CMD_CLASS
    )
