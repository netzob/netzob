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
#include "libRegex.h"



PyObject *exception = NULL;

static PyMethodDef regex_methods[] = {
		{"getBID", py_getBID, METH_NOARGS},
		{"match", py_match, METH_VARARGS},
		{NULL, NULL}
};
//+---------------------------------------------------------------------------+
//| initlibRegex : Python will use this function to init the module
//+---------------------------------------------------------------------------+
PyMODINIT_FUNC init_libRegex(void) {
    PyObject *d = PyDict_New();
    (void) Py_InitModule("_libRegex", regex_methods);
    #if PYTHON_API_VERSION >= 1007
        exception = PyErr_NewException("_libRegex.error", NULL, NULL);
    #else
        exception = Py_BuildValue("s", "_libRegex.error");
    #endif
        PyDict_SetItemString(d, "error", exception);
}

PyObject* py_match(PyObject* self, PyObject* args) {
    char* tomatch;
    char* regex;
    int indFields;
    int exactlymatch = 0;
    
    PyObject *recordedFields = NULL;
	char *answer = NULL;
    // Converts the arguments
    if (!PyArg_ParseTuple(args, "ssi", &regex, &tomatch, &exactlymatch)) {
    	PyErr_SetString(PyExc_TypeError, "Usage: _libRegex.match(regex,message,option) where option = 0 or 1");
        return NULL;
    }

    indFields = matchandalign(&answer,regex,tomatch,exactlymatch,0); 
    if(indFields>=0){
        recordedFields = PyString_FromString(answer);
        free(answer);
        return recordedFields;
    }
    char errormsg[]="Error append during alignment. See standard error output for more infos";      
    Py_XINCREF(exception);
    PyErr_SetObject(exception, Py_BuildValue("s",errormsg));
    return NULL;
}

