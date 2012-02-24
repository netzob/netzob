// -*- coding: utf-8 -*-

/*
 +---------------------------------------------------------------------------+
 |         01001110 01100101 01110100 01111010 01101111 01100010             | 
 +---------------------------------------------------------------------------+
 | NETwork protocol modeliZatiOn By reverse engineering                      |
 | ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~+
 | @license      : GNU GPL v3                                                |
 | @copyright    : Georges Bossert and Frederic Guihery                      |
 | @url          : http://code.google.com/p/netzob/                          |
 | ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~+
 | @author       : {gbt,fgy}@amossys.fr                                      |
 | @organization : Amossys, http://www.amossys.fr                            |
 +---------------------------------------------------------------------------+
*/

// Compilation : gcc -fPIC -O3 -fopenmp -shared -I/usr/include/python2.6 -lpython2.6 -o libNeedleman.so NeedlemanWunsch.c

#include "headers/NeedlemanWunsch.h"

static PyObject* py_getMatrix(PyObject* self, PyObject* args) {
	unsigned char *serialGroups;
	unsigned char *format;
	unsigned char *tmp;
	unsigned char *tmp2;
	unsigned char *p;
	unsigned short int nbGroups;
	unsigned short int doInternalSlick;
	unsigned short int nbMessages;
	unsigned short int sizeMessage;
	int i, j, k, l;
	unsigned short int len;
	int sizeSerialGroups;
	t_group *t_groups;

	if (!PyArg_ParseTuple(args, "hhss#", &doInternalSlick, &nbGroups, &format, &serialGroups,
			&sizeSerialGroups))
		return NULL;

	// Allocate nbGroups pointers
	t_groups = malloc(nbGroups * sizeof(t_group));

	// Deserialize the groups of messages
	for (i = 0, k = 0, l = 0; i < nbGroups; ++i) {
		// Retrieve the nb of messages for the current group
		p = strchr(format + k, 'G');
		len = (unsigned short int) (p - (format + k));
		tmp = malloc((len + 1) * sizeof(unsigned char));
		memcpy(tmp, format + k, len);
		tmp[len] = '\0';
		nbMessages = atoi(tmp);
		k += len + 1;

		// Allocate nbMessages pointers
		t_groups[i].len = nbMessages;
		t_groups[i].messages = malloc(nbMessages * sizeof(t_message));

		for (j = 0; j < nbMessages; ++j) {
			// Retrieve the size of each message
			p = strchr(format + k, 'M');
			len = (unsigned short int) (p - (format + k));
			tmp2 = malloc((len + 1) * sizeof(unsigned char));
			memcpy(tmp2, format + k, len);
			tmp2[len] = '\0';
			sizeMessage = atoi(tmp2);
			k += len + 1;

			// Retrieve the data of each message
			t_groups[i].messages[j].len = sizeMessage;
			t_groups[i].messages[j].message = serialGroups + l;
			t_groups[i].messages[j].mask = serialGroups + l + sizeMessage;
			l += sizeMessage * 2;
			free( tmp2 );
		}
		free( tmp );
	}

	// Compute the matrix
	float **matrix;
	float maxScore = -1.0f;
	short int i_maximum = -1;
	short int j_maximum = -1;

	matrix = (float **) malloc( nbGroups * sizeof(float*) );
	for (i = 0; i < nbGroups; i++) {
	  matrix[i] = (float *) malloc( sizeof(float) * nbGroups );
	  for(j = 0; j < nbGroups; j++)
	    {
	      matrix[i][j] = 0.0;
	    }
	}

	//	omp_lock_t my_lock;
	//	omp_set_num_threads(8);
	//	omp_init_lock(&my_lock);

#pragma omp parallel for shared(t_groups, nbGroups, matrix)
	for (i = 0; i < nbGroups; i++) {
	  int p = 0;
	  for (p = 0; p < nbGroups; p++) {
		  if (i < p) {
		                int m, n;
				t_group p_group;
				t_regex regex;
				t_regex regex1;
				t_regex regex2;
				p_group.len = t_groups[i].len + t_groups[p].len;
				p_group.messages = malloc(p_group.len * sizeof(t_message));
				for (m = 0; m < t_groups[i].len; ++m) {
				  p_group.messages[m] = t_groups[i].messages[m];
				}
				for (m = m, n = 0; n < t_groups[p].len; ++m, ++n) {
					p_group.messages[m] = t_groups[p].messages[n];
				}

				// Align the messages of the current group
				regex1.len = p_group.messages[0].len;
				regex1.regex = p_group.messages[0].message;
				regex1.mask = p_group.messages[0].mask;

				for (m = 1; m < p_group.len; ++m) {
					regex2.len = p_group.messages[m].len;
					regex2.regex = p_group.messages[m].message;
					regex2.mask = p_group.messages[m].mask;

					alignTwoSequences(doInternalSlick, regex1, regex2, &regex);

					regex1.len = regex.len;
					regex1.mask = regex.mask;
					regex1.regex = regex.regex;
				}
				//				omp_set_lock(&my_lock);
				matrix[i][p] = regex.score;
				//				omp_unset_lock(&my_lock);

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
	for (i = 0; i < nbGroups; i++)
	  free( matrix[i] );
	free( matrix );
	
	for (i = 0; i < nbGroups; ++i) {
	  free( t_groups[i].messages );
	}
	free( t_groups );
	
	return Py_BuildValue("(iif)", i_maximum, j_maximum, maxScore);
}

static PyObject* py_alignSequences(PyObject* self, PyObject* args) {
	unsigned char *serialMessages;
	unsigned char *format;
	unsigned char *tmp2;
	unsigned char *p;
	unsigned short int nbMessages;
	unsigned short int doInternalSlick;
	unsigned short int sizeMessage;
	unsigned short int i, j, k, l;
	unsigned short int len;
	int sizeSerialMessages;
	t_group p_group;
	t_regex regex;
	t_regex regex1;
	t_regex regex2;

	if (!PyArg_ParseTuple(args, "hhss#", &doInternalSlick, &nbMessages, &format, &serialMessages,
			&sizeSerialMessages))
		return NULL;

	// Allocate nbMessages pointers
	p_group.len = nbMessages;
	p_group.messages = malloc(nbMessages * sizeof(t_message));

	// Deserialize the input messages
	for (k = 0, l = 0, j = 0; j < nbMessages; ++j) {
	  // Retrieve the size of each message
	  p = strchr(format + k, 'M');
	  len = (unsigned short int) (p - (format + k));
	  tmp2 = malloc((len + 1) * sizeof(unsigned char));
	  memcpy(tmp2, format + k, len);
	  tmp2[len] = '\0';
	  sizeMessage = atoi(tmp2);
	  k += len + 1;

	  // Retrieve the data of each message
	  p_group.messages[j].len = sizeMessage;
	  p_group.messages[j].message = serialMessages + l;
	  l += sizeMessage;
	  free( tmp2 );
	}

	// Align the messages
	regex1.len = p_group.messages[0].len;
	regex1.regex = p_group.messages[0].message;
	regex1.mask = malloc(p_group.messages[0].len * sizeof(unsigned char));
	memset(regex1.mask, 0, p_group.messages[0].len);

	// Only usefull in case of nbMessages == 1
	regex.len = regex1.len;
	regex.mask = regex1.mask;
	regex.regex = regex1.regex;
	regex.score = 0.0;

	for (k = 1; k < p_group.len; ++k) {
	  regex2.len = p_group.messages[k].len;
	  regex2.regex = p_group.messages[k].message;
	  regex2.mask = malloc(p_group.messages[k].len * sizeof(unsigned char));
	  memset(regex2.mask, 0, p_group.messages[k].len);
	    
	  alignTwoSequences(doInternalSlick, regex1, regex2, &regex);
	  
	  free(regex1.mask);
	  free(regex2.mask);
	  regex1.len = regex.len;
	  regex1.mask = regex.mask;
	  regex1.regex = regex.regex;
	}

	// Room service
	//	free( regex.regex );
	//	free( regex.mask );
	free( p_group.messages );

	return Py_BuildValue("(fs#s#)", regex.score, regex.regex, regex.len, regex.mask, regex.len);
}

void initlibNeedleman() {
	(void) Py_InitModule("libNeedleman", libNeedleman_methods);
}

void alignTwoSequences(unsigned short int doInternalSlick, t_regex seq1, t_regex seq2, t_regex *regex) {
	const short int match = 10;
	const short int mismatch = -10;
	const short int gap = 0;

	//	dumpRegex(seq1);
	//	dumpRegex(seq2);

	// initiliaze the matrix with 0
	short int **matrix;
	unsigned short int i = 0;
	unsigned short int j = 0;

	matrix = (short int**) malloc( sizeof(short int*) * (seq1.len + 1) );
	for (i = 0; i < (seq1.len + 1); i++) {
	  matrix[i] = (short int*) calloc( (seq2.len + 1), sizeof(short int) );
	}

	// fill the matrix
	short int elt1, elt2, elt3, max, eltL, eltD, eltT;
	BOOL finish;

	for (i = 1; i < (seq1.len + 1); i++) {
		for (j = 1; j < (seq2.len + 1); j++) {
			/*
			 # Matrix[i][j] = MAXIMUM (
			 # elt1 :         Matrix[i-1][j-1] + match/mismatch(Matrix[i][j]),
			 # elt2 :         Matrix[i][j-1]   + gap,
			 # elt3 :         Matrix[i-1][j]   + gap)
			 */
		        elt1 = matrix[i - 1][j - 1];
			if ( (seq1.mask[i - 1] == 0) && (seq2.mask[j - 1] == 0)
			     && (seq1.regex[i - 1] == seq2.regex[j - 1]))
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
	unsigned char *regex1 = calloc( seq1.len + seq2.len, sizeof(unsigned char));
	unsigned char *regex2 = calloc( seq1.len + seq2.len, sizeof(unsigned char));
	unsigned char *regex1Mask = malloc( (seq1.len + seq2.len) * sizeof(unsigned char));
	unsigned char *regex2Mask = malloc( (seq1.len + seq2.len) * sizeof(unsigned char));
	// TODO: (fgy) handle errors on malloc operation
	memset(regex1Mask, 2, (seq1.len + seq2.len) * sizeof(unsigned char));
	memset(regex2Mask, 2, (seq1.len + seq2.len) * sizeof(unsigned char));
	unsigned short int iReg1 = seq1.len + seq2.len - 1;
	unsigned short int iReg2 = seq1.len + seq2.len - 1;

	i = seq1.len;
	j = seq2.len;
	while ((i > 0) && (j > 0)) {
		eltL = matrix[i][j - 1];
		eltD = matrix[i - 1][j - 1];
		eltT = matrix[i - 1][j];

		if ((eltL > eltD) && (eltL > eltT)) {
			--j;
			regex1[iReg1] = 0xf1;
			regex1Mask[iReg1] = 1;
			if( seq2.mask[j] == 0) {
			  regex2[iReg2] = seq2.regex[j];
			  regex2Mask[iReg2] = 0;
			}
			else {
			  regex2[iReg2] = 0xf1;
			  regex2Mask[iReg2] = 1;
			}
		} else if ((eltT >= eltL) && (eltT > eltD)) {
			--i;
			regex2[iReg2] = 0xf2;
			regex2Mask[iReg2] = 1;
			if( seq1.mask[i] == 0) {
			  regex1[iReg1] = seq1.regex[i];
			  regex1Mask[iReg1] = 0;
			}
			else {
			  regex1[iReg1] = 0xf2;
			  regex1Mask[iReg1] = 1;
			}
		} else {
			--i;
			--j;
			if( seq1.mask[i] == 0) {
			  regex1[iReg1] = seq1.regex[i];
			  regex1Mask[iReg1] = 0;
			}
			else {
			  regex1[iReg1] = 0xf2;
			  regex1Mask[iReg1] = 1;
			}

			if( seq2.mask[j] == 0) {
			  regex2[iReg2] = seq2.regex[j];
			  regex2Mask[iReg2] = 0;
			}
			else {
			  regex2[iReg2] = 0xf2;
			  regex2Mask[iReg2] = 1;
			}
		}
		--iReg1;
		--iReg2;
	}
	while (i > 0) {
	  --i;
	  regex2[iReg2] = 0xf3;
	  regex2Mask[iReg2] = 1;

	  if( seq1.mask[i] == 0) {
	    regex1[iReg1] = seq1.regex[i];
	    regex1Mask[iReg1] = 0;
	  }
	  else {
	    regex1[iReg1] = 0xf3;
	    regex1Mask[iReg1] = 1;
	  }
	  --iReg1;
	  --iReg2;
	}
	while (j > 0) {
	  --j;
	  regex1[iReg1] = 0xf4;
	  regex1Mask[iReg1] = 1;

	  if( seq2.mask[j] == 0) {
	    regex2[iReg2] = seq2.regex[j];
	    regex2Mask[iReg2] = 0;
	  }
	  else {
	    regex2[iReg2] = 0xf4;
	    regex2Mask[iReg2] = 1;
	  }

	  --iReg1;
	  --iReg2;
	}

	/*	 // For debug only
	for( i = 0; i < seq1.len + seq2.len; i++)
	  if( regex1Mask[i] == 0 )
	    printf("%02x", (unsigned char) regex1[i]);
	  else if ( regex1Mask[i] == 2 )
	    printf("##");
	  else
	    printf("--");
	printf("\n");
	for( i = 0; i < seq1.len + seq2.len; i++)
	  if( regex2Mask[i] == 0 )
	    printf("%02x", (unsigned char) regex2[i]);
	  else if ( regex2Mask[i] == 2 )
	    printf("##");
	  else
	    printf("--");
	printf("\n");
	*/

	// Compute the common regex
	unsigned char *regexTmp = calloc( seq1.len + seq2.len, sizeof(unsigned char));
	unsigned char *regexMaskTmp = malloc( (seq1.len + seq2.len) * sizeof(unsigned char));
	memset(regexMaskTmp, 2, (seq1.len + seq2.len) * sizeof(unsigned char));
	i = seq1.len + seq2.len;
	while (i > 0) {
	  --i;
	  if ((regex1Mask[i] == 2) || (regex2Mask[i] == 2)) {
	    regexTmp[i] = 0xf9;
	    regexMaskTmp[i] = 2;
	  }
	  else if ((regex1Mask[i] == 0) && (regex2Mask[i] == 0) && (regex1[i] == regex2[i])) {
	    regexTmp[i] = regex1[i];
	    regexMaskTmp[i] = 0;
	  }
	  else {
	    regexTmp[i] = 0xf5;
	    regexMaskTmp[i] = 1;
	  }
	}

	// Compute the score of the regex
	float nbDynamic = 0.0f;
	float nbStatic = 0.0f;
	float cent = 100.0f;
	BOOL inDyn = FALSE;
	for (i = (seq1.len + seq2.len - 1); i >= 1; --i) {
	  if (regexMaskTmp[i] == 2) {
	    break;
	  } else if (regexMaskTmp[i] == 0) {
	    if (inDyn == TRUE) {
	      nbDynamic = nbDynamic + 1.0f;
	      inDyn = FALSE;
	    }
	    nbStatic = nbStatic + 1.0f;
	  } else if (regexMaskTmp[i] == 1)
	    inDyn = TRUE;
	}
	if (inDyn == TRUE)
	  nbDynamic = nbDynamic + 1.0f;

	// Retrieve the shortest possible regex
	regex->score = 100.0 / (nbStatic + nbDynamic) * nbStatic;
	i = 0;
	while( regexMaskTmp[i] == 2 )
	  i++;
	regex->len = seq1.len + seq2.len - i;
	regex->regex = malloc(regex->len * sizeof(unsigned char));
	regex->mask = malloc(regex->len * sizeof(unsigned char));
	// TODO: (fgy) free regex.mask and regex.regex
	memcpy(regex->regex, regexTmp + i, regex->len);
	memcpy(regex->mask, regexMaskTmp + i, regex->len);

	// Try to slick the regex
	if(doInternalSlick == 1)
	  for(i = 1; i < regex->len - 1; i++)
	    if( regex->mask[i] == 0 )
	      if( regex->mask[i - 1] == 1 )
		if( regex->mask[i + 1] == 1 ) {
		  regex->regex[i] = 0xf6;
		  regex->mask[i] = 1;
		}

	
	//	dumpRegex(*regex);
	//	printf("\n");
	

	// Room service
	for (i = 0; i < (seq1.len + 1); i++) {
	  free( matrix[i] );
	}
	free( matrix );

	free(regex1);
	free(regex2);
	free(regex1Mask);
	free(regex2Mask);
	free(regexTmp);
	free(regexMaskTmp);
}

int hexdump(unsigned char *buf, int dlen) {
	int OPL = 64;
	char c[OPL + 1];int
	i, ct;

	if (dlen < 0) {
		printf("WARNING: computed dlen %d\n", dlen);
		dlen = 0;
	}
	for (i = 0; i < dlen; ++i) {
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
