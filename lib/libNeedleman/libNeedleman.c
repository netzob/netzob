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
#ifdef _WIN32
#include <stdio.h>
#include <malloc.h>
#endif


static PyMethodDef libNeedleman_methods[] = {
  {"getHighestEquivalentGroup", py_getHighestEquivalentGroup, METH_VARARGS},
  {"alignMessages", py_alignMessages, METH_VARARGS},
  {"alignTwoMessages", py_alignTwoMessages, METH_VARARGS},
  {"deserializeMessages", py_deserializeMessages, METH_VARARGS},
  {"deserializeGroups", py_deserializeGroups, METH_VARARGS},
  {NULL, NULL}
};

//+---------------------------------------------------------------------------+
//| initlibNeedleman : Python will use this function to init the module
//+---------------------------------------------------------------------------+
PyMODINIT_FUNC init_libNeedleman(void) {
  (void) Py_InitModule("_libNeedleman", libNeedleman_methods);
}
//+---------------------------------------------------------------------------+
//| callbackStatus : displays the status or call python wrapper is available
//+---------------------------------------------------------------------------+
int callbackStatus(double percent, char* message, ...) {
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
    arglist_cb = Py_BuildValue("(d,s)", percent, buffer);
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
//| py_getHighestEquivalenceGroup : Python wrapper for getHighestEquivalenceGroup
//+---------------------------------------------------------------------------+
static PyObject* py_getHighestEquivalentGroup(PyObject* self, PyObject* args) {
  unsigned int doInternalSlick = 0;
  unsigned int nbGroups = 0;
  unsigned char * format;
  int sizeFormat;
  unsigned char * serialGroups;
  int sizeSerialGroups;
  unsigned int debugMode = 0;
  int i = 0 ,j = 0;
  int nbDeserializedGroups;
  PyObject *temp_cb;
  t_groups groups;
  t_equivalentGroup result;
  Bool bool_debugMode;

  // Converts the arguments
  if (!PyArg_ParseTuple(args, "hhs#s#Oh", &doInternalSlick, &nbGroups, &format, &sizeFormat, &serialGroups, &sizeSerialGroups, &temp_cb, &debugMode)) {
    PyErr_SetString(PyExc_TypeError, "Error while parsing the arguments provided to py_getHighestEquivalentGroup");
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
  for (i_record = 0; i_record < nbGroups; i_record++) {
      for(j_record = i_record + 1; j_record < nbGroups; j_record++){
	//        printf("Scores : %d %d %f\n",i_record,j_record - i_record - 1,groups.groups[i_record].scores[j_record - i_record - 1]);
        
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
  return Py_BuildValue("(iifS)", result.i, result.j, result.score,recordedScores);
}
void getHighestEquivalentGroup(t_equivalentGroup * result, Bool doInternalSlick, int nbGroups, t_groups* groups, Bool debugMode) {
  // Compute the matrix
  float **matrix;
  int i, j;
  float maxScore = -1.0f;
  int i_maximum = -1;
  int j_maximum = -1;
  // local variable
  int p = 0;
  double status = 0.0;

  // First we fill the matrix with 0s
  if (callbackStatus(status, "Building the scoring matrix for %d groups", nbGroups) == -1) {
    printf("Error, error while executing C callback.\n");
  }

  matrix = (float **) malloc( nbGroups * sizeof(float*) );
  for (i = 0; i < nbGroups; i++) {
    matrix[i] = (float *) malloc( sizeof(float) * nbGroups );
    for(j = 0; j < nbGroups; j++) {
      matrix[i][j] = 0.0;
    }
  }
  
  status = 2.0;


  #pragma omp parallel for shared(result,groups, nbGroups, matrix,debugMode,doInternalSlick,maxScore,i_maximum,j_maximum) private(i,p)
  // We loop over each couple of groups
  for (i = 0; i < nbGroups; i++) {
    for (p = i + 1; p < nbGroups; p++) {
      if(groups->groups[i].scores[p-i-1]==-1){//Check if the score has been allready computed 
	int m, n;
	float finalScore = 0.0;
	t_message tmpMessage;
	t_score score;
	tmpMessage.score = &score;
	
	// We loop over each couple of messages
	for (m = 0; m < groups->groups[i].len; ++m) {
	  for (n = 0; n < groups->groups[p].len; ++n) {
	    score.s1 = 0;
	    score.s2 = 0;
	    score.s3 = 0;
	    alignTwoMessages(&tmpMessage, doInternalSlick, &groups->groups[i].messages[m], &groups->groups[p].messages[n], debugMode);
	    finalScore += computeDistance( tmpMessage.score );
	  }
	}
	{
          matrix[i][p] = finalScore / (groups->groups[i].len * groups->groups[p].len); 
	  (&groups->groups[i])->scores[p-i-1] = matrix[i][p];
	}
      }
      else{
	matrix[i][p] = groups->groups[i].scores[p-i-1];// Put the score allready computed
      }
      
      if (((maxScore < matrix[i][p]) || (maxScore == -1))) {
	maxScore = matrix[i][p];
	i_maximum = i;
	j_maximum = p;
      }
      
      if (debugMode) {
	printf("matrix %d,%d = %f\n", i, p, matrix[i][p]);
      }
    }
  }
  
  // Room service
  for (i = 0; i < nbGroups; i++) {
    free( matrix[i] );
  }
  free( matrix );

  if (callbackStatus(status, "Two equivalent groups were found.") == -1) {
    printf("Error, error while executing C callback.\n");
  }

  result->i = i_maximum;
  result->j = j_maximum;
  result->score = maxScore;
}

//+---------------------------------------------------------------------------+
//| py_alignSequences : Python wrapper for alignMessages
//+---------------------------------------------------------------------------+
static PyObject* py_alignMessages(PyObject* self, PyObject* args) {
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
  resMessage.len = 0;
  resMessage.mask = malloc(group.messages[0].len * sizeof(unsigned char));
  memset(resMessage.mask, '\0', group.messages[0].len);
  //+------------------------------------------------------------------------+
  // Execute the alignment process
  //+------------------------------------------------------------------------+
  alignMessages(&resMessage, bool_doInternalSlick, nbMessages, &group, bool_debugMode);

  // Return the results
  return Py_BuildValue("(fffs#s#)", resMessage.score->s1, resMessage.score->s2, resMessage.score->s3, resMessage.alignment, resMessage.len, resMessage.mask, resMessage.len);
}
void alignMessages(t_message *resMessage, Bool doInternalSlick, unsigned int nbMessages, t_group* group, Bool debugMode) {
  // local variable
  unsigned int numberOfOperations = 0;
  double costOfOperation;
  double status = 0.0;
  
  // Local variables
  t_message current_message;
  t_message new_message;
  t_score score;
  unsigned int i_message = 0;
  
  score.s1 = 0;
  score.s2 = 0;
  score.s3 = 0;
  score.value = 0;
  
  //+------------------------------------------------------------------------+
  // Estimate the number of operation
  //+------------------------------------------------------------------------+
  numberOfOperations = group->len - 1;
  costOfOperation = 100.0 / numberOfOperations;

  // Create a current message (using first message)
  // current message = Align N+1 message with current message
  current_message.len = group->messages[0].len;
  current_message.alignment = group->messages[0].alignment;
  current_message.mask = malloc(group->messages[0].len * sizeof(unsigned char));
  memset(current_message.mask, 0, group->messages[0].len);
  current_message.score = &score;

  // Prepare for the resMessage
  if (group->len == 1) {
    resMessage->len = current_message.len;
    resMessage->mask = current_message.mask;
    resMessage->alignment = current_message.alignment;
    resMessage->score = current_message.score;
  }
  for (i_message=1; i_message < group->len; i_message++) {
    // Update the execution status
    if (callbackStatus(status, "Consider message %d in the alignment process", i_message) == -1) {
      printf("Error, error while executing C callback.\n");
    }

    new_message.len = group->messages[i_message].len;
    new_message.alignment = group->messages[i_message].alignment;
    new_message.mask = malloc(group->messages[i_message].len * sizeof(unsigned char));
    memset(new_message.mask, 0, group->messages[i_message].len);

    // Align current_message with new_message
    alignTwoMessages(resMessage, doInternalSlick, &current_message, &new_message, debugMode);

    free(current_message.mask);
    free(new_message.mask);
    // Copy result in the current message
    current_message.len = resMessage->len;
    current_message.alignment = resMessage->alignment;
    current_message.mask = resMessage->mask;

    //udpate status
    status += costOfOperation;
  }

  // Update the execution status
  if (callbackStatus(status, "The %d messages have sucessfully been aligned.", group->len) == -1) {
    printf("Error, error while executing C callback.\n");
  }


  free(group->messages);
}
//+---------------------------------------------------------------------------+
//| py_alignTwoMessages : Python wrapper for alignTwoMessages
//+---------------------------------------------------------------------------+
static PyObject* py_alignTwoMessages(PyObject* self, PyObject* args) {
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
  resMessage.score = &score;
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
  }
  // Execute the C function
  alignTwoMessages(&resMessage, bool_doInternalSlick, &message1, &message2, bool_debugMode);

  free(message1.mask);
  free(message2.mask);

  // Return the result
  return Py_BuildValue("(fffs#s#)", resMessage.score->s1, resMessage.score->s2, resMessage.score->s3, resMessage.alignment, resMessage.len, resMessage.mask, resMessage.len);
}
int alignTwoMessages(t_message * resMessage, Bool doInternalSlick, t_message * message1, t_message * message2, Bool debugMode){
  // local variables
  short int **matrix;
  unsigned int i = 0;
  unsigned int j = 0;

  // Construction of the matrix
  short int elt1, elt2, elt3, max, eltL, eltD, eltT;
  // Levenshtein distance
  float levenshtein = 0.0;
  unsigned int maxLen = 0;
  // Traceback
  unsigned char *contentMessage1;
  unsigned char *contentMessage2;
  unsigned char *maskMessage1;
  unsigned char *maskMessage2;
  unsigned int iReg1 = 0;
  unsigned int iReg2 = 0;

  // Computing resMessage
  unsigned char *tmpMessage;
  unsigned char *tmpMessageMask;

  // Score computation
  unsigned int nbDynTotal = 0;
  unsigned int nbDynCommon = 0;

  //+------------------------------------------------------------------------+
  // Create and initialize the matrix
  //+------------------------------------------------------------------------+
  matrix = (short int**) malloc( sizeof(short int*) * (message1->len + 1) );
  for (i = 0; i < (message1->len + 1); i++) {
    matrix[i] = (short int*) calloc( (message2->len + 1), sizeof(short int) );
  }
  
  //+------------------------------------------------------------------------+
  // Fullfill the matrix given the two messages
  //+------------------------------------------------------------------------+
  maxLen = message1->len > message2->len ? message1->len : message2->len;
  for (i = 1; i < (message1->len + 1); i++) {
    for (j = 1; j < (message2->len + 1); j++) {
      /*
        # Matrix[i][j] = MAXIMUM (
        # elt1 :         Matrix[i-1][j-1] + match/mismatch(Matrix[i][j]),
        # elt2 :         Matrix[i][j-1]   + gap,
        # elt3 :         Matrix[i-1][j]   + gap)
      */
      elt1 = matrix[i - 1][j - 1];
      if ( (message1->mask[i - 1] == 0) && (message2->mask[j - 1] == 0) && (message1->alignment[i - 1] == message2->alignment[j - 1])) {
        elt1 += MATCH;
      } else {
        elt1 += MISMATCH;
      }
      elt2 = matrix[i][j - 1] + GAP;
      elt3 = matrix[i - 1][j] + GAP;
      max = elt1 > elt2 ? elt1 : elt2;
      max = max > elt3 ? max : elt3;
      matrix[i][j] = max;
      levenshtein = levenshtein < max ? (float)max : levenshtein;
    }
  }
  levenshtein = levenshtein * 10 / maxLen;

  //+------------------------------------------------------------------------+
  // Traceback into the matrix
  //+------------------------------------------------------------------------+
  //finish = FALSE;
  contentMessage1 = calloc( message1->len + message2->len, sizeof(unsigned char));
  contentMessage2 = calloc( message1->len + message2->len, sizeof(unsigned char));
  maskMessage1 = calloc( message1->len + message2->len, sizeof(unsigned char));
  maskMessage2 = calloc( message1->len + message2->len, sizeof(unsigned char));

  if (contentMessage1 == NULL) {
    printf("Error while trying to allocate memory for variable : contentMessage1.\n");
    return -1;
  }
  if (contentMessage2 == NULL) {
    printf("Error while trying to allocate memory for variable : contentMessage2.\n");
    return -1;
  }
  if (maskMessage1 == NULL) {
    printf("Error while trying to allocate memory for variable : maskMessage1.\n");
    return -1;
  }
  if (maskMessage2 == NULL) {
    printf("Error while trying to allocate memory for variable : maskMessage2.\n");
    return -1;
  }
  // Fullfill the mask with END like filling it with a '\0'
  memset(maskMessage1, END, (message1->len + message2->len) * sizeof(unsigned char));
  memset(maskMessage2, END, (message1->len + message2->len) * sizeof(unsigned char));

  // Prepare variables for the traceback
  iReg1 = message1->len + message2->len - 1;
  iReg2 = iReg1;
  i = message1->len;
  j = message2->len;

  // DIAGONAL (almost) TRACEBACK
  while ((i > 0) && (j > 0)) {
    eltL = matrix[i][j - 1];
    eltD = matrix[i - 1][j - 1];
    eltT = matrix[i - 1][j];

    if ((eltL > eltD) && (eltL > eltT)) {
      --j;

      contentMessage1[iReg1] = 0xf1;
      maskMessage1[iReg1] = DIFFERENT;

      if( message2->mask[j] == EQUAL) {
        contentMessage2[iReg2] = message2->alignment[j];
        maskMessage2[iReg2] = EQUAL;
      }
      else {
        contentMessage2[iReg2] = 0xf1;
        maskMessage2[iReg2] = DIFFERENT;
      }
    } else if ((eltT >= eltL) && (eltT > eltD)) {
      --i;

      contentMessage2[iReg2] = 0xf2;
      maskMessage2[iReg2] = DIFFERENT;

      if( message1->mask[i] == EQUAL) {
        contentMessage1[iReg1] = message1->alignment[i];
        maskMessage1[iReg1] = EQUAL;
      }
      else {
        contentMessage1[iReg1] = 0xf2;
        maskMessage1[iReg1] = DIFFERENT;
      }
    } else {
      --i;
      --j;

      if(message1->mask[i] == EQUAL) {
        contentMessage1[iReg1] = message1->alignment[i];
        maskMessage1[iReg1] = EQUAL;
      }
      else {
        contentMessage1[iReg1] = 0xf2;
        maskMessage1[iReg1] = DIFFERENT;
      }

      if(message2->mask[j] == EQUAL) {
        contentMessage2[iReg2] = message2->alignment[j];
        maskMessage2[iReg2] = EQUAL;
      }
      else {
        contentMessage2[iReg2] = 0xf2;
        maskMessage2[iReg2] = DIFFERENT;
      }
    }
    --iReg1;
    --iReg2;
  }



  // THE DIAGONAL IS FINISH WE CLOSE THE
  // TRACEBACK BY GOING TO THE EXTREME TOP
  while (i > 0) {
    --i;
    contentMessage2[iReg2] = 0xf3;
    maskMessage2[iReg2] = DIFFERENT;

    if(message1->mask[i] == EQUAL) {
      contentMessage1[iReg1] = message1->alignment[i];
      maskMessage1[iReg1] = EQUAL;
    }
    else {
      contentMessage1[iReg1] = 0xf3;
      maskMessage1[iReg1] = DIFFERENT;
    }
    --iReg1;
    --iReg2;
  }

  // THE DIAGONAL IS FINISH WE CLOSE THE
  // TRACEBACK BY GOING TO THE EXTREME LEFT
  while (j > 0) {
    --j;
    contentMessage1[iReg1] = 0xf4;
    maskMessage1[iReg1] = DIFFERENT;

    if(message2->mask[j] == EQUAL) {
      contentMessage2[iReg2] = message2->alignment[j];
      maskMessage2[iReg2] = EQUAL;
    }
    else {
      contentMessage2[iReg2] = 0xf4;
      maskMessage2[iReg2] = DIFFERENT;
    }
    --iReg1;
    --iReg2;
  }

  // For debug only
  if (debugMode == TRUE) {
    printf("Message 1 : ");
    for( i = 0; i < message1->len + message2->len; i++) {
      if(maskMessage1[i] == EQUAL ) {
        printf("%02x", (unsigned char) contentMessage1[i]);
      } else if ( maskMessage2[i] == END ) {
        //printf("##");
      } else {
        printf("--");
      }
    }
    printf("\n");
    printf("Message 2 : ");
    for( i = 0; i < message1->len + message2->len; i++) {
      if( maskMessage2[i] == EQUAL ) {
        printf("%02x", (unsigned char) contentMessage2[i]);
      } else if ( maskMessage2[i] == END ) {
        //printf("##");
      } else {
        printf("--");
      }
    }
    printf("\n");
  }

  // Compute the common alignment
  tmpMessage = calloc(message1->len + message2->len, sizeof(unsigned char));
  tmpMessageMask = malloc((message1->len + message2->len) * sizeof(unsigned char));
  memset(tmpMessageMask, END, (message1->len + message2->len) * sizeof(unsigned char));

  i = message1->len + message2->len;
  while (i > 0) {
    --i;
    if ((maskMessage1[i] == END) || (maskMessage2[i] == END)) {
      tmpMessage[i] = 0xf9;
      tmpMessageMask[i] = END;
    }
    else if ((maskMessage1[i] == EQUAL) && (maskMessage2[i] == EQUAL) && (contentMessage1[i] == contentMessage2[i])) {
      tmpMessage[i] = contentMessage1[i];
      tmpMessageMask[i] = EQUAL;
    }
    else {
      tmpMessage[i] = 0xf5;
      tmpMessageMask[i] = DIFFERENT;

      nbDynTotal += 1;
      if ((maskMessage1[i] == EQUAL) && (maskMessage2[i] == EQUAL)) {
	nbDynCommon += 1;
      }      
    }
  }

  // Try to (optionally) slick the alignment
  if(doInternalSlick == TRUE) {
    for(i = 1; i < message1->len + message2->len - 1; i++) {
      if( tmpMessageMask[i] == EQUAL ) {
        if( tmpMessageMask[i - 1] == DIFFERENT ) {
          if( tmpMessageMask[i + 1] == DIFFERENT ) {
            tmpMessage[i] = 0xf6;
            tmpMessageMask[i] = DIFFERENT;
          }
        }
      }
    }
  }

  // Create the alignment based on obtained data
  // Remove the first # of the alignment (where mask = END)
  // Retrieve the shortest possible alignment
  i = 0;
  while( tmpMessageMask[i] == END )
    i++;

  // Store the results
  resMessage->len = message1->len + message2->len - i;
  resMessage->alignment = malloc(resMessage->len * sizeof(unsigned char));
  resMessage->mask = malloc(resMessage->len * sizeof(unsigned char));
  // TODO: (fgy) free resMessage.mask and resMessage.alignment
  memcpy(resMessage->alignment, tmpMessage + i, resMessage->len);
  memcpy(resMessage->mask, tmpMessageMask + i, resMessage->len);


  // Compute the scores of similarity, using the resMessage
  if (debugMode) {
    printf("Result    : ");
    for( i = 0; i < resMessage->len; i++) {
      if(resMessage->mask[i] == EQUAL ) {
        printf("%02x", (unsigned char) resMessage->alignment[i]);
      } else if ( resMessage->mask[i] == END ) {
        //printf("##");
      } else {
        printf("--");
      }
    }
    printf("\n");
  }


  // COMPUTE THE SCORES
  // Using the resMessage, we compute the multiple scores
  resMessage->score->s1 = getScoreRatio(resMessage);
  resMessage->score->s2 = getScoreDynSize(nbDynTotal, nbDynCommon);
  resMessage->score->s3 = levenshtein;

  if (debugMode) {
    printf("Score ratio : %0.2f.\n", resMessage->score->s1);
    printf("Score DynSize : %0.2f.\n", resMessage->score->s2);
    printf("Score Rang : %0.2f.\n", resMessage->score->s3);
  }


  // Room service
  for (i = 0; i < (message1->len + 1); i++) {
    free( matrix[i] );
  }
  free( matrix );
  free(contentMessage1);
  free(contentMessage2);
  free(maskMessage1);
  free(maskMessage2);
  free(tmpMessage);
  free(tmpMessageMask);
  return 0;
}


float getScoreRatio(t_message * message) {
  // Computing score of the alignment
  float nbDynamic = 0.0f;
  float nbStatic = 0.0f;
  Bool inDyn = FALSE;
  int i=0;
  float result = 0;

  for (i = (message->len - 1); i >= 1; --i) {
    if (message->mask[i] == END) {
      break;
    }
    if (message->mask[i] == EQUAL) {
      if (inDyn == TRUE) {
        nbDynamic = nbDynamic + 1.0f;
        inDyn = FALSE;
      }
      nbStatic = nbStatic + 1.0f;
    } else if (message->mask[i] == DIFFERENT) {
      inDyn = TRUE;
    }
  }
  if (inDyn == TRUE)
    nbDynamic = nbDynamic + 1.0f;
  if(nbStatic == 0){
    result = 0;
  }
  else {
  result = 100.0 / (nbStatic + nbDynamic) * nbStatic;
  }
  return result;
}
float getScoreDynSize(unsigned int nbDynTotal, unsigned int nbDynCommon) {
  // Compute score of common dynamic elements
  float result = 0;
  if(nbDynTotal == 0) {
    result = 100;
  }
  else {
    result = (100.0 - 1) / nbDynTotal * nbDynCommon;
  }
  return result;
}
float getScoreRang(t_message * message) {
  float result = 0;
  
  return result;
}
float computeDistance(t_score * score) {
  float result = 0;
  result = sqrt(0.0 * pow(score->s1,2) + 0.0 * pow(score->s2,2) + 1.0 * pow(score->s3,2));
  return result;
}
  
 



//+---------------------------------------------------------------------------+
//| py_deserializeMessages : Python wrapper for deserializeMessages
//+---------------------------------------------------------------------------+
static PyObject* py_deserializeMessages(PyObject* self, PyObject* args) {
  unsigned int nbMessages = 0;
  unsigned char *format;
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

  nbDeserializedMessage = deserializeMessages(&group_result, format, sizeFormat, serialMessages, nbMessages, sizeSerialMessages, debugMode);

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
//| deserializeMessages : Deserialization of messages
//+---------------------------------------------------------------------------+
unsigned int deserializeMessages(t_group * group, unsigned char *format, int sizeFormat, unsigned char *serialMessages, int nbMessages, int sizeSerialMessages, Bool debugMode) {
  int i_message = 0;
  unsigned char * p;
  unsigned int serial_shift = 0;
  unsigned int format_shift = 0;
  unsigned int len_size_message=0;
  unsigned int size_message=0;
  unsigned char * size_message_str;
  unsigned int nbDeserializedMessages = 0;

  for (i_message=0; i_message < nbMessages; i_message++) {
    // Retrieve the size of each message
    p = strchr(format + format_shift, 'M');
    len_size_message = (unsigned int) (p - (format + format_shift));
    size_message_str = malloc((len_size_message + 1) * sizeof(unsigned char));
    memcpy(size_message_str, format + format_shift, len_size_message);
    size_message_str[len_size_message] = '\0';
    size_message = atoi(size_message_str);

    // Register the message
    group->messages[i_message].len = size_message;
    group->messages[i_message].alignment = serialMessages + serial_shift;
    group->messages[i_message].mask = malloc(size_message * sizeof(unsigned char));
    memset(group->messages[i_message].mask, '\0', size_message);
    t_score score;
    group->messages[i_message].score = &score;

    nbDeserializedMessages += 1;

    format_shift = format_shift + len_size_message + 1;
    serial_shift = serial_shift + size_message;

    // Cleaning useless allocated memory
    free(size_message_str);
  }

  if (debugMode == TRUE) {
    printf("A number of %d messages has been deserialized.\n", nbDeserializedMessages);
    for (i_message = 0; i_message<nbDeserializedMessages; i_message++) {
      printf("Message %d : \n", i_message);
      hexdump(group->messages[i_message].alignment, group->messages[i_message].len);
    }
  }
  return nbDeserializedMessages;
}






//+---------------------------------------------------------------------------+
//| py_deserializeGroups : Python wrapper for deserializeGroups
//+---------------------------------------------------------------------------+
static PyObject* py_deserializeGroups(PyObject* self, PyObject* args) {
  unsigned int nbGroups = 0;
  unsigned char *format;
  int sizeFormat;
  unsigned char *serialGroups;
  int sizeSerialGroups;
  unsigned int debugMode = 0;
  unsigned int nbDeserializedGroup = 0;
  t_groups groups_result;
  
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

  nbDeserializedGroup = deserializeGroups(&groups_result, format, sizeFormat, serialGroups, nbGroups, sizeSerialGroups, debugMode);

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

unsigned int deserializeGroups(t_groups * groups, unsigned char * format, int sizeFormat, unsigned char * serialGroups, int nbGroups, int sizeSerialGroups, Bool debugMode) {
  int i_group = 0;
  int j_group = 0;
  int l = 0;
  unsigned char * p;
  unsigned char *q;
  unsigned char *r;
  unsigned char *s;
  unsigned short int format_shift = 0;
  unsigned int len_size_group = 0;
  unsigned int len_size_message = 0;
  unsigned int len_score_group = 0;
  unsigned int size_group = 0;
  unsigned int size_message = 0;
  unsigned char * size_group_str;
  unsigned char * size_message_str;
  unsigned char * score_group;
  int i_message = 0;

  for (i_group = 0; i_group <nbGroups; i_group++)  {
    //Retrieve the precompiled scores
    s = strchr(format + format_shift, 'E');
    if (s != NULL){ // Used for compatibility between version
      for (j_group = i_group + 1; j_group < nbGroups ; j_group ++){
        r = strchr(format + format_shift, 'S');
        if (r!=NULL && (int) (s - r) > 0){
          len_score_group = (unsigned int) (r - (format + format_shift));
          score_group = malloc((len_score_group + 1) * sizeof(unsigned char));
          memcpy(score_group, format + format_shift, len_score_group);
          score_group[len_score_group]='\0';
          groups->groups[i_group].scores[j_group-(i_group+1)] = atof(score_group);
          format_shift += len_score_group + 1;
          free(score_group);
        }
        else{
          break;
        }
      }
    format_shift += 1; // FOR LETTER 'E'*/
    }
    // retrieve the number of messages in the current group
    p = strchr(format + format_shift, 'G');
    len_size_group = (unsigned int) (p - (format + format_shift));
    size_group_str = malloc((len_size_group + 1) * sizeof(unsigned char));
    memcpy(size_group_str, format + format_shift, len_size_group);
    size_group_str[len_size_group] = '\0';
    size_group = atoi(size_group_str);
    format_shift += len_size_group + 1;

    // Allocate pointers to store the messages of current group
    groups->groups[i_group].len = size_group;
    groups->groups[i_group].messages = malloc(size_group * sizeof(t_message));

    for (i_message = 0; i_message < size_group; i_message++) {
      // Retrieve the size of each message
      q = strchr(format + format_shift, 'M');
      len_size_message = (unsigned int) (q - (format + format_shift));
      size_message_str = malloc((len_size_message + 1) * sizeof(unsigned char));
      memcpy(size_message_str, format + format_shift, len_size_message);
      size_message_str[len_size_message] = '\0';
      size_message = atoi(size_message_str);
      format_shift += len_size_message + 1;

      // Retrieve the data of each message
      groups->groups[i_group].messages[i_message].len = size_message;
      groups->groups[i_group].messages[i_message].alignment = serialGroups + l;
      groups->groups[i_group].messages[i_message].mask = serialGroups + l + size_message;

      l += size_message * 2;
      free(size_message_str );
    }
    free(size_group_str);
  }
  return i_group;
}









#define OPL 64

void hexdump(unsigned char *buf, int dlen) {
  char c[OPL + 1];
  int i, ct;

  if (dlen < 0) {
    printf("WARNING: computed dlen %d\n", dlen);
    dlen = 0;
  }

  for (i = 0; i < dlen; ++i) {
    if (i == 0)
      printf("DATA: ");
    else if ((i % OPL) == 0) {
      c[OPL] = '\0';
      printf("\t\"%s\"\nDATA: ", c);
    }
    ct = buf[i] & 0xff;
    c[i % OPL] = (ct >= ' ' && ct <= '~') ? ct : '.';
    printf("%02x ", ct);
  }
  c[i % OPL] = '\0';
  for (; i % OPL; ++i)
    printf("   ");
  printf("\t\"%s\"\n", c);
}


void dumpMessage(t_message message) {
  int i;
  printf("%d ", message.len);
  for(i = 0; i < message.len; i++) {
    if(message.mask[i] == 0)
      printf("%02x", (unsigned char) message.alignment[i]);
    else if(message.mask[i] == 2)
      printf("##");
    else
      printf("--");
  }
  printf("\n");
}




