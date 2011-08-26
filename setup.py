#!/usr/bin/python
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
                               libraries=['python2.6'],
                               extra_compile_args=["-fopenmp"],
                               extra_link_args=["-fopenmp"],
                               include_dirs=['/usr/include/python2.6'],
                               sources=['lib/libNeedleman/NeedlemanWunsch.c'])

#+---------------------------------------------------------------------------- 
#| Definition of NETZOB for setup
#+----------------------------------------------------------------------------
setup(
    name="Netzob",
    packages=[
                "src",
                    "src.netzob",
                        "src.netzob.Capturing",
                            "src.netzob.Capturing.GotPoisoning",
                            "src.netzob.Capturing.TreeViews",
                        "src.netzob.Common",
                            "src.netzob.Common.Models",
                                "src.netzob.Common.Models.Factories",
                        "src.netzob.Dumping",
                        "src.netzob.Fuzzing",
                        "src.netzob.Sequencing",
                            "src.netzob.Sequencing.TreeViews",
                ],
    ext_modules=[moduleLibNeedleman],
    version="1.0.0",
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
