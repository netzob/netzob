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

//Compilation Windows
//cl -Fe_libInterface.pyd -Ox -Ot -openmp -LD /I"C:\Python26\include" /I"C:\Program Files (x86)\Microsoft Visual Studio 9.0\VC\include" libInterface.c "C:\Python26\libs\python26.lib" "C:\Program Files (x86)\Microsoft Visual Studio 9.0\VC\lib\vcomp.lib"
#ifndef FACTORY_H
#define FACTORY_H
#include "commonPythonLib.h"
#include "commonLib.h"
#include <stdio.h>
#include <stdarg.h>

int parseArgs(PyObject* factobj, ...);

/**
   parseLibscoreComputation:

   This function parses the arguments wrapper following a specific format.
   The definition of this format can be found in the Python function:
   netzob.Common.C_Extensions.WrapperArgsFactory:WrapperArgsFactory.computeSimilarityMatrix()
   Once parsed, the wrapper reveal arguments which will be stored in the args parameter.
   Format:
   - List<Message> with Message: (alignment, mask, length, uid)
*/
void parseLibscoreComputation(PyObject* factobj, va_list args);

void parseLibNeedleman(PyObject* factobj, va_list args);

/**
   parseMessage:

   This function parses a python Netzob message to its C representation
   @param item : the PyObject which host the python representation of the message
   @param message : the message which should host the python extracted message's information
   @return void
*/
void parseMessage(PyObject * item, t_message * message);

#endif
