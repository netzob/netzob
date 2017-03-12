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

#ifndef libNeedleman_H
#define libNeedleman_H 

//+---------------------------------------------------------------------------+
//| Imports
//+---------------------------------------------------------------------------+
#include "commonPythonLib.h"
#include "commonLib.h"
#include "Needleman.h"

//+---------------------------------------------------------------------------+
//| py_alignMessages : Python wrapper for alignMessages
//+---------------------------------------------------------------------------+
PyObject* py_alignMessages(PyObject* self, PyObject* args);

//+---------------------------------------------------------------------------+
//| py_alignTwoMessages : Python wrapper for alignTwoMessages
//+---------------------------------------------------------------------------+
PyObject* py_alignTwoMessages(PyObject* self, PyObject* args);

//+---------------------------------------------------------------------------+
//| initLibNeedleman : Python will use this function to init the module
//+---------------------------------------------------------------------------+
PyMODINIT_FUNC init_libNeedleman(void);


#endif
