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
//cl -Fe_libNeedleman.pyd -Ox -Ot -openmp -LD /I"C:\Python26\include" /I"C:\Program Files (x86)\Microsoft Visual Studio 9.0\VC\include" libNeedleman.c "C:\Python26\libs\python26.lib" "C:\Program Files (x86)\Microsoft Visual Studio 9.0\VC\lib\vcomp.lib"

//+---------------------------------------------------------------------------+
//| Import Associated Header
//+---------------------------------------------------------------------------+
#include "factory.h"

/*parseArgs return values:
*	0: Success
*	1: not yet implemented
*	2: not WrapperFactory
*/
int parseArgs(PyObject* factobj, ...){
  PyObject* wrapperObj;
  char* function=NULL;
  va_list args;
  va_start(args,factobj);

  /**
     Search for the function for which the wrapper has been created
     Python : WrapperArgsFactory.function
  */
  if(PyObject_HasAttrString(factobj,"function")){

    wrapperObj = PyObject_GetAttrString(factobj, "function");
    if(wrapperObj == NULL) {
      PyErr_SetString(PyExc_TypeError, "Error when calling PyObject_GetAttrString()");
      return 1;
    }

    function = PyUnicode_AsUTF8(wrapperObj);
    
    /**
       Function name found.
       It searches for a parser which can manage this format of wrapper
    */
    if(!strcmp(function,"_libScoreComputation.computeSimilarityMatrix")){
      /**
	 Function : computeSimilarityMatrix
	 Parse the wrapper given its format
      */
      parseLibscoreComputation(factobj,args);
    }
    else if(!strcmp(function,"_libNeedleman.alignMessages")){
      /**
	 Function : alignMessages
	 Parse the wrapper given its format
      */
      parseLibNeedleman(factobj,args);
    }

    else{
      PyErr_SetObject(PyExc_NameError, PyBytes_FromFormat("%s not yet implemented",function));
      return 1;
    }
    return 0;
  }
  else{
    PyErr_SetString(PyExc_TypeError, "Wrong argument type: must be a WrapperArgsFactory");
    return 2;
  }

}

void parseLibscoreComputation(PyObject* factobj, va_list args){
  unsigned int i;
  PyObject* pysize = NULL;
  unsigned int* nbmess = va_arg(args,unsigned int*);
  t_message** messages = va_arg(args,t_message**);
  unsigned int debugMode = FALSE;

  /**
     list : which is a list of messages
  */
  PyObject* list = PyObject_GetAttrString(factobj, "args");

  /**
     Find the number of elements in the list.
     This number of elements = number of messages (nbmess)
  */
  pysize = PyLong_FromSsize_t(PyList_Size(list));
  *nbmess = (unsigned int) PyLong_AsLong(pysize);
  Py_XDECREF(pysize);

  /**
     Reserves an array of [nbmess] t_messages
  */
  *messages = (t_message*) malloc((*nbmess)*sizeof(t_message));

  /**
     Parse each message and store them in the newly allocated array
  */
  for(i=0;i<*nbmess;i++){
    PyObject* item;
    item = PyList_GetItem(list,(Py_ssize_t)i);
    parseMessage(item, &((*messages)[i]));
  }

  // [DEBUG] Display the content of the deserialized messages
  if (debugMode == TRUE) {
    unsigned int iMessage;
    for(iMessage=0;iMessage<*nbmess;iMessage++) {
      t_message message = (*messages)[iMessage];
      printf("Message : %d (UID Symbol=%s)\n", iMessage, message.uid);
      printf("Data : ");
      for (i=0; i< message.len; i++) {
	printf("%02x", (unsigned char) message.alignment[i]);
      }
      printf("\n");
      printf("Tags : ");
      for (i=0; i< message.len; i++) {
	if (message.semanticTags != NULL && message.semanticTags[i] != NULL && message.semanticTags[i]->name != NULL && strcmp(message.semanticTags[i]->name, "None")!=0) {
	  printf("!!");
	} else {
	  printf("..");
	}
      }
      printf("\n");
    }
    // [DEBUG]
  }
}

void parseMessage(PyObject * item, t_message * message) {
  char * tmp_alignment;
  unsigned int j;
  /**
     message.alignment contains the message.getReducedStringData() in python raw format. Its the content of the message. If its during orphan reduction, this content is reduced to the considered section (sliding window).
  */
  tmp_alignment = PyBytes_AsString(PyObject_GetAttrString(item, "alignment"));
  message->alignment = (unsigned char*) tmp_alignment;

  /**
     message->mask will be allocated (no value in it yet) to contain at least ... ?
  */
  message->mask = calloc(strlen(tmp_alignment)+1,sizeof(unsigned char*));

  /**
     message->len contains the size of tmp_alignment
  **/
  message->len = (unsigned int) PyLong_AsUnsignedLong(PyObject_GetAttrString(item, "length"));

  /**
     message->semanticTags contains the list of tags attached to each half-byte of the alignment
  */
  message->semanticTags = calloc(message->len, sizeof(t_semanticTag *));

  // retrieve the list of tags
  PyObject* listOfSemanticTags = PyObject_GetAttrString(item, "semanticTags");

  // verify its a list
  if (PyList_CheckExact(listOfSemanticTags) && message->len == (unsigned int)PyList_Size(listOfSemanticTags)) {
    // every half-byte should be tagged (with no-tag or with a real tag)
    // parse all the tags
    for (j=0; j<message->len; j++) {
      PyObject * listItem = PyList_GetItem(listOfSemanticTags,(Py_ssize_t)j);
      char * tag = PyUnicode_AsUTF8(listItem);

      message->semanticTags[j] = malloc(sizeof(t_semanticTag));
      message->semanticTags[j]->name = tag;
    }
  } else {
    printf("[C-Extension] Error while parsing semantic tags.\n");
  }
  /**
     message->uid contains the UID of the symbol which contains
     the message.

     Warning: I though it was message's UID, but its not !!
  */
  message->uid = PyUnicode_AsUTF8(PyObject_GetAttrString(item, "uid"));

}


/**
   parseLibNeedlman:

   This function parses the arguments wrapper following a specific format.
   The definition of this format can be found in the Python function:
   netzob.Common.C_Extensions.WrapperArgsFactory:WrapperArgsFactory.computeSimilarityMatrix()
   Once parsed, the wrapper reveal arguments which will be stored in the args parameter.
   Format:
   - List<Message> with Message: (alignment, mask, length, uid)
*/
void parseLibNeedleman(PyObject* factobj, va_list args){

  PyObject* pysize = NULL;
  unsigned int* nbmess = va_arg(args,unsigned int*);
  t_message** messages = va_arg(args,t_message**);
  unsigned int debugMode = FALSE;
  unsigned int i;

  /**
     list : which is a list of messages
  */
  PyObject* list = PyObject_GetAttrString(factobj, "args");

  /**
     Find the number of elements in the list.
     This number of elements = number of messages (nbmess)
  */
  pysize = PyLong_FromSsize_t(PyList_Size(list));
  *nbmess = (unsigned int) PyLong_AsLong(pysize);
  Py_XDECREF(pysize);

  /**
     Reserves an array of [nbmess] t_messages
  */
  *messages = (t_message*) malloc((*nbmess)*sizeof(t_message));

  /**
     Parse each message and store them in the newly allocated array
  */
  for(i=0;i<*nbmess;i++){
    PyObject* item;
    item = PyList_GetItem(list,(Py_ssize_t)i);
    parseMessage(item, &((*messages)[i]));
  }

  // [DEBUG] Display the content of the deserialized messages
  if (debugMode == TRUE) {
    unsigned int iMessage;
    for(iMessage=0;iMessage<*nbmess;iMessage++) {
      printf("Message : %d\n", iMessage);
      printf("Data : ");
      t_message message = (*messages)[iMessage];

      for (i=0; i< message.len; i++) {
	printf("%02x", (unsigned char) message.alignment[i]);
      }
      printf("\n");
      printf("Tags : ");
      for (i=0; i< message.len; i++) {
	if (message.semanticTags != NULL && message.semanticTags[i] != NULL && message.semanticTags[i]->name != NULL && strcmp(message.semanticTags[i]->name, "None")!=0) {
	  printf("!!");
	} else {
	  printf("..");
	}
      }
      printf("\n");
    }
    // [DEBUG]
  }

}
