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
from glob import glob
import os
from fnmatch import fnmatch

def opj(*args):
    path = os.path.join(*args)
    return os.path.normpath(path)

def find_data_files(dstdir, srcdir, *wildcards, **kw):
    """Build a mapping of merge path and local files to put in
    data_files argument of setup() call"""

    # get a list of all files under the srcdir matching wildcards,
    # returned in a format to be used for install_data
    def walk_helper(arg, dirname, files):
        if '.git' in dirname:
            return
        names = []
        (lst,) = arg
        for wc in wildcards:
            wc_name = opj(dirname, wc)
            for f in files:
                filename = opj(dirname, f)
                if fnmatch(filename, wc_name) and not os.path.isdir(filename):
                    names.append(filename)
        lst.append((dirname.replace(srcdir, dstdir), names))

    file_list = []
    if kw.get('recursive', True):
        os.path.walk(srcdir, walk_helper, (file_list,))
    else:
        walk_helper((file_list,), srcdir,
                    [os.path.basename(f) for f in glob(opj(srcdir, '*'))])
    return file_list
