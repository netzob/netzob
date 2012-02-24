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

//+---------------------------------------------------------------------------+
//| Import Associated Header
//+---------------------------------------------------------------------------+
#include "libNeedleman.h"

//+---------------------------------------------------------------------------+
//| initlibNeedleman : Python will use this function to init the module
//+---------------------------------------------------------------------------+
void initlibNeedleman(void) {
  (void) Py_InitModule("libNeedleman", libNeedleman_methods);
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
    printf("[%d] %s\n", percent, buffer);
    return 1;
  }
  return 0;
}



//+---------------------------------------------------------------------------+
//| py_getHighestEquivalenceGroup : Python wrapper for getHighestEquivalenceGroup
//+---------------------------------------------------------------------------+
static PyObject* py_getHighestEquivalentGroup(PyObject* self, PyObject* args) {
  unsigned short int doInternalSlick;
  unsigned short int nbGroups;
  unsigned char * format;
  int sizeFormat;
  unsigned char * serialGroups;
  int sizeSerialGroups;
  PyObject *temp_cb;
  unsigned short int debugMode;

  // local variables
  t_groups groups;
  int nbDeserializedGroups;
  t_equivalentGroup result;
  Bool bool_debugMode;
  Bool bool_doInternalSlick;

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

  // Concert doInternalSlick parameter in a BOOL
  if (doInternalSlick) {
    bool_doInternalSlick = TRUE;
  } else {
    bool_doInternalSlick = FALSE;
  }
  result.i = -1;
  result.j= -1;
  result.score = -1;

  getHighestEquivalentGroup(&result, doInternalSlick, nbGroups, &groups, debugMode);

  if (debugMode) {
    printf("Group 1 i = %d\n", result.i);
    printf("Group 2 j = %d\n", result.j);
    printf("Score : %f\n", result.score);
  }

  if (bool_debugMode == TRUE && result.score == -1) {
    printf("Impossible to compute the highest equivalent set of groups.");
  }

  return Py_BuildValue("(iif)", result.i, result.j, result.score);

}
void getHighestEquivalentGroup(t_equivalentGroup * result, Bool doInternalSlick, int nbGroups, t_groups* groups, Bool debugMode) {
  // Compute the matrix
  float **matrix;
  int i, j;
  float maxScore = -1.0f;
  short int i_maximum = -1;
  short int j_maximum = -1;

  // local variable
  int p = 0;
  double status = 0.0;
  int nbStep;
  double sizeSteps;
  

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


  //  #pragma omp parallel for shared(t_groups, nbGroups, matrix)
    for (i = 0; i < nbGroups; i++) {
      p = 0;

      for (p = 0; p < nbGroups; p++) {
	status += sizeSteps;
        if (i < p) {
          int m, n;
          t_group p_group;
          t_regex regex;
          t_regex regex1;
          t_regex regex2;
          p_group.len = groups->groups[i].len + groups->groups[p].len;
          p_group.messages = malloc(p_group.len * sizeof(t_message));
          for (m = 0; m < groups->groups[i].len; ++m) {
            p_group.messages[m] = groups->groups[i].messages[m];
          }
          for (m = m, n = 0; n < groups->groups[p].len; ++m, ++n) {
            p_group.messages[m] = groups->groups[p].messages[n];
          }

          // Align the messages of the current group
          regex1.len = p_group.messages[0].len;
          regex1.regex = p_group.messages[0].message;
          regex1.mask = p_group.messages[0].mask;

          for (m = 1; m < p_group.len; ++m) {
            regex2.len = p_group.messages[m].len;
            regex2.regex = p_group.messages[m].message;
            regex2.mask = p_group.messages[m].mask;

            alignTwoMessages(&regex, doInternalSlick, &regex1, &regex2, debugMode);

            regex1.len = regex.len;
            regex1.mask = regex.mask;
            regex1.regex = regex.regex;
          }
          //                              omp_set_lock(&my_lock);
          matrix[i][p] = regex.score;
          //                              omp_unset_lock(&my_lock);
	  if (debugMode == TRUE) {
	    printf("matrix %d,%d = %f\n", i, p, regex.score);
	  }

          free( regex.regex );
          free( regex.mask );
          free( p_group.messages );
        }
      }
    }

    for (i = 0; i < nbGroups; ++i) {
      for (j = 0; j < nbGroups; ++j) {
        if (i != j && ((maxScore < matrix[i][j]) || (maxScore == -1))) {
          maxScore = matrix[i][j];
          i_maximum = i;
          j_maximum = j;
        }
      }
    }

    // Room service
    for (i = 0; i < nbGroups; i++) {
      free( matrix[i] );
    }
    free( matrix );

    for (i = 0; i < nbGroups; ++i) {
      free( groups->groups[i].messages );
    }
    free( groups->groups );
    
      // First we fill the matrix with 0s
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
  unsigned short int doInternalSlick;
  unsigned short int nbMessages;
  unsigned char *format;
  int sizeFormat;
  unsigned char *serialMessages;
  int sizeSerialMessages;
  PyObject *temp_cb;
  unsigned short int debugMode;

  // local variables
  unsigned short int nbDeserializedMessage;
  t_regex regex;
  t_group group;
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

  // Fix the default values associated with regex
  regex.score = 0.0;
  regex.regex = malloc(group.messages[0].len * sizeof(unsigned char));
  memset(regex.regex, '\0', group.messages[0].len);
  regex.len = 0;
  regex.mask = malloc(group.messages[0].len * sizeof(unsigned char));
  memset(regex.mask, '\0', group.messages[0].len);
  //+------------------------------------------------------------------------+
  // Execute the alignment process
  //+------------------------------------------------------------------------+
  alignMessages(&regex, bool_doInternalSlick, nbMessages, &group, bool_debugMode);

  // Return the results
  return Py_BuildValue("(fs#s#)", regex.score, regex.regex, regex.len, regex.mask, regex.len);
}
void alignMessages(t_regex *regex, Bool doInternalSlick, unsigned short int nbMessages, t_group* group, Bool debugMode) {
  // local variable
  unsigned short int numberOfOperations;
  double costOfOperation;
  double status = 0.0;

  //+------------------------------------------------------------------------+
  // Estimate the number of operation
  //+------------------------------------------------------------------------+
  numberOfOperations = group->len - 1;
  costOfOperation = 100.0 / numberOfOperations;


  // Local variables
  t_regex current_regex;
  t_regex new_regex;
  unsigned short int i_message;

  // Create a current regex (using first message)
  // current regex = Align N+1 message with current regex
  current_regex.len = group->messages[0].len;
  current_regex.regex = group->messages[0].message;
  current_regex.mask = malloc(group->messages[0].len * sizeof(unsigned char));
  memset(current_regex.mask, 0, group->messages[0].len);

  // Prepare for the regex
  if (group->len == 1) {
    regex->len = current_regex.len;
    regex->mask = current_regex.mask;
    regex->regex = current_regex.regex;
    regex->score = 0.0;
  }
  for (i_message=1; i_message < group->len; i_message++) {
    // Update the execution status
    if (callbackStatus(status, "Consider message %d in the alignment process", i_message) == -1) {
      printf("Error, error while executing C callback.\n");
    }

    new_regex.len = group->messages[i_message].len;
    new_regex.regex = group->messages[i_message].message;
    new_regex.mask = malloc(group->messages[i_message].len * sizeof(unsigned char));
    memset(new_regex.mask, 0, group->messages[i_message].len);

    // Align current_regex with new_regex
    alignTwoMessages(regex, doInternalSlick, &current_regex, &new_regex, debugMode);

    free(current_regex.mask);
    free(new_regex.mask);
    // Copy resut in the current regex
    current_regex.len = regex->len;
    current_regex.regex = regex->regex;
    current_regex.mask = regex->mask;

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
  unsigned short int doInternalSlick;
  unsigned short int nbMessages;
  unsigned char *format;
  int sizeFormat;
  unsigned char *serialMessages;
  int sizeSerialMessages;
  unsigned short int debugMode;

  // local variables
  unsigned short int nbDeserializedMessage;
  t_regex regexMessage1;
  t_regex regexMessage2;
  t_regex regex;
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

  // Establishes regex for message1
  regexMessage1.len = group.messages[0].len;
  regexMessage1.score = 0.0;
  regexMessage1.regex = group.messages[0].message;
  regexMessage1.mask  = malloc(group.messages[0].len * sizeof(unsigned char));
  memset(regexMessage1.mask, 0, group.messages[0].len);

  // Establishes regex for message2
  regexMessage2.len = group.messages[1].len;
  regexMessage2.score = 0.0;
  regexMessage2.regex = group.messages[1].message;
  regexMessage2.mask  = malloc(group.messages[1].len * sizeof(unsigned char));
  memset(regexMessage2.mask, 0, group.messages[1].len);

  // Prepare the response
  regex.len = 0;
  regex.score = 0.0;
  if (regexMessage1.len >= regexMessage2.len) {
    regex.mask = malloc(regexMessage1.len * sizeof(unsigned char));
    memset(regex.mask, 0, regexMessage1.len);
    regex.regex = malloc(regexMessage1.len * sizeof(unsigned char));
    memset(regex.regex, 0, regexMessage1.len);
  } else {
    regex.mask = malloc(regexMessage2.len * sizeof(unsigned char));
    memset(regex.mask, 0, regexMessage2.len);
    regex.regex = malloc(regexMessage2.len * sizeof(unsigned char));
    memset(regex.regex, 0, regexMessage2.len);
  }
  // Execute the C function
  alignTwoMessages(&regex, bool_doInternalSlick, &regexMessage1, &regexMessage2, bool_debugMode);

  free(regexMessage1.mask);
  free(regexMessage2.mask);

  // Return the result
  return Py_BuildValue("(fs#s#)", regex.score, regex.regex, regex.len, regex.mask, regex.len);
}
int alignTwoMessages(t_regex * regex, Bool doInternalSlick, t_regex * regex1, t_regex * regex2, Bool debugMode){
  // local variables
  short int **matrix;
  unsigned short int i = 0;
  unsigned short int j = 0;

  // Construction of the matrix
  short int elt1, elt2, elt3, max, eltL, eltD, eltT;

  // Traceback
  unsigned char *contentRegex1;
  unsigned char *contentRegex2;
  unsigned char *maskRegex1;
  unsigned char *maskRegex2;
  unsigned short int iReg1;
  unsigned short int iReg2;

  // Computing Regex
  unsigned char *regexTmp;
  unsigned char *regexMaskTmp;

  // Computing score of the regex
  float nbDynamic = 0.0f;
  float nbStatic = 0.0f;
  float cent = 100.0f;
  Bool inDyn = FALSE;

  //+------------------------------------------------------------------------+
  // Create and initialize the matrix
  //+------------------------------------------------------------------------+
  matrix = (short int**) malloc( sizeof(short int*) * (regex1->len + 1) );
  for (i = 0; i < (regex1->len + 1); i++) {
    matrix[i] = (short int*) calloc( (regex2->len + 1), sizeof(short int) );
  }
  
  //+------------------------------------------------------------------------+
  // Fullfill the matrix given the two messages
  //+------------------------------------------------------------------------+
  for (i = 1; i < (regex1->len + 1); i++) {
    for (j = 1; j < (regex2->len + 1); j++) {
      /*
        # Matrix[i][j] = MAXIMUM (
        # elt1 :         Matrix[i-1][j-1] + match/mismatch(Matrix[i][j]),
        # elt2 :         Matrix[i][j-1]   + gap,
        # elt3 :         Matrix[i-1][j]   + gap)
      */
      elt1 = matrix[i - 1][j - 1];
      if ( (regex1->mask[i - 1] == 0) && (regex2->mask[j - 1] == 0) && (regex1->regex[i - 1] == regex2->regex[j - 1])) {
        elt1 += MATCH;
      } else {
        elt1 += MISMATCH;
      }
      elt2 = matrix[i][j - 1] + GAP;
      elt3 = matrix[i - 1][j] + GAP;
      max = elt1 > elt2 ? elt1 : elt2;
      max = max > elt3 ? max : elt3;
      matrix[i][j] = max;
    }
  }


  //+------------------------------------------------------------------------+
  // Traceback into the matrix
  //+------------------------------------------------------------------------+
  //finish = FALSE;
  contentRegex1 = calloc( regex1->len + regex2->len, sizeof(unsigned char));
  contentRegex2 = calloc( regex1->len + regex2->len, sizeof(unsigned char));
  maskRegex1 = calloc( regex1->len + regex2->len, sizeof(unsigned char));
  maskRegex2 = calloc( regex1->len + regex2->len, sizeof(unsigned char));

  if (contentRegex1 == NULL) {
    printf("Error while trying to allocate memory for variable : contentRegex1.\n");
    return -1;
  }
  if (contentRegex2 == NULL) {
    printf("Error while trying to allocate memory for variable : contentRegex2.\n");
    return -1;
  }
  if (maskRegex1 == NULL) {
    printf("Error while trying to allocate memory for variable : maskRegex1.\n");
    return -1;
  }
  if (maskRegex2 == NULL) {
    printf("Error while trying to allocate memory for variable : maskRegex2.\n");
    return -1;
  }
  // Fullfill the mask with END like filling it with a '\0'
  memset(maskRegex1, END, (regex1->len + regex2->len) * sizeof(unsigned char));
  memset(maskRegex2, END, (regex1->len + regex2->len) * sizeof(unsigned char));

  // Prepare variables for the traceback
  iReg1 = regex1->len + regex2->len - 1;
  iReg2 = iReg1;
  i = regex1->len;
  j = regex2->len;

  // DIAGONAL (almost) TRACEBACK
  while ((i > 0) && (j > 0)) {
    eltL = matrix[i][j - 1];
    eltD = matrix[i - 1][j - 1];
    eltT = matrix[i - 1][j];

    if ((eltL > eltD) && (eltL > eltT)) {
      --j;

      contentRegex1[iReg1] = 0xf1;
      maskRegex1[iReg1] = DIFFERENT;

      if( regex2->mask[j] == EQUAL) {
        contentRegex2[iReg2] = regex2->regex[j];
        maskRegex2[iReg2] = EQUAL;
      }
      else {
        contentRegex2[iReg2] = 0xf1;
        maskRegex2[iReg2] = DIFFERENT;
      }
    } else if ((eltT >= eltL) && (eltT > eltD)) {
      --i;

      contentRegex2[iReg2] = 0xf2;
      maskRegex2[iReg2] = DIFFERENT;

      if( regex1->mask[i] == EQUAL) {
        contentRegex1[iReg1] = regex1->regex[i];
        maskRegex1[iReg1] = EQUAL;
      }
      else {
        contentRegex1[iReg1] = 0xf2;
        maskRegex1[iReg1] = DIFFERENT;
      }
    } else {
      --i;
      --j;

      if(regex1->mask[i] == EQUAL) {
        contentRegex1[iReg1] = regex1->regex[i];
        maskRegex1[iReg1] = EQUAL;
      }
      else {
        contentRegex1[iReg1] = 0xf2;
        maskRegex1[iReg1] = DIFFERENT;
      }

      if(regex2->mask[j] == EQUAL) {
        contentRegex2[iReg2] = regex2->regex[j];
        maskRegex2[iReg2] = EQUAL;
      }
      else {
        contentRegex2[iReg2] = 0xf2;
        maskRegex2[iReg2] = DIFFERENT;
      }
    }
    --iReg1;
    --iReg2;
  }



  // THE DIAGONAL IS FINISH WE CLOSE THE
  // TRACEBACK BY GOING TO THE EXTREME TOP
  while (i > 0) {
    --i;
    contentRegex2[iReg2] = 0xf3;
    maskRegex2[iReg2] = DIFFERENT;

    if(regex1->mask[i] == EQUAL) {
      contentRegex1[iReg1] = regex1->regex[i];
      maskRegex1[iReg1] = EQUAL;
    }
    else {
      contentRegex1[iReg1] = 0xf3;
      maskRegex1[iReg1] = DIFFERENT;
    }
    --iReg1;
    --iReg2;
  }

  // THE DIAGONAL IS FINISH WE CLOSE THE
  // TRACEBACK BY GOING TO THE EXTREME LEFT
  while (j > 0) {
    --j;
    contentRegex1[iReg1] = 0xf4;
    maskRegex1[iReg1] = DIFFERENT;

    if(regex2->mask[j] == EQUAL) {
      contentRegex2[iReg2] = regex2->regex[j];
      maskRegex2[iReg2] = EQUAL;
    }
    else {
      contentRegex2[iReg2] = 0xf4;
      maskRegex2[iReg2] = DIFFERENT;
    }
    --iReg1;
    --iReg2;
  }

  // For debug only
  if (debugMode == TRUE) {
    printf("Message 1 : ");
    for( i = 0; i < regex1->len + regex2->len; i++) {
      if(maskRegex1[i] == EQUAL ) {
        printf("%02x", (unsigned char) contentRegex1[i]);
      } else if ( maskRegex2[i] == END ) {
        printf("##");
      } else {
        printf("--");
      }
    }
    printf("\n");
    printf("Message 2 : ");
    for( i = 0; i < regex1->len + regex2->len; i++) {
      if( maskRegex2[i] == EQUAL ) {
        printf("%02x", (unsigned char) contentRegex2[i]);
      } else if ( maskRegex2[i] == END ) {
        printf("##");
      } else {
        printf("--");
      }
    }
    printf("\n");
  }

  // Compute the common regex
  regexTmp = calloc(regex1->len + regex2->len, sizeof(unsigned char));
  regexMaskTmp = malloc((regex1->len + regex2->len) * sizeof(unsigned char));
  memset(regexMaskTmp, END, (regex1->len + regex2->len) * sizeof(unsigned char));

  i = regex1->len + regex2->len;
  while (i > 0) {
    --i;
    if ((maskRegex1[i] == END) || (maskRegex2[i] == END)) {
      regexTmp[i] = 0xf9;
      regexMaskTmp[i] = END;
    }
    else if ((maskRegex1[i] == EQUAL) && (maskRegex2[i] == EQUAL) && (contentRegex1[i] == contentRegex2[i])) {
      regexTmp[i] = contentRegex1[i];
      regexMaskTmp[i] = EQUAL;
    }
    else {
      regexTmp[i] = 0xf5;
      regexMaskTmp[i] = DIFFERENT;
    }
  }

  if (debugMode) {
    printf("Result    : ");
    for( i = 0; i < regex1->len + regex2->len; i++) {
      if(regexMaskTmp[i] == EQUAL ) {
        printf("%02x", (unsigned char) regexTmp[i]);
      } else if ( regexMaskTmp[i] == END ) {
        printf("##");
      } else {
        printf("--");
      }
    }
    printf("\n");
  }

  // Try to slick the regex
  if(doInternalSlick == TRUE) {
    for(i = 1; i < regex1->len + regex2->len - 1; i++) {
      if( regexMaskTmp[i] == EQUAL ) {
        if( regexMaskTmp[i - 1] == DIFFERENT ) {
          if( regexMaskTmp[i + 1] == DIFFERENT ) {
            regexTmp[i] = 0xf6;
            regexMaskTmp[i] = DIFFERENT;
          }
        }
      }
    }
  }

  // Compute the score of the regex
  for (i = (regex1->len + regex2->len - 1); i >= 1; --i) {
    if (regexMaskTmp[i] == END) {
      break;
    }

    if (regexMaskTmp[i] == EQUAL) {

      if (inDyn == TRUE) {
        nbDynamic = nbDynamic + 1.0f;
        inDyn = FALSE;
      }
      nbStatic = nbStatic + 1.0f;
    } else if (regexMaskTmp[i] == DIFFERENT) {
      inDyn = TRUE;
    }
  }
  if (inDyn == TRUE)
    nbDynamic = nbDynamic + 1.0f;

  regex->score = 100.0 / (nbStatic + nbDynamic) * nbStatic;
  if (debugMode) {
    printf("Computed score = %0.2f (nbStatic = %0.2f, nbDynamix = %0.2f).\n", regex->score, nbStatic, nbDynamic);
  }

  // Remove the first # of the regex (where mask = END)
  // Retrieve the shortest possible regex
  i = 0;
  while( regexMaskTmp[i] == END )
    i++;

  // Store the results
  regex->len = regex1->len + regex2->len - i;
  regex->regex = malloc(regex->len * sizeof(unsigned char));
  regex->mask = malloc(regex->len * sizeof(unsigned char));
  // TODO: (fgy) free regex.mask and regex.regex
  memcpy(regex->regex, regexTmp + i, regex->len);
  memcpy(regex->mask, regexMaskTmp + i, regex->len);


  // Room service
  for (i = 0; i < (regex1->len + 1); i++) {
    free( matrix[i] );
  }
  free( matrix );
  free(contentRegex1);
  free(contentRegex2);
  free(maskRegex1);
  free(maskRegex2);
  free(regexTmp);
  free(regexMaskTmp);
  return 0;
}





//+---------------------------------------------------------------------------+
//| py_deserializeMessages : Python wrapper for deserializeMessages
//+---------------------------------------------------------------------------+
static PyObject* py_deserializeMessages(PyObject* self, PyObject* args) {
  unsigned short int nbMessages;
  unsigned char *format;
  int sizeFormat;
  unsigned char *serialMessages;
  int sizeSerialMessages;
  unsigned short int debugMode;
  unsigned short int nbDeserializedMessage;

  // Converts the arguments
  if (!PyArg_ParseTuple(args, "hss#h", &nbMessages, &format, &sizeFormat, &serialMessages, &sizeSerialMessages, &debugMode)) {
    printf("Error while parsing the arguments provided to py_deserializeMessages\n");
    return NULL;
  }

  t_group group_result;
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
unsigned short int deserializeMessages(t_group * group, unsigned char *format, int sizeFormat, unsigned char *serialMessages, int nbMessages, int sizeSerialMessages, Bool debugMode) {
  t_message * messages= NULL;
  int i_message = 0;
  unsigned char * p;
  unsigned short int serial_shift = 0;
  unsigned short int format_shift = 0;
  unsigned short int len_size_message=0;
  unsigned short int size_message=0;
  unsigned char * size_message_str;
  unsigned short int nbDeserializedMessages = 0;

  for (i_message=0; i_message < nbMessages; i_message++) {
    // Retrieve the size of each message
    p = strchr(format + format_shift, 'M');
    len_size_message = (unsigned short int) (p - (format + format_shift));
    size_message_str = malloc((len_size_message + 1) * sizeof(unsigned char));
    memcpy(size_message_str, format + format_shift, len_size_message);
    size_message_str[len_size_message] = '\0';
    size_message = atoi(size_message_str);

    // Register the message
    group->messages[i_message].len = size_message;
    group->messages[i_message].message = serialMessages + serial_shift;

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
      hexdump(group->messages[i_message].message, group->messages[i_message].len);
    }
  }
  return nbDeserializedMessages;
}






//+---------------------------------------------------------------------------+
//| py_deserializeGroups : Python wrapper for deserializeGroups
//+---------------------------------------------------------------------------+
static PyObject* py_deserializeGroups(PyObject* self, PyObject* args) {
  unsigned short int nbGroups;
  unsigned char *format;
  int sizeFormat;
  unsigned char *serialGroups;
  int sizeSerialGroups;
  unsigned short int debugMode;
  unsigned short int nbDeserializedGroup;

  // Converts the arguments
  if (!PyArg_ParseTuple(args, "hss#h", &nbGroups, &format, &sizeFormat, &serialGroups, &sizeSerialGroups, &debugMode)) {
    printf("Error while parsing the arguments provided to py_deserializeGroups\n");
    return NULL;
  }

  t_groups groups_result;
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

unsigned short int deserializeGroups(t_groups * groups, unsigned char * format, int sizeFormat, unsigned char * serialGroups, int nbGroups, int sizeSerialGroups, Bool debugMode) {
  int i_group = 0;
  int l = 0;
  unsigned char * p;
  unsigned char *q;
  unsigned short int serial_shift = 0;
  unsigned short int format_shift = 0;
  unsigned short int len_size_group = 0;
  unsigned short int len_size_message = 0;
  unsigned short int size_group = 0;
  unsigned short int size_message = 0;
  unsigned char * size_group_str;
  unsigned char * size_message_str;
  int i_message = 0;


  for (i_group = 0; i_group <nbGroups; i_group++)  {
    // retrieve the number of messages in the current group
    p = strchr(format + format_shift, 'G');
    len_size_group = (unsigned short int) (p - (format + format_shift));
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
      len_size_message = (unsigned short int) (q - (format + format_shift));
      size_message_str = malloc((len_size_message + 1) * sizeof(unsigned char));
      memcpy(size_message_str, format + format_shift, len_size_message);
      size_message_str[len_size_message] = '\0';
      size_message = atoi(size_message_str);
      format_shift += len_size_message + 1;

      // Retrieve the data of each message
      groups->groups[i_group].messages[i_message].len = size_message;
      groups->groups[i_group].messages[i_message].message = serialGroups + l;
      groups->groups[i_group].messages[i_message].mask = serialGroups + l + size_message;

      l += size_message * 2;
      free(size_message_str );
    }
    free(size_group_str);
  }
  return i_group;
}













int hexdump(unsigned char *buf, int dlen) {
  int OPL = 64;
  char c[OPL + 1];
  int i, ct;

  if (dlen < 0) {
    printf("WARNING: computed dlen %d\n", dlen);
    dlen = 0;
  }

  for (i = 0; i < dlen; ++i) {
    if (i == 0)
      printf("DATA: ",c);
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


void dumpRegex(t_regex regex) {
  int i;
  printf("%d ", regex.len);
  for(i = 0; i < regex.len; i++) {
    if(regex.mask[i] == 0)
      printf("%02x", (unsigned char) regex.regex[i]);
    else if(regex.mask[i] == 2)
      printf("##");
    else
      printf("--");
  }
  printf("\n");
}




