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

//+---------------------------------------------------------------------------+
//| Import Associated Header
//+---------------------------------------------------------------------------+
#include "libInterface.h"
#ifdef _WIN32
#include <stdio.h>
#include <malloc.h>
#endif

// The Python callback
PyObject *python_callback;
PyObject *python_callback_isFinish;

unsigned int deserializeSymbols(PyObject *symbols, Bool debugMode);
PyObject* py_deserializeSymbols(PyObject* self, PyObject* args);

static PyMethodDef libInterface_methods[] = {
  {"getBID", py_getBID, METH_NOARGS, NULL},
  {"deserializeMessages", py_deserializeMessages, METH_VARARGS, NULL},
  {"deserializeGroups", py_deserializeGroups, METH_VARARGS, NULL},
  {"deserializeSymbols",py_deserializeSymbols, METH_VARARGS, NULL},
  {NULL, NULL, 0, NULL}
};
//+---------------------------------------------------------------------------+
//| initlibInterface : Python will use this function to init the module
//+---------------------------------------------------------------------------+
PyObject* PyInit__libInterface(void) {
    static struct PyModuleDef moduledef = {
    PyModuleDef_HEAD_INIT,
    "_libInterface",
    NULL,
    -1,
    libInterface_methods,
    NULL,
    NULL,
    NULL,
    NULL
  };

  return PyModule_Create(&moduledef);
}

int callbackIsFinish(void) {
	if (python_callback_isFinish != NULL) {
			int isFinish;
			PyObject *result_cb;
			result_cb = PyObject_CallObject(python_callback_isFinish, NULL);
			if (result_cb == NULL) {
				return -1;
			}
			if (result_cb == Py_True) {
				isFinish = 1;
			}
			else if (result_cb == Py_False) {
				isFinish = 0;
			} else {
				isFinish = -1;
			}
			Py_DECREF(result_cb);
			return isFinish;
	}
	return -1;
}

//+---------------------------------------------------------------------------+
//| callbackStatus : displays the status or call python wrapper is available
//+---------------------------------------------------------------------------+
int callbackStatus(int stage, double percent, char* message, ...) {
	// Variadic member
	va_list args;

	// local variables
	PyObject *arglist_cb;
	PyObject *result_cb;
	char buffer[4096];

	va_start(args, message);
	vsnprintf(buffer, sizeof(buffer), message, args);
	va_end(args);
	buffer[4095] = '\0';
	if (python_callback != NULL) {
		arglist_cb = Py_BuildValue("(i,d,s)", stage, percent, buffer);
		result_cb = PyObject_CallObject(python_callback, arglist_cb);
		Py_DECREF(arglist_cb);

		if (result_cb == NULL) {
		  return -1;
		}
		Py_DECREF(result_cb);
		return 1;
	}
	else {
		printf("[%f] %s\n", percent, buffer);
		return 1;
	}
	return 0;
}

//+---------------------------------------------------------------------------+
//| py_deserializeMessages : Python wrapper for deserializeMessages
//+---------------------------------------------------------------------------+
PyObject* py_deserializeMessages(__attribute__((unused))PyObject* self, PyObject* args) {
  unsigned int nbMessages = (unsigned int) PyObject_Size(args);
  char *format;
  int sizeFormat;
  unsigned char *serialMessages;
  int sizeSerialMessages;
  unsigned int debugMode = 0;
  unsigned int nbDeserializedMessage = 0;
  t_group group_result;
  // Converts the arguments

  if (!PyArg_ParseTuple(args, "hss#h", &nbMessages, &format, &sizeFormat, &serialMessages, &sizeSerialMessages, &debugMode)) {
    printf("Error while parsing the arguments provided to py_deserializeMessages\n");
    return NULL;
  }

  // Deserializes the provided arguments
  if (debugMode == 1) {
    printf("py_alignSequences : Deserialization of the arguments (format, serialMessages).\n");
  }

  group_result.len = nbMessages;
  group_result.messages = malloc(nbMessages*sizeof(t_message));

  nbDeserializedMessage = deserializeMessages(&group_result, format, serialMessages, nbMessages, debugMode);

  if (nbDeserializedMessage != nbMessages) {
    printf("Error : impossible to deserialize all the provided messages.\n");
    return NULL;
  }

  // cleaning a bit
  free(group_result.messages);

  if(debugMode == 1) {
    printf("All the provided messages were deserialized (%d).\n", nbDeserializedMessage);
  }

  // return the number of deserialized messages
  return Py_BuildValue("i", nbDeserializedMessage);
}




//+---------------------------------------------------------------------------+
//| py_deserializeGroups : Python wrapper for deserializeGroups
//+---------------------------------------------------------------------------+
PyObject* py_deserializeGroups(__attribute__((unused))PyObject* self, PyObject* args) {
  unsigned int nbGroups = 0;
  char *format;
  int sizeFormat;
  unsigned char *serialGroups;
  int sizeSerialGroups;
  unsigned int debugMode = 0;
  unsigned int nbDeserializedGroup = 0;
  t_groups groups_result;

  // Get the number of group (need python>=2.5)
  if(PyObject_Size(args) == -1) {
    printf("The argument has no length");
    return NULL;
  }
  else {
    nbGroups = (unsigned int) PyObject_Size(args);
  }


  // Converts the arguments
  if (!PyArg_ParseTuple(args, "hss#h", &nbGroups, &format, &sizeFormat, &serialGroups, &sizeSerialGroups, &debugMode)) {
    printf("Error while parsing the arguments provided to py_deserializeGroups\n");
    return NULL;
  }

  // Deserializes the provided arguments
  if (debugMode == 1) {
    printf("py_deserializeGroups : Deserialization of the arguments (format, serialGroups).\n");
  }

  groups_result.len = nbGroups;
  groups_result.groups = malloc(nbGroups*sizeof(t_group));

  nbDeserializedGroup = deserializeGroups(&groups_result, format, serialGroups, nbGroups, debugMode);
//  deserializeSymbols(&groups_result, args, debugMode);
  if (nbDeserializedGroup != nbGroups) {
    printf("Error : impossible to deserialize all the provided groups, %d/%d were effectly parsed.\n", nbDeserializedGroup, nbGroups);
    return NULL;
  }

  // cleaning a bit
  free(groups_result.groups);

  if(debugMode == 1) {
    printf("All the provided groups were deserialized (%d).\n", nbDeserializedGroup);
  }

  // return the number of deserialized groups
  return Py_BuildValue("i", nbDeserializedGroup);
}

/********************************************************************
*  deserializeSymbols:
*         push list of symbols in the groups
*
*********************************************************************/
PyObject * py_deserializeSymbols(__attribute__((unused))PyObject* self, PyObject* args) {

     deserializeSymbols(args,0);
     return Py_BuildValue("i", 1);
}
unsigned int deserializeSymbols(PyObject *args, Bool debugMode) {
  PyObject *symbols = PyTuple_GetItem(args, 0);
  int nbGroups = PyObject_Size(symbols);
  int nbScore = 0;
  float tempScore = 0;
  if (nbGroups == -1)
      return 0;
  int i_group = 0;
  int j_group = 0;
  PyObject *current_symbol = NULL;
  PyObject *scoresList = NULL;
  PyObject *current_position = NULL;

  printf("IN\n");
  if (!PyList_Check(symbols))
  {
    printf("The format of the list of symbols given is not a list");
    return 0;
  }
  else {
    if(debugMode == 1) {
      printf("Size %d\n",nbGroups);
      printf("InElse\n");
    }

    for (i_group = 0; i_group <nbGroups; i_group++)  {

      current_position = PyList_GetItem(symbols, i_group);
      printf("Step1\n");
      if (!PyList_Check(current_position))
      {
        printf("The format of the list of symbols given is not a list");
        return 0;
      }
      current_symbol = PyList_GetItem(current_position, 0); // The Symbols Object
      scoresList = PyList_GetItem(current_position, 1);     // The list of scores
      nbScore = PyObject_Size(scoresList);                  // # of scores recorded

      for (j_group = 0; j_group < nbScore ; j_group ++){
        tempScore = (float) PyFloat_AsDouble(PyList_GetItem(scoresList,j_group));
	if(debugMode == 1) {
	  printf("tempScore %f\n",tempScore);
	}

      }
      if(debugMode == 1) {
	printf("END SCORE\n");
      }



      /* Decrease the ref at the end of the loop*/
      if (i_group == nbGroups-1) {
       if(current_position != NULL)
         Py_DECREF(current_position);
       if(current_symbol != NULL)
         Py_DECREF(current_symbol);
       if(scoresList != NULL)
         Py_DECREF(scoresList);
      }
    }
  }
  if(debugMode == 1) {
    printf("End of else\n");
  }


  return 1;
}



