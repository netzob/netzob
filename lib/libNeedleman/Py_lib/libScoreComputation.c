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
		{"getBID", py_getBID, METH_NOARGS},
		{"getHighestEquivalentGroup", py_getHighestEquivalentGroup, METH_VARARGS},
		{NULL, NULL}
};

//+---------------------------------------------------------------------------+
//| initlibScoreComputation : Python will use this function to init the module
//+---------------------------------------------------------------------------+
PyMODINIT_FUNC init_libScoreComputation(void) {
  (void) Py_InitModule("_libScoreComputation", libScoreComputation_methods);
}

//+---------------------------------------------------------------------------+
//| py_getHighestEquivalenceGroup : Python wrapper for getHighestEquivalenceGroup
//+---------------------------------------------------------------------------+
PyObject* py_getHighestEquivalentGroup(PyObject* self, PyObject* args) {
  unsigned int doInternalSlick = 0;
  unsigned int debugMode = 0;
  int i = 0,j = 0;
  PyObject *temp_cb;
  PyObject *temp2_cb;
  t_equivalentGroup result;
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
  parseRet = parseArgs(wrapperFactory,&nbmessage,&mesmessages);
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
  } else {
    bool_debugMode = FALSE;
  }
  
  getHighestEquivalentGroup2(&result, doInternalSlick, nbmessage, mesmessages, debugMode, scoreMatrix);
  
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
        PyObject *i_p = PyString_FromString(mesmessages[i_record].uid);
        PyObject *j_p = PyString_FromString(mesmessages[j_record].uid);
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
  for(i=0;i<nbmessage;i++)
  {
  	free(mesmessages[i].mask);
  	free(scoreMatrix[i]);
  }
  free(scoreMatrix);
  free(mesmessages);
  return Py_BuildValue("(iifS)", result.i, result.j, result.score,recordedScores);
  
  
  /*//+------------------------------------------------------------------------+
  // We verify the callback parameter
  //+------------------------------------------------------------------------+
  if (!PyCallable_Check(temp_cb)) {
    PyErr_SetString(PyExc_TypeError, "The provided 7th parameter should be callback");
    return NULL;
  }
  // Parse the callback
  Py_XINCREF(temp_cb);          /* Add a reference to new callback /
  Py_XDECREF(python_callback);  /* Dispose of previous callback /
  python_callback = temp_cb;    /* Remember new callback /

  groups.len = nbGroups;
  groups.groups = malloc(nbGroups*sizeof(t_group));
  for(i=0; i<nbGroups-1; i++){
    groups.groups[i].scores = malloc((nbGroups-i-1)*sizeof(float));
    for(j=0;j<nbGroups-i-1;j++){
      groups.groups[i].scores[j] = -1;
    }
  }
  //+------------------------------------------------------------------------+
  // Deserializes the provided arguments
  //+------------------------------------------------------------------------+
  if (debugMode == 1) {
    printf(" Deserialization of the arguments (format, serialMessages).\n");
  }

  nbDeserializedGroups = deserializeGroups(&groups, format, sizeFormat, serialGroups, nbGroups, sizeSerialGroups, debugMode);

  if (nbDeserializedGroups != nbGroups) {
    printf("Error : impossible to deserialize all the provided groups.\n");
    return NULL;
  }
  if (debugMode == 1) {
    printf("A number of %d groups has been deserialized.\n", nbDeserializedGroups);
  }

  // Convert debugMode parameter in a BOOL
  if (debugMode) {
    bool_debugMode = TRUE;
  } else {
    bool_debugMode = FALSE;
  }

 // printf("A number of %d groups has been deserialized.\n", nbDeserializedGroups);
  result.i = -1;
  result.j= -1;
  result.score = -1;

  getHighestEquivalentGroup(&result, doInternalSlick, nbGroups, &groups, debugMode);


//  printf("Gethighest Done\n");

  //Compute the scores recorded in a python list
  PyObject *recordedScores = PyList_New((nbGroups*(nbGroups-1))/2);
  if (!recordedScores)
    return NULL;
  int i_record = 0;
  int j_record = 0;
  int current_index = 0;
  if (!recordedScores)
    return NULL;
  for (i_record = 0; i_record < nbGroups; i_record++) {
      for(j_record = i_record + 1; j_record < nbGroups; j_record++){
        //printf("Scores : %d %d %f\n",i_record,j_record - i_record - 1,groups.groups[i_record].scores[j_record - i_record - 1]);
        
        PyObject *s = PyFloat_FromDouble((double)groups.groups[i_record].scores[j_record - i_record - 1]);
        PyObject *i_p = PyInt_FromLong((long)i_record);
        PyObject *j_p = PyInt_FromLong((long)j_record);
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

  if (debugMode) {
    printf("Group 1 i = %d\n", result.i);
    printf("Group 2 j = %d\n", result.j);
    printf("Score : %f\n", result.score);
  }

  if (bool_debugMode == TRUE && result.score == -1) {
    printf("Impossible to compute the highest equivalent set of groups.");
  }

  //We need to free the groups. We cannot do this before as we need scores to be recorded
  for (i = 0; i < nbGroups; ++i) {
      free( groups.groups[i].messages );
      if(i < nbGroups-1){
          free(groups.groups[i].scores);}
    }
  free( groups.groups );
  return Py_BuildValue("(iifS)", result.i, result.j, result.score,recordedScores);*/
}



