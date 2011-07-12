// Compilation : gcc -fPIC -shared -I/usr/include/python2.6 -lpython2.6 -o libNeedleman.so NeedlemanWunsch.c

#include <Python.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

typedef enum
  {
    FALSE,
    TRUE
  } BOOL;

typedef struct
{
  unsigned short int len; // length of the message
  char *message; // a message
} t_message;

typedef struct
{
  unsigned short int len; // nb of messages in the group
  t_message *messages; // a list of messages
} t_group;

typedef struct
{
  unsigned short int len; // size of the regex
  char *regex; // the actual regex
  char *mask; // its mask
  float score;
} t_regex;

void alignTwoSequences(t_regex seq1, t_regex seq2, t_regex regex);
int hexdump(unsigned char *buf, int dlen);

static PyObject* py_getMatrix(PyObject* self, PyObject* args)
{
  char *serialGroups;
  char *format;
  char *tmp;
  char *tmp2;
  char *tmp3;
  char *p;
  unsigned short int nbGroups;
  unsigned short int nbMessages;
  unsigned short int sizeMessage;
  unsigned short int i, j, k, l;
  unsigned short int len;
  int sizeMessages;
  t_group   *t_groups;
  // TODO: (fgy) do not forget the freeing of these tables of pointers

  if (!PyArg_ParseTuple(args, "hss#", &nbGroups, &format, &serialGroups, &sizeMessages))
    return NULL;

  // Allocate nbGroups pointers
  t_groups = malloc( nbGroups * sizeof(t_group) );

  // Deserialize the groups of messages
  for(i = 0, k = 0, l = 0; i < nbGroups; ++i) {
    // Retrieve the nb of messages for the current group
    p = strchr( format + k,  'G');
    len = (unsigned short int) (p - (format + k));
    tmp = malloc( (len + 1) * sizeof(char) );
    memcpy(tmp, format + k, len);
    tmp[len] = '\0';
    nbMessages = atoi( tmp );
    k += len + 1;

    // Allocate nbMessages pointers
    t_groups[i].len = nbMessages;
    t_groups[i].messages = malloc( nbMessages * sizeof(t_message) );

    for(j = 0; j < nbMessages; ++j) {
      // Retrieve the size of each message
      p = strchr(format + k,  'M');
      len = (unsigned short int) (p - (format + k));
      tmp2 = malloc( (len + 1) * sizeof(char) );
      memcpy(tmp2, format + k, len);
      tmp2[len] = '\0';
      sizeMessage = atoi( tmp2 );
      k += len + 1;

      // Retrieve the data of each message
      tmp3 = malloc( sizeMessage * sizeof(char) );
      // TODO: (fgy) do not forget the freeing of this string
      memcpy(tmp3, serialGroups + l, sizeMessage);
      t_groups[i].messages[j].len = sizeMessage;
      t_groups[i].messages[j].message = tmp3;
      l += sizeMessage;
      free(tmp2);
    }
    free(tmp);
  }

  // Compute the matrix
  float matrix[nbGroups][nbGroups];
  t_group p_group;
  t_regex regex;
  t_regex regex1;
  t_regex regex2;
  short int nb_msg_group;
  for( i = 0; i < nbGroups; ++i) {
    for( j = 0; j < nbGroups; ++j) {
      if( i == j )
	matrix[i][j] = 100;
      else if( i < j ) {
	p_group.len = t_groups[i].len + t_groups[j].len;
	p_group.messages = malloc( p_group.len * sizeof(t_message) );
	for(k = 0; k < t_groups[i].len; ++k) {
	  p_group.messages[k] = t_groups[i].messages[k];
	}
	for(k = k, l = 0; l < t_groups[j].len; ++k, ++l) {
	  p_group.messages[k] = t_groups[j].messages[l];
	}

	// Align the messages of the current group
	regex1.len = p_group.messages[0].len;
	regex1.regex = p_group.messages[0].message;
	regex1.mask = malloc( p_group.messages[0].len * sizeof(char) );
	memset( regex1.mask, 2, p_group.messages[0].len );
	
	for(k = 1; k < p_group.len; ++k) {
	  regex2.len = p_group.messages[k].len;
	  regex2.regex = p_group.messages[k].message;
	  regex2.mask = malloc( p_group.messages[k].len * sizeof(char) );
	  memset( regex2.mask, 2, p_group.messages[k].len );

	  regex.len = regex1.len + regex2.len;
	  regex.regex = malloc(regex.len * sizeof(char));
	  regex.mask = malloc(regex.len * sizeof(char));
	  memset(regex.regex, 0, regex.len * sizeof(char));
	  memset(regex.mask, 2, regex.len * sizeof(char));

	  alignTwoSequences(regex1, regex2, regex);

	  hexdump(regex.regex, regex.len);
	  hexdump(regex.mask, regex.len);
	  printf("score: %f\n", regex.score);
	  free(regex1.mask);
	  free(regex2.mask);
	  regex1.len = regex.len;
	  regex1.mask = regex.mask;
	  regex1.regex = regex.regex;
	}
	matrix[i][j] = regex.score;
	matrix[j][i] = regex.score;
      }
    }
  }

  for( i = 0; i < nbGroups; ++i) {
    for( j = 0; j < nbGroups; ++j)
      printf( " %f ", matrix[j][i] );
    printf("\n");
  }
  
  return Py_None;
  //Py_BuildValue("i", sts); // return the matrice and the regex...
}

/*
 * Bind Python function names to our C functions
 */
static PyMethodDef libNeedleman_methods[] = {
	{"getMatrix", py_getMatrix, METH_VARARGS},
	{NULL, NULL}
};

void initlibNeedleman() {
  (void) Py_InitModule("libNeedleman", libNeedleman_methods);
}

void alignTwoSequences(t_regex seq1, t_regex seq2, t_regex regex) {
  const short int match = 10;
  const short int mismatch = -10;
  const short int gap = 0;

  // initiliaze the matrix with 0
  short int matrix[seq1.len + 1][seq2.len + 1];
  unsigned short int i = 0;
  unsigned short int j = 0;
  memset(matrix, 0, sizeof(short int) * (seq1.len + 1) * (seq2.len + 1)); // TODO: not necessary => only fill first col and first row

  // fill the matrix
  short int elt1, elt2, elt3, max, eltL, eltD, eltT;
  BOOL finish;
  for(i = 1; i < (seq1.len + 1) ; i++) {
    for(j = 1; j < (seq2.len + 1) ; j++) {
      /*
	# Matrix[i][j] = MAXIMUM (
	# elt1 :         Matrix[i-1][j-1] + match/mismatch(Matrix[i][j]),
	# elt2 :         Matrix[i][j-1]   + gap,
	# elt3 :         Matrix[i-1][j]   + gap)
      */
      elt1 = matrix[i - 1][j - 1];
      if((seq1.mask[i - 1] != 1) && (seq2.mask[j - 1] != 1) && (seq1.regex[i - 1] == seq2.regex[j - 1]))
	elt1 += match;
      else
	elt1 += mismatch;
      elt2 = matrix[i][j - 1] + gap;
      elt3 = matrix[i - 1][j] + gap;

      max = elt1 > elt2 ? elt1 : elt2;
      max = max > elt3 ? max : elt3;
      matrix[i][j] = max;
    }
  }
   
  // Traceback
  finish = FALSE;
  unsigned char *regex1 = malloc((seq1.len + seq2.len) * sizeof(unsigned char));
  unsigned char *regex2 = malloc((seq1.len + seq2.len) * sizeof(unsigned char));
  unsigned char *regex1Mask = malloc((seq1.len + seq2.len) * sizeof(unsigned char));
  unsigned char *regex2Mask = malloc((seq1.len + seq2.len) * sizeof(unsigned char));
  // TODO: (fgy) handle errors on malloc operation
  memset(regex1, 0x00, (seq1.len + seq2.len) * sizeof(unsigned char));
  memset(regex2, 0x00, (seq1.len + seq2.len) * sizeof(unsigned char));
  memset(regex1Mask, 2, (seq1.len + seq2.len) * sizeof(unsigned char));
  memset(regex2Mask, 2, (seq1.len + seq2.len) * sizeof(unsigned char));
  unsigned short int iReg1 = seq1.len + seq2.len - 1;
  unsigned short int iReg2 = seq1.len + seq2.len - 1;

  i = seq1.len;
  j = seq2.len;
  while( finish != TRUE ) {
    eltL = matrix[i][j - 1];
    eltD = matrix[i - 1][j - 1];
    eltT = matrix[i - 1][j];

    if ((eltL > eltD) && (eltL > eltT)) {
      --j;
      regex1[iReg1] = 0xff;
      regex1Mask[iReg1] = 1;
      regex2[iReg2] = seq2.regex[j];
      --iReg1;
      --iReg2;
     }
    else if ((eltT >= eltL) && (eltT > eltD)){
      --i;
      regex2[iReg2] = 0xff;
      regex2Mask[iReg2] = 1;
      regex1[iReg1] = seq1.regex[i];
      --iReg1;
      --iReg2;
    }
    else{
      --i;
      --j;
      regex1[iReg1] = seq1.regex[i];
      regex2[iReg2] = seq2.regex[j];
      regex1Mask[iReg1] = 0;
      regex2Mask[iReg2] = 0;
      --iReg1;
      --iReg2;
    }
         
    if (i == 0 || j == 0)
      finish = TRUE;
  }

  // Compute the common regex
  unsigned short int iReg = seq1.len + seq2.len - 1;
  i = seq1.len + seq2.len - 1;
  while ( i > 0 ) {
    if( (regex1Mask[i] == 2) && (regex2Mask[i] == 2)) {
      regex.regex[iReg] = 0xff;
      regex.mask[iReg] = 2;
      --iReg;
    }
    else if( (regex1Mask[i] == 1) || (regex2Mask[i] == 1) || (regex1[i] != regex2[i]) ) {
      regex.regex[iReg] = 0xff;
      regex.mask[iReg] = 1;
      --iReg;
    }
    else {
      regex.regex[iReg] = regex1[i];
      regex.mask[iReg] = 0;
      --iReg;
    }
    --i;
  }

  // Compute the score of the regex
  float nbDynamic = 0.0f;
  float nbStatic = 0.0f;
  float cent = 100.0f;
  BOOL inDyn = FALSE;
  for(i = 0; i < regex.len; ++i) {
    if(regex.mask[i] == 0) {
      if(inDyn == TRUE) {
	nbDynamic = nbDynamic + 1.0f;
	inDyn = FALSE;
      }
      nbStatic = nbStatic + 1.0f;
    }
    else if(regex.mask[i] == 1)
      inDyn = TRUE;
  }
  if(inDyn == TRUE)
    nbDynamic = nbDynamic + 1.0f;
  regex.score = (float) ((float)(((float)cent) / (((float)nbStatic) + ((float)nbDynamic))) * ((float)nbStatic));
  printf("Ouinnnnnnnnnnnnnnnnnnnnnh... \n");

  // Room service
  free( regex1 );
  free( regex2 );
  free( regex1Mask );
  free( regex2Mask );
  // TODO: (fgy) avoid double freeing
}

int hexdump(unsigned char *buf, int dlen) {
  int OPL = 32;
  char	c[OPL+1];
  int	i, ct;

  if (dlen < 0) {
    printf("WARNING: computed dlen %d\n", dlen);
    dlen = 0;
  }
  for (i=0; i<dlen; ++i) {
    if (i == 0)
      printf("DATA: ", c);
    else if ((i % OPL) == 0) {
      c[OPL] = '\0';
      printf("\t\"%s\"\nDATA: ", c);
    }
    ct = buf[i] & 0xff;
    c[i % OPL] = (ct >= ' ' && ct <= '~') ? ct : '.';
    printf("%02x ", ct);
  }
  c[i%OPL] = '\0';
  for (; i % OPL; ++i)
    printf("   ");
  printf("\t\"%s\"\n", c);
}
