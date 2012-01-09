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
from distutils.core import setup, Extension

#+----------------------------------------------------------------------------
#| Definition of the extensions
#+----------------------------------------------------------------------------
moduleLibNeedleman = Extension('libNeedleman',
                               extra_compile_args=["-fopenmp"],
                               extra_link_args=["-fopenmp"],
                               sources=['lib/libNeedleman/NeedlemanWunsch.c'])

#+---------------------------------------------------------------------------- 
#| Definition of Netzob for setup
#+----------------------------------------------------------------------------
setup(
    name="Netzob",
    packages=[
        "netzob",
        "netzob.Common",
        "netzob.Common.MMSTD",
        "netzob.Common.MMSTD.Actors",
        "netzob.Common.MMSTD.Actors.Network",
        "netzob.Common.MMSTD.Dictionary",
        "netzob.Common.MMSTD.Dictionary.Values",
        "netzob.Common.MMSTD.Dictionary.Variables",
        "netzob.Common.MMSTD.States",
        "netzob.Common.MMSTD.States.impl",
        "netzob.Common.MMSTD.Symbols",
        "netzob.Common.MMSTD.Symbols.impl",
        "netzob.Common.MMSTD.Tools",
        "netzob.Common.MMSTD.Tools.Drawing",
        "netzob.Common.MMSTD.Tools.Parsers",
        "netzob.Common.MMSTD.Tools.Parsers.DictionaryParser",
        "netzob.Common.MMSTD.Tools.Parsers.MMSTDParser",
        "netzob.Common.MMSTD.Transitions",
        "netzob.Common.MMSTD.Transitions.impl",
        "netzob.Common.Models",
        "netzob.Common.Models.Factories",
        "netzob.Common.Type",
        "netzob.Export",
        "netzob.Export.TreeViews",
        "netzob.ExternalLibs",
        "netzob.Fuzzing",
        "netzob.Fuzzing.TreeViews",
        "netzob.Import",
        "netzob.Import.GOTPoisoning",
        "netzob.Import.TreeViews",
        "netzob.Inference",
        "netzob.Inference.Grammar",
        "netzob.Inference.Grammar.EquivalenceOracles",
        "netzob.Inference.Grammar.Oracles",
        "netzob.Inference.Grammar.Queries",
        "netzob.Inference.Vocabulary",
        "netzob.Inference.Vocabulary.TreeViews",
        "netzob.Simulator"
        ],
    package_dir={"netzob": "src/netzob" },
    ext_modules=[moduleLibNeedleman],
    data_files=[
        ('share/netzob', ['resources/static/logo.png']),
        ('share/icons/hicolor/22x22/apps/', ["resources/static/icons/22x22/netzob.png"]),
        ('share/icons/hicolor/48x48/apps/', ["resources/static/icons/48x48/netzob.png"]),
        ('share/icons/hicolor/64x64/apps/', ["resources/static/icons/64x64/netzob.png"]),
        ('share/netzob/defaults', ["resources/static/defaults/repository.xml.default"])
        ],
    scripts=["netzob"],
    version="0.3.0",
    description="Inferring communication protocols",
    author="Georges Bossert, Frederic Guihery",
    author_email="contact@netzob.org",
    url="http://www.netzob.org",
    download_url="https://dev.netzob.org",
    keywords=["Protocol", "Inference", "Networking", "Reverse Engineering", "Driver", "Security"],
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
    long_description="""\
Inferring communication protocols
-------------------------------------

Netzob simplifies the work for security auditors by providing a complete framework 
for the reverse engineering of communication protocols. 

It handles different types of protocols : text protocols (like HTTP and IRC), fixed fields protocols (like IP and TCP) 
and variable fields protocols (like ASN.1 based formats). 
Netzob is therefore suitable for reversing network protocols, structured files and system and process 
flows (IPC and communication with drivers). Netzob is provided with modules dedicated to capture data in 
multiple contexts (network, file, process and kernel data acquisition). 
"""
    )
