#!/usr/bin/env python
# -*- coding: utf-8 -*-

# +---------------------------------------------------------------------------+
# |          01001110 01100101 01110100 01111010 01101111 01100010            |
# |                                                                           |
# |               Netzob : Inferring communication protocols                  |
# +---------------------------------------------------------------------------+
# | Copyright (C) 2011-2014 Georges Bossert and Frédéric Guihéry              |
# | This program is free software: you can redistribute it and/or modify      |
# | it under the terms of the GNU General Public License as published by      |
# | the Free Software Foundation, either version 3 of the License, or         |
# | (at your option) any later version.                                       |
# |                                                                           |
# | This program is distributed in the hope that it will be useful,           |
# | but WITHOUT ANY WARRANTY; without even the implied warranty of            |
# | MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the              |
# | GNU General Public License for more details.                              |
# |                                                                           |
# | You should have received a copy of the GNU General Public License         |
# | along with this program. If not, see <http://www.gnu.org/licenses/>.      |
# +---------------------------------------------------------------------------+
# | @url      : http://www.netzob.org                                         |
# | @contact  : contact@netzob.org                                            |
# | @sponsors : Amossys, http://www.amossys.fr                                |
# |             Supélec, http://www.rennes.supelec.fr/ren/rd/cidre/           |
# +---------------------------------------------------------------------------+

# +---------------------------------------------------------------------------+
# | File contributors :                                                       |
# |       - Sumit Acharya <sumit.acharya@uni-ulm.de>                          |
# |       - Stephan Kleber <stephan.kleber@uni-ulm.de>                        |
# +---------------------------------------------------------------------------+

# +---------------------------------------------------------------------------+
# | Purpose :                                                                 |
# | Serialize and de-serialize python objects so that a completed or manually |
# | augmeneted analysis can be saved/stored in the filesystem and load them   |
# | back into memory.                                                         |
# +---------------------------------------------------------------------------+

import os
import uuid
import logging
import bitarray

import pickle as cPickle

from netzob.Common.Utils.Decorators import typeCheck

class Cpicklizer(object):
	'''Serialize and de-Serialize the python objects.'''

	@staticmethod
	@typeCheck(object, str)
	def dumpToFile(obj, filename):
	    '''Dump objects to a file'''

	    if filename is not None:
	        f = open(filename, 'wb')
	        cPickle.dump(obj,f,cPickle.HIGHEST_PROTOCOL)
	    else:
	        logging.warn("This file is not reachable: {0}".format(str(aFile)))
	        return None

	@staticmethod
	@typeCheck(object, str)
	def restoreFromFile(filename):
	    '''Restore Objects from file'''
	    if filename is not None and os.path.exists(filename):
        	return cPickle.load(open(filename,'rb'))
	    else:
	        return None
