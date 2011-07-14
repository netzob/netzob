// Compilation : gcc -fPIC -fopenmp -shared -I/usr/include/python2.6 -lpython2.6 -o libNeedleman.so NeedlemanWunsch.c

#include "headers/NeedlemanWunsch.h"

static PyObject* py_getMatrix(PyObject* self, PyObject* args) {
	char *serialGroups;
	char *format;
	char *tmp;
	char *tmp2;
	char *p;
	unsigned short int nbGroups;
	unsigned short int nbMessages;
	unsigned short int sizeMessage;
	unsigned short int i, j, k, l;
	unsigned short int len;
	int sizeMessages;
	t_group *t_groups;

	// TODO: (fgy) do not forget the freeing of these tables of pointers

	if (!PyArg_ParseTuple(args, "hss#", &nbGroups, &format, &serialGroups,
			&sizeMessages))
		return NULL;

	// Allocate nbGroups pointers
	t_groups = malloc(nbGroups * sizeof(t_group));

	// Deserialize the groups of messages
	for (i = 0, k = 0, l = 0; i < nbGroups; ++i) {
		// Retrieve the nb of messages for the current group
		p = strchr(format + k, 'G');
		len = (unsigned short int) (p - (format + k));
		tmp = malloc((len + 1) * sizeof(char));
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
			tmp2 = malloc((len + 1) * sizeof(char));
			memcpy(tmp2, format + k, len);
			tmp2[len] = '\0';
			sizeMessage = atoi(tmp2);
			k += len + 1;

			// Retrieve the data of each message
			t_groups[i].messages[j].message = malloc(sizeMessage * sizeof(char));			
			// TODO: (fgy) do not forget the freeing of this string
			memcpy(t_groups[i].messages[j].message, serialGroups + l, sizeMessage);
			t_groups[i].messages[j].len = sizeMessage;
			l += sizeMessage;
			free( tmp2 );
		}
		free( tmp );
	}

	// Compute the matrix
	float **matrix;
	float maxScore = -1.0f;
	short int i_maximum = -1;
	short int j_maximum = -1;
	short int nb_msg_group;

	matrix = (float **) malloc( nbGroups * sizeof(float*) );
	for (i = 0; i < nbGroups; i++) {
	  matrix[i] = (float *) malloc( sizeof(float) * nbGroups );
	  for(j = 0; j < nbGroups; j++)
	    {
	      matrix[i][j] = 0.0;
	    }
	}

	#pragma omp parallel for shared(matrix, t_groups)
	for (i = 0; i < nbGroups; ++i) {
		for (j = 0; j < nbGroups; ++j) {
			if (i == j)
			  matrix[i][j] = 100.0;
			else if (i < j) {
				t_group p_group;
				t_regex regex;
				t_regex regex1;
				t_regex regex2;
				p_group.len = t_groups[i].len + t_groups[j].len;
				p_group.messages = malloc(p_group.len * sizeof(t_message));
				for (k = 0; k < t_groups[i].len; ++k) {
				  p_group.messages[k] = t_groups[i].messages[k];
				}
				for (k = k, l = 0; l < t_groups[j].len; ++k, ++l) {
					p_group.messages[k] = t_groups[j].messages[l];
				}

				// Align the messages of the current group
				regex1.len = p_group.messages[0].len;
				regex1.regex = p_group.messages[0].message;
				regex1.mask = malloc(p_group.messages[0].len * sizeof(char));
				memset(regex1.mask, 2, p_group.messages[0].len);

				for (k = 1; k < p_group.len; ++k) {
					regex2.len = p_group.messages[k].len;
					regex2.regex = p_group.messages[k].message;
					regex2.mask = malloc(
							p_group.messages[k].len * sizeof(char));
					memset(regex2.mask, 2, p_group.messages[k].len);

					// TODO: free regex.mask and regex.regex
					regex.len = regex1.len + regex2.len;
					regex.regex = malloc(regex.len * sizeof(char));
					regex.mask = malloc(regex.len * sizeof(char));
					memset(regex.regex, 0, regex.len * sizeof(char));
					memset(regex.mask, 2, regex.len * sizeof(char));

					alignTwoSequences(regex1, regex2, &regex);

					free(regex1.mask);
					free(regex2.mask);
					regex1.len = regex.len;
					regex1.mask = regex.mask;
					regex1.regex = regex.regex;
				}
				matrix[i][j] = regex.score;

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
	  for (j = 0; j < t_groups[i].len; ++j) {
	    free( t_groups[i].messages[j].message );
	  }
	  free( t_groups[i].messages );
	}
	free( t_groups );
	
	return Py_BuildValue("(iif)", i_maximum, j_maximum, maxScore);
}

void initlibNeedleman() {
	(void) Py_InitModule("libNeedleman", libNeedleman_methods);
}

void alignTwoSequences(t_regex seq1, t_regex seq2, t_regex *regex) {
	const short int match = 10;
	const short int mismatch = -10;
	const short int gap = 0;

	// initiliaze the matrix with 0
	short int **matrix;
	unsigned short int i = 0;
	unsigned short int j = 0;

	matrix = (short int**) malloc( sizeof(short int*) * (seq1.len + 1) );
	for (i = 0; i < (seq1.len + 1); i++) {
	  matrix[i] = (short int*) malloc( sizeof(short int) * (seq2.len + 1) );
	  for(j = 0; j < (seq2.len + 1); j++)
	    {
	      matrix[i][j] = 0;
	    }
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
			if ((seq1.mask[i - 1] != 1) && (seq2.mask[j - 1] != 1)
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
	unsigned char *regex1 = malloc(
			(seq1.len + seq2.len) * sizeof(unsigned char));
	unsigned char *regex2 = malloc(
			(seq1.len + seq2.len) * sizeof(unsigned char));
	unsigned char *regex1Mask = malloc(
			(seq1.len + seq2.len) * sizeof(unsigned char));
	unsigned char *regex2Mask = malloc(
			(seq1.len + seq2.len) * sizeof(unsigned char));
	// TODO: (fgy) handle errors on malloc operation
	memset(regex1, 0x00, (seq1.len + seq2.len) * sizeof(unsigned char));
	memset(regex2, 0x00, (seq1.len + seq2.len) * sizeof(unsigned char));
	memset(regex1Mask, 2, (seq1.len + seq2.len) * sizeof(unsigned char));
	memset(regex2Mask, 2, (seq1.len + seq2.len) * sizeof(unsigned char));
	unsigned short int iReg1 = seq1.len + seq2.len - 1;
	unsigned short int iReg2 = seq1.len + seq2.len - 1;

	i = seq1.len;
	j = seq2.len;
	while (finish != TRUE) {
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
		} else if ((eltT >= eltL) && (eltT > eltD)) {
			--i;
			regex2[iReg2] = 0xff;
			regex2Mask[iReg2] = 1;
			regex1[iReg1] = seq1.regex[i];
			--iReg1;
			--iReg2;
		} else {
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

	for (i = 0; i < (seq1.len + 1); i++) {
	  free( matrix[i] );
	}
	free( matrix );

	// Compute the common regex
	unsigned short int iReg = seq1.len + seq2.len - 1;
	i = seq1.len + seq2.len - 1;
	while (i > 0) {
		if ((regex1Mask[i] == 2) && (regex2Mask[i] == 2)) {
			regex->regex[iReg] = 0xff;
			regex->mask[iReg] = 2;
			--iReg;
		} else if ((regex1Mask[i] == 1) || (regex2Mask[i] == 1)
				|| (regex1[i] != regex2[i])) {
			regex->regex[iReg] = 0xff;
			regex->mask[iReg] = 1;
			--iReg;
		} else {
			regex->regex[iReg] = regex1[i];
			regex->mask[iReg] = 0;
			--iReg;
		}
		--i;
	}

	// Compute the score of the regex
	float nbDynamic = 0.0f;
	float nbStatic = 0.0f;
	float cent = 100.0f;
	BOOL inDyn = FALSE;
	for (i = 0; i < regex->len; ++i) {
		if (regex->mask[i] == 0) {
			if (inDyn == TRUE) {
				nbDynamic = nbDynamic + 1.0f;
				inDyn = FALSE;
			}
			nbStatic = nbStatic + 1.0f;
		} else if (regex->mask[i] == 1)
			inDyn = TRUE;
	}
	if (inDyn == TRUE)
		nbDynamic = nbDynamic + 1.0f;

	regex->score = 100.0 / (nbStatic + nbDynamic) * nbStatic;

	// Room service
	free(regex1);
	free(regex2);
	free(regex1Mask);
	free(regex2Mask);
	// TODO: (fgy) avoid double freeing
}

int hexdump(unsigned char *buf, int dlen) {
	int OPL = 32;
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

