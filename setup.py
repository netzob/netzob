#!/usr/bin/env python
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
#| Definition of NETZOB for setup
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
        "netzob.Export",
        "netzob.Export.TreeViews",
        "netzob.Fuzzing",
        "netzob.Fuzzing.TreeViews",
        "netzob.Import",
        "netzob.Import.GOTPoisoning",
        "netzob.Import.TreeViews",
        "netzob.Modelization",
        "netzob.Modelization.TreeViews",
        "netzob.Simulator",
	"netzob.ExternalLibs"
        ],
    package_dir = {"netzob": "src/netzob" },
    ext_modules=[moduleLibNeedleman],
    data_files = [
        ('share/netzob', ['resources/static/logo.png']),
        ('share/icons/hicolor/22x22/apps/', ["resources/static/icons/22x22/netzob.png"]),
        ('share/icons/hicolor/48x48/apps/', ["resources/static/icons/48x48/netzob.png"]),
        ('share/icons/hicolor/64x64/apps/', ["resources/static/icons/64x64/netzob.png"])
        ],
    scripts = ["netzob"],
    version="0.3.0",
    description="Network protocol modelization by reverse engineering",
    author="Georges Bossert, Frederic Guihery",
    author_email="{gbt,fgy}@amossys.fr",
    url="http://code.google.com/p/netzob/",
    download_url="https://netzob.googlecode.com/svn/trunk/",
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
NETwork protocol modeliZatiOn By reverse engineering
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
