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
from setuptools import setup
import sys

package = 'IpcCapturer'
resourcesPath = "../../../../resources/"

sys.path.append(resourcesPath)
from sdist.utils import find_data_files, opj

pluginsStaticResourcesPath = opj(resourcesPath, "static/netzob_plugins/", package)

dependencies = [
    'python-ptrace',
    'Netzob >= 0.4'
]

#+----------------------------------------------------------------------------
#| Definition of Netzob for setup
#+----------------------------------------------------------------------------
setup(
    name="Netzob-IpcCapturer",
    version="1.0.0",
    author="Georges Bossert, Frédéric Guihéry",
    author_email="contact@netzob.org",
    packages=[package],
    install_requires=dependencies,
    data_files=find_data_files(opj("share", "netzob", "plugins", package),
                               pluginsStaticResourcesPath,
                               '*.glade',
                               recursive=True),
    entry_points="""
    [netzob.plugins]
    IpcCapturer=IpcCapturer.IpcCapturerPlugin:IpcCapturerPlugin
    """
)
