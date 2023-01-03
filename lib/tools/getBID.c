// -*- coding: utf-8 -*-

//+---------------------------------------------------------------------------+
//|          01001110 01100101 01110100 01111010 01101111 01100010            |
//|                                                                           |
//|               Netzob : Inferring communication protocols                  |
//+---------------------------------------------------------------------------+
//| Copyright (C) 2011-2017 Georges Bossert and Frédéric Guihéry              |
//| This program is free software: you can redistribute it and/or modify      |
//| it under the terms of the GNU General Public License as published by      |
//| the Free Software Foundation, either version 3 of the License, or         |
//| (at your option) any later version.                                       |
//|                                                                           |
//| This program is distributed in the hope that it will be useful,           |
//| but WITHOUT ANY WARRANTY; without even the implied warranty of            |
//| MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the              |
//| GNU General Public License for more details.                              |
//|                                                                           |
//| You should have received a copy of the GNU General Public License         |
//| along with this program. If not, see <http://www.gnu.org/licenses/>.      |
//+---------------------------------------------------------------------------+
//| @url      : http://www.netzob.org                                         |
//| @contact  : contact@netzob.org                                            |
//| @sponsors : Amossys, http://www.amossys.fr                                |
//|             Supélec, http://www.rennes.supelec.fr/ren/rd/cidre/           |
//+---------------------------------------------------------------------------+
#include "commonPythonLib.h"

//+---------------------------------------------------------------------------+
//| py_getBID : Returns the unique Binary IDentifier
//+---------------------------------------------------------------------------+
PyObject * py_getBID(__attribute__((unused))PyObject* self, __attribute__((unused))PyObject *noarg) {
	char str_bid[37];
	#ifdef BID
		strncpy(str_bid,STR(BID), sizeof str_bid - 1);
	#else
		printf("The macro which established the BID has not been defined when compiling the lib, default one will be returned.\n");
		strncpy(str_bid, STR(DEFAULT_BID), sizeof str_bid - 1);
	#endif
	str_bid[sizeof str_bid -1]='\0';
	return Py_BuildValue("s", str_bid);
}
