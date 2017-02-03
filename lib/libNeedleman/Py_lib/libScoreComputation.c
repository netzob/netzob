// -*- coding: utf-8 -*-

//+---------------------------------------------------------------------------+
//|          01001110 01100101 01110100 01111010 01101111 01100010            |
//|                                                                           |
//|               Netzob : Inferring communication protocols                  |
//+---------------------------------------------------------------------------+
//| Copyright (C) 2011-2016 Georges Bossert and Frédéric Guihéry              |
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
//cl -Fe_libScoreComputation.pyd -Ox -Ot -openmp -LD /I"C:\Python26\include" /I"C:\Program Files (x86)\Microsoft Visual Studio 9.0\VC\include" libScoreComputation.c "C:\Python26\libs\python26.lib" "C:\Program Files (x86)\Microsoft Visual Studio 9.0\VC\lib\vcomp.lib"

//+---------------------------------------------------------------------------+
//| Import Associated Header
//+---------------------------------------------------------------------------+
#include "libScoreComputation.h"
#ifdef _WIN32
#include <stdio.h>
#include <malloc.h>
#endif

// The Python callback
extern PyObject *python_callback;
extern PyObject *python_callback_isFinish;

static PyMethodDef libScoreComputation_methods[] = {
  {"getBID", py_getBID, METH_NOARGS, NULL},
  {"computeSimilarityMatrix", py_computeSimilarityMatrix, METH_VARARGS, NULL},
  {NULL, NULL, 0, NULL}
};

//+---------------------------------------------------------------------------+
//| initlibScoreComputation : Python will use this function to init the module
//+---------------------------------------------------------------------------+
PyObject* PyInit__libScoreComputation(void) {
    static struct PyModuleDef moduledef = {
    PyModuleDef_HEAD_INIT,
    "_libScoreComputation",
    NULL,
    -1,
    libScoreComputation_methods,
    NULL,
    NULL,
    NULL,
    NULL
  };

  return PyModule_Create(&moduledef);
}

//+---------------------------------------------------------------------------+
//| py_computeSimilarityMatrix : Python wrapper for computeSimilarityMatrix
//+---------------------------------------------------------------------------+
PyObject* py_computeSimilarityMatrix(__attribute__((unused))PyObject* self, PyObject* args) {
  unsigned int doInternalSlick = 0;
  unsigned int debugMode = 0;
  int i = 0;
  unsigned int j = 0;
  PyObject *temp_cb;
  PyObject *temp2_cb;
  Bool bool_debugMode;
  PyObject* wrapperFactory;
  float **scoreMatrix = NULL;
  t_message *mesmessages;
  long nbmessage = 0;


  // Converts the arguments
  if (!PyArg_ParseTuple(args, "hOOhO", &doInternalSlick, &temp_cb, &temp2_cb, &debugMode,&wrapperFactory)) {
    PyErr_SetString(PyExc_TypeError, "Error while parsing the arguments provided to py_getHighestEquivalentGroup");
    return NULL;
  }
  if (!PyCallable_Check(temp_cb)) {
      PyErr_SetString(PyExc_TypeError, "The provided argument (status) should be callback");
      return NULL;
  }
  if (!PyCallable_Check(temp2_cb)) {
      PyErr_SetString(PyExc_TypeError, "The provided argument (is finish) should be callback");
      return NULL;
  }

  // Parse the callback
  Py_XINCREF(temp_cb);          /* Add a reference to new callback */
  Py_XDECREF(python_callback);  /* Dispose of previous callback */
  python_callback = temp_cb;    /* Remember new callback */

  // Parse the callback2
  Py_XINCREF(temp2_cb);          /* Add a reference to new callback */
  Py_XDECREF(python_callback_isFinish);  /* Dispose of previous callback */
  python_callback_isFinish = temp2_cb;    /* Remember new callback */

  int parseRet;
  parseRet = parseArgs(wrapperFactory, &nbmessage, &mesmessages);
  //Parsing error: PyErr allready set in parseArgs
  if(parseRet){
    return NULL;
  }

  //init matrix
  scoreMatrix = (float**) malloc (nbmessage*sizeof(float*));
  for(i=0;i<nbmessage;i++)
  {
    scoreMatrix[i] = calloc (nbmessage,sizeof(float*));
  }

  // Convert debugMode parameter in a BOOL
  if (debugMode) {
    bool_debugMode = TRUE;
    printf("Compute Similarity Matrix for %ld messages\n", nbmessage);
  } else {
    bool_debugMode = FALSE;
  }

  computeSimilarityMatrix(nbmessage, mesmessages, bool_debugMode, scoreMatrix);

  //Compute the scores recorded in a python list://TODO Return Factory
  PyObject *recordedScores = PyList_New((nbmessage*(nbmessage-1))/2);
  if (!recordedScores)
    return NULL;
  int i_record = 0;
  int j_record = 0;
  int current_index = 0;
  for (i_record = 0; i_record < nbmessage; i_record++) {
      for(j_record = i_record + 1; j_record < nbmessage; j_record++){

        PyObject *s = PyFloat_FromDouble((double)scoreMatrix[i_record][j_record]);
        PyObject *i_p = PyUnicode_FromString(mesmessages[i_record].uid);
        PyObject *j_p = PyUnicode_FromString(mesmessages[j_record].uid);
        PyObject *res = PyList_New(3);
        if (!s || !i_p || !j_p || !res) {
            Py_XDECREF(recordedScores);
            return NULL;
        }
        PyList_SET_ITEM(res,0,i_p);
        PyList_SET_ITEM(res,1,j_p);
        PyList_SET_ITEM(res,2,s);
        PyList_SET_ITEM(recordedScores, current_index, res);   // reference to num stolen
        current_index++;
     }
  }

  //Free all //TODO: do a freeFactory
  for(i=0; i<nbmessage; i++) {
    for (j=0; j<mesmessages[i].len; j++) {
      free(mesmessages[i].semanticTags[j]);
    }
    free(mesmessages[i].semanticTags);

    free(mesmessages[i].mask);
    free(scoreMatrix[i]);
  }
  free(scoreMatrix);
  free(mesmessages);

  return Py_BuildValue("S", recordedScores);
}



