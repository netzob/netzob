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

//Compilation Windows
//cl -Fe_libNeedleman.pyd -Ox -Ot -openmp -LD /I"C:\Python26\include" /I"C:\Program Files (x86)\Microsoft Visual Studio 9.0\VC\include" libNeedleman.c "C:\Python26\libs\python26.lib" "C:\Program Files (x86)\Microsoft Visual Studio 9.0\VC\lib\vcomp.lib"

//+---------------------------------------------------------------------------+
//| Import Associated Header
//+---------------------------------------------------------------------------+
#include "libNeedleman.h"
#include <time.h>
#ifdef _WIN32
#include <stdio.h>
#include <malloc.h>
#endif

// The Python callback
extern PyObject *python_callback;

static PyMethodDef libNeedleman_methods[] = {
		{"getBID", py_getBID, METH_NOARGS},
		{"alignTwoMessages", py_alignTwoMessages, METH_VARARGS},
		{"alignMessages", py_alignMessages, METH_VARARGS},
		{NULL, NULL}
};

//+---------------------------------------------------------------------------+
//| initlibNeedleman : Python will use this function to init the module
//+---------------------------------------------------------------------------+
PyMODINIT_FUNC init_libNeedleman(void) {
  (void) Py_InitModule("_libNeedleman", libNeedleman_methods);
}

//+---------------------------------------------------------------------------+
//| py_alignSequences : Python wrapper for alignMessages
//+---------------------------------------------------------------------------+
PyObject* py_alignMessages(PyObject* self, PyObject* args) {

  // Parameters (in order)
  unsigned int doInternalSlick = 0;
  unsigned int nbMessages = 0;
  unsigned char *format;
  int sizeFormat;
  unsigned char *serialMessages;
  int sizeSerialMessages;
  PyObject *temp_cb;
  unsigned int debugMode = 0;
  // local variables
  unsigned int nbDeserializedMessage = 0;
  t_message resMessage;
  t_group group;
  t_score score;
  Bool bool_doInternalSlick;
  Bool bool_debugMode;


  // Converts the arguments
  if (!PyArg_ParseTuple(args, "hhs#s#Oh", &doInternalSlick, &nbMessages, &format, &sizeFormat, &serialMessages, &sizeSerialMessages, &temp_cb, &debugMode)) {
    PyErr_SetString(PyExc_TypeError, "Error while parsing the arguments provided to py_alignMessages");
    return NULL;
  }
  //+------------------------------------------------------------------------+
  // We verify the callback parameter
  //+------------------------------------------------------------------------+
  if (!PyCallable_Check(temp_cb)) {
    PyErr_SetString(PyExc_TypeError, "The provided 7th parameter should be callback");
    return NULL;
  }
  // Parse the callback
  Py_XINCREF(temp_cb);          /* Add a reference to new callback */
  Py_XDECREF(python_callback);  /* Dispose of previous callback */
  python_callback = temp_cb;    /* Remember new callback */

  group.len = nbMessages;
  group.messages = malloc(nbMessages*sizeof(t_message));
  //+------------------------------------------------------------------------+
  // Deserializes the provided arguments
  //+------------------------------------------------------------------------+
  if (debugMode == 1) {
    printf("py_alignSequences : Deserialization of the arguments (format, serialMessages).\n");
  }
  nbDeserializedMessage = deserializeMessages(&group, format, sizeFormat, serialMessages, nbMessages, sizeSerialMessages, debugMode);

  if (nbDeserializedMessage != nbMessages) {
    printf("Error : impossible to deserialize all the provided messages.\n");
    return NULL;
  }
  if (debugMode == 1) {
    printf("A number of %d messages has been deserialized.\n", nbDeserializedMessage);
  }

  // Convert debugMode parameter in a BOOL
  if (debugMode) {
    bool_debugMode = TRUE;
  } else {
    bool_debugMode = FALSE;
  }

  // Concert doInternalSlick parameter in a BOOL
  if (doInternalSlick) {
    bool_doInternalSlick = TRUE;
  } else {
    bool_doInternalSlick = FALSE;
  }

  // Fix the default values associated with resMessage
  score.s1 = 0;
  score.s2 = 0;
  score.s3 = 0;
  resMessage.score = &score;
  resMessage.alignment = malloc(group.messages[0].len * sizeof(unsigned char));
  memset(resMessage.alignment, '\0', group.messages[0].len);
  //+------------------------------------------------------------------------+
  // Execute the alignment process
  //+------------------------------------------------------------------------+
  void (*alignMessagesfunctions[2])(t_message *, Bool , t_group* , Bool )={alignMessages,alignMessages2};
  int t=clock();
  int functionnb = 0;
  (*alignMessagesfunctions[functionnb])(&resMessage, bool_doInternalSlick, &group, bool_debugMode);
  int t1=clock();
  if (debugMode == 1) {
    printf ("It took you for function %d %f operation \n",functionnb, (float)(t1-t)/CLOCKS_PER_SEC);
  }
  
  // Return the results
  return Py_BuildValue("(fffs#s#)", resMessage.score->s1, resMessage.score->s2, resMessage.score->s3, resMessage.alignment, resMessage.len, resMessage.mask, resMessage.len);
}


//+---------------------------------------------------------------------------+
//| py_alignTwoMessages : Python wrapper for alignTwoMessages
//+---------------------------------------------------------------------------+
PyObject* py_alignTwoMessages(PyObject* self, PyObject* args) {
  // Parameters (in order)
  unsigned int doInternalSlick = 0;
  unsigned char *format;
  int sizeFormat;
  unsigned char *serialMessages;
  int sizeSerialMessages;
  unsigned int debugMode = 0;

  // local variables
  unsigned int nbDeserializedMessage = 0;
  t_message message1;
  t_score scoreMessage1;
  t_message message2;
  t_score scoreMessage2;
  t_message resMessage;
  t_score score;
  t_group group;
  Bool bool_doInternalSlick;
  Bool bool_debugMode;

  // Converts the arguments
  if (!PyArg_ParseTuple(args, "hs#s#h", &doInternalSlick, &format, &sizeFormat, &serialMessages, &sizeSerialMessages, &debugMode)) {
    PyErr_SetString(PyExc_TypeError, "Error while parsing the arguments provided to py_alignTwoMessages");
    return NULL;
  }

  //+------------------------------------------------------------------------+
  // Deserializes the provided arguments
  //+------------------------------------------------------------------------+
  if (debugMode == 1) {
    printf("The following arguments were received : \n");
    printf("doInternalSlick : %d\n", doInternalSlick);
    printf("Format :\n");
    hexdump(format, sizeFormat);
    printf("Serial :\n");
    hexdump(serialMessages, sizeSerialMessages);
    printf("Debug mode : %d\n", debugMode);
  }

  // Deserialization of messages
  group.len = 2;
  group.messages = malloc(2*sizeof(t_message));

  nbDeserializedMessage = deserializeMessages(&group, format, sizeFormat, serialMessages, 2, sizeSerialMessages, debugMode);

  if (nbDeserializedMessage != 2) {
    printf("Error : impossible to deserialize all the provided messages.\n");
    return NULL;
  }

  //+------------------------------------------------------------------------+
  // Execute the alignment of two messages
  //+------------------------------------------------------------------------+
  // Convert debugMode parameter in a BOOL
  if (debugMode) {
    bool_debugMode = TRUE;
  } else {
    bool_debugMode = FALSE;
  }

  // Concert doInternalSlick parameter in a BOOL
  if (doInternalSlick) {
    bool_doInternalSlick = TRUE;
  } else {
    bool_doInternalSlick = FALSE;
  }

  // Establishes message1
  message1.len = group.messages[0].len;
  scoreMessage1.s1 = 0;
  scoreMessage1.s2 = 0;
  scoreMessage1.s3 = 0;
  message1.score = &scoreMessage1;
  message1.alignment = group.messages[0].alignment;
  message1.mask  = malloc(group.messages[0].len * sizeof(unsigned char));
  memset(message1.mask, 0, group.messages[0].len);

  // Establishes message2
  message2.len = group.messages[1].len;
  scoreMessage2.s1 = 0;
  scoreMessage2.s2 = 0;
  scoreMessage2.s3 = 0;
  message2.score = &scoreMessage2;
  message2.alignment = group.messages[1].alignment;
  message2.mask  = malloc(group.messages[1].len * sizeof(unsigned char));
  memset(message2.mask, 0, group.messages[1].len);

  // Prepare the response
  resMessage.len = 0;
  score.s1 = 0;
  score.s2 = 0;
  score.s3 = 0;
  resMessage.score = &score;/*
  if (message1.len >= message2.len) {
    resMessage.mask = malloc(message1.len * sizeof(unsigned char));
    memset(resMessage.mask, 0, message1.len);
    resMessage.alignment = malloc(message1.len * sizeof(unsigned char));
    memset(resMessage.alignment, 0, message1.len);
  } else {
    resMessage.mask = malloc(message2.len * sizeof(unsigned char));
    memset(resMessage.mask, 0, message2.len);
    resMessage.alignment = malloc(message2.len * sizeof(unsigned char));
    memset(resMessage.alignment, 0, message2.len);
  }*/
  // Execute the C function
  alignTwoMessages(&resMessage, bool_doInternalSlick, &message1, &message2, bool_debugMode);

  free(message1.mask);
  free(message2.mask);

  // Return the result
  return Py_BuildValue("(fffs#s#)", resMessage.score->s1, resMessage.score->s2, resMessage.score->s3, resMessage.alignment, resMessage.len, resMessage.mask, resMessage.len);
}

