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
#include "factory.h"
#define tostring(s) PyString_FromString(s)
#define getstringattr(o,s) PyString_AsString(PyObject_GetAttr(o,tostring(s)))
#define getUnsignedLongAttribute(o,s) PyLong_AsUnsignedLong(PyObject_GetAttr(o,tostring(s)))

/*parseArgs return values:
*	0: Success
*	1: not yet implemented
*	2: not WrapperFactory
*/
int parseArgs(PyObject* factobj, ...){
  va_list args;
  va_start(args,factobj);

  /**
     Search for the function for which the wrapper has been created
     Python : WrapperArgsFactory.function
  */
  if(PyObject_HasAttrString(factobj,"function")){
    char* function=NULL;
    function =  getstringattr(factobj,"function");
    /**
       Function name found.
       It searches for a parser which can manage this format of wrapper
    */
    if(!strcmp(function,"_libScoreComputation.getHighestEquivalentGroup")){
      /**
	 Function : getHighestEquivalentGroup
	 Parse the wrapper given its format
      */
      parseLibscoreComputation(factobj,args);
    }
    else{
      PyErr_SetObject(PyExc_NameError, PyString_FromFormat("%s not yet implemented",function));
      return 1;
    }
    return 0;
  }
  else{
    PyErr_SetString(PyExc_TypeError, "Wrong argument type: must be a WrapperArgsFactory");
    return 2;
  }

}

/**
   parseLibscoreComputation:

   This function parses the arguments wrapper following a specific format.
   The definition of this format can be found in the Python function:
   netzob.Common.C_Extensions.WrapperArgsFactory:WrapperArgsFactory.getHighestEquivalentGroup()
   Once parsed, the wrapper reveal arguments which will be stored in the args parameter.
   Format:
   - List<Message> with Message: (alignment, mask, length, uid)
*/
void parseLibscoreComputation(PyObject* factobj, va_list args){
	long i;
	PyObject* pysize = NULL;
	long* nbmess = va_arg(args,long*);
	t_message** messages = va_arg(args,t_message**);
	char * tmp_alignment;
	/**
	   list : which is a list of messages
	*/
	PyObject* list = PyObject_GetAttr(factobj,PyString_FromString("args"));
	/**
	   Find the number of elements in the list.
	   This number of elements = number of messages (nbmess)
	*/
	pysize = PyLong_FromSsize_t(PyList_Size(list));
	*nbmess = PyLong_AsLong(pysize);
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
		/**
		   message.alignment contains the message.getReducedStringData() in python raw format. Its the content of the message. If its during orphan reduction, this content is reduced to the considered section (sliding window).
		 */
		tmp_alignment = getstringattr(item,"alignment");
		(*messages)[i].alignment = (unsigned char*) tmp_alignment;

		/**
		   message.mask will be allocated (no value in it yet) to contain at least ... ?
		 */
		(*messages)[i].mask = calloc(strlen(tmp_alignment)+1,sizeof(unsigned char*));
		/**
		   message.len contains the size of tmp_alignment
		**/
		(*messages)[i].len = (unsigned int) getUnsignedLongAttribute(item,"length");
		/**
		   message.uid contains the UID of the symbol which contains
		   the message.

		   Warning: I though it was message's UID, but its not !!
		*/
		(*messages)[i].uid = getstringattr(item,"uid");
	}

}
#undef getstringattr
#undef tostring
