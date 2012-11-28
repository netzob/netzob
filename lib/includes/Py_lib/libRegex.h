// -*- coding: utf-8 -*-

//+---------------------------------------------------------------------------+
//|          01001110 01100101 01110100 01111010 01101111 01100010            |
//|                                                                           |
//|               Netzob : Inferring communication protocols                  |
//+---------------------------------------------------------------------------+
//| Copyright (C) 2011 Georges Bossert and Frédéric Guihéry                   |
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
#ifndef LIBREGEX_H
#define LIBREGEX_H
#include <Python.h>
#include "struct.h"
#include "regex.h"
#include "manipulate.h"
#include "commonPythonLib.h"

/*
*   Initializes the module for python
*
*/
PyMODINIT_FUNC init_libRegex(void);

/*
*   Function which find the alignment corresponding to the regex
*   or raises an exception which need to be caught.
*   args must be a tuple with the regex as first argument and the string to match as second
*/
PyObject* py_match(PyObject* self, PyObject* args);


/* Concatenate the string of fields from the same group
*   string: string representation of the group
*   field: the current field we are analyzing
*   sub: the subfield we add the String representation to the variable field
*/
//void retField(PyObject** string,Fields* field,Subfield* sub,int options);

#endif
