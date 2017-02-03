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
//cl -Fe_libInterface.pyd -Ox -Ot -openmp -LD /I"C:\Python26\include" /I"C:\Program Files (x86)\Microsoft Visual Studio 9.0\VC\include" libInterface.c "C:\Python26\libs\python26.lib" "C:\Program Files (x86)\Microsoft Visual Studio 9.0\VC\lib\vcomp.lib"

//+---------------------------------------------------------------------------+
//| Import Associated Header
//+---------------------------------------------------------------------------+
#include "Interface.h"
#ifdef _WIN32
#include <stdio.h>
#include <malloc.h>
#endif

#ifdef CCALLFORDEBUG
//+---------------------------------------------------------------------------+
//| callbackStatus : displays the status on terminal when using only C calls
//+---------------------------------------------------------------------------+
int callbackStatus(int stage, double percent, char* message, ...) {
  // Variadic member
  va_list args;

  // local variables
  char buffer[4096];

  va_start(args, message);
  vsnprintf(buffer, sizeof(buffer), message, args);
  va_end(args);
  buffer[4095] = '\0';

  printf("[%d, %f] %s\n", stage, percent, buffer);
  return 1;

}
#endif


//+---------------------------------------------------------------------------+
//| deserializeMessages : Deserialization of messages
//+---------------------------------------------------------------------------+
unsigned int deserializeMessages(t_group * group, char *format, unsigned char *serialMessages, unsigned int nbMessages, Bool debugMode) {
  unsigned int i_message = 0;
  char * p;
  unsigned int serial_shift = 0;
  unsigned int format_shift = 0;
  unsigned int len_size_message=0;
  unsigned int size_message=0;
  char * size_message_str;
  unsigned int nbDeserializedMessages = 0;

  for (i_message=0; i_message < nbMessages; i_message++) {
    // Retrieve the size of each message
    p = strchr(format + format_shift, 'M');
    len_size_message = (unsigned int) (p - (format + format_shift));
    size_message_str = malloc((len_size_message + 1) * sizeof(char));
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
      printf("Message %u : \n", i_message);
      hexdump(group->messages[i_message].alignment, group->messages[i_message].len);
    }
  }
  return nbDeserializedMessages;
}

unsigned int deserializeGroups(t_groups * groups, char * format, unsigned char * serialGroups, int nbGroups, Bool debugMode) {
  int i_group = 0;
  int j_group = 0;
  int l = 0;
  char * p;
  char *q;
  char *r;
  char *s;
  unsigned short int format_shift = 0;
  unsigned int len_size_group = 0;
  unsigned int len_size_message = 0;
  unsigned int len_score_group = 0;
  unsigned int size_group = 0;
  unsigned int size_message = 0;
  char * size_group_str;
  char * size_message_str;
  char * score_group;
  unsigned int i_message = 0;

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
    size_group_str = malloc((len_size_group + 1) * sizeof(char));
    memcpy(size_group_str, format + format_shift, len_size_group);
    size_group_str[len_size_group] = '\0';
    size_group = (unsigned int) atoi(size_group_str);
    format_shift += len_size_group + 1;

    // Allocate pointers to store the messages of current group
    groups->groups[i_group].len = size_group;
    groups->groups[i_group].messages = malloc(size_group * sizeof(t_message));

    for (i_message = 0; i_message < size_group; i_message++) {
      // Retrieve the size of each message
      q = strchr(format + format_shift, 'M');
      len_size_message = (unsigned int) (q - (format + format_shift));
      size_message_str = malloc((len_size_message + 1) * sizeof(char));
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
  if (debugMode == TRUE) {
    printf("A number of %d group has been deserialized.\n", nbGroups);
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
  unsigned int i;
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

unsigned int serializeSemanticTags(char ** serializedTags, t_semanticTag ** tags, unsigned int nbSemanticTags) {
  unsigned int sizeSerializedTags = 0;
  unsigned int iTag = 0;
  unsigned int sizeLocalTag = 0;
  // serializedTags = "tag1;tag2;tag3;..."
  // first we compute the size of the result:
  // size(serializedTags) = sum(size(tags->name)+1)+1

  for (iTag=0; iTag<nbSemanticTags; iTag++){
    if(tags[iTag]->name != NULL) {
      sizeSerializedTags += strlen(tags[iTag]->name);
    }
    sizeSerializedTags +=1;
  }
  sizeSerializedTags +=1; // for the NULL byte
  *serializedTags = calloc(sizeSerializedTags, sizeof(char));
  for (iTag=0; iTag<nbSemanticTags; iTag++) {
    if (tags[iTag]->name != NULL) {
      sizeLocalTag = strlen(tags[iTag]->name);
      if(sizeLocalTag>0){
	strncat(*serializedTags, tags[iTag]->name, sizeLocalTag);
      }
    }
    strncat(*serializedTags, ";", 1);
  }
  return sizeSerializedTags;
}

PyObject * serializeMessage(t_message * message) {
  char * semanticTags = NULL;
  unsigned int lenSemanticTags = serializeSemanticTags(&semanticTags, message->semanticTags, message->len);
  return Py_BuildValue("(fffy#y#s#)", message->score->s1, message->score->s2, message->score->s3, message->alignment, message->len, message->mask, message->len, semanticTags, lenSemanticTags);

}
