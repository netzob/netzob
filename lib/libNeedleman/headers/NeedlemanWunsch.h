#ifndef __NeedlemanWunsch_header
#define __NeedlemanWunsch__header

#include <Python.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <omp.h>

/**
 * Definitions of the different ENUM and Types
 */

typedef enum {
	FALSE, TRUE
} BOOL;

typedef struct {
	unsigned short int len; // length of the message
	unsigned char *message; // a message
} t_message;

typedef struct {
	unsigned short int len; // nb of messages in the group
	t_message *messages; // a list of messages
} t_group;

typedef struct {
	unsigned short int len; // size of the regex
	unsigned char *regex; // the actual regex
	unsigned char *mask; // its mask
	float score;
} t_regex;

static PyObject* py_getMatrix(PyObject* self, PyObject* args);
static PyObject* py_alignSequences(PyObject* self, PyObject* args);

void initlibNeedleman();
void alignTwoSequences(unsigned short int doInternalSlick, t_regex seq1, t_regex seq2, t_regex *regex);
int hexdump(unsigned char *buf, int dlen);
void dumpRegex(t_regex regex);

/**
 * Bind Python function names to our C functions
 */
static PyMethodDef libNeedleman_methods[] = {
	{"getMatrix", py_getMatrix, METH_VARARGS},
	{"alignSequences", py_alignSequences, METH_VARARGS},
	{NULL, NULL}
};
#endif
