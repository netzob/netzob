// -*- coding: utf-8 -*-

//+---------------------------------------------------------------------------+
//|          01001110 01100101 01110100 01111010 01101111 01100010            |
//|                                                                           |
//|               Netzob : Inferring communication protocols                  |
//+---------------------------------------------------------------------------+
//| Copyright (C) 2011-2017 Georges Bossert and Frédéric Guihéry              |
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

#include <stdio.h>
#include "libRelation.h"
#include "relation.h"

#define DEXC(stmt) if (stmt) PyErr_Print()

PyObject *exception = NULL;

static PyMethodDef relation_methods[] = {
    {"find", py_find, METH_VARARGS,
     "Iterate over relation algorithms"},
    {NULL, NULL, 0, NULL}
};

PyObject* PyInit__libRelation(void) {
  static struct PyModuleDef moduledef = {
    PyModuleDef_HEAD_INIT,
    "_libRelation",
    NULL,
    -1,
    relation_methods,
    NULL,
    NULL,
    NULL,
    NULL
  };

  return PyModule_Create(&moduledef);

    /* PyObject *d = PyDict_New(); */
    /* exception = PyErr_NewException("_libRelation.error", NULL, NULL); */
    /* PyDict_SetItemString(d, "error", exception); */
}

/*
 * C wrapper for function "find" of _libRelation.
 * This functions takes a two-dimension array built like this:
 * > [(m0f0, m0f1, ...), (m1f0, m1f1, ...)]
 */
static PyObject*
py_find(__attribute__((unused))PyObject* self, PyObject* args) {
    PyObject* pListCells;
    PyObject* pCells;
    PyObject* pCell;
    PyObject* pDm = NULL;
    size_t cells_hlen, cells_vlen;
    unsigned int i, j;
    char ***pppCells = NULL;
    struct relation_datamodel* dm = NULL;

    /* Parse arguments */
    if ((pListCells = PyTuple_GetItem(args, 0)) == NULL) {
    fprintf(stderr, "ERROR: Unable to parse args\n");
        goto end;
    }

    /* Check type of arguments */
    if (!PySequence_Check(pListCells)) {
        fprintf(stderr, "ERROR: Unable to parse arg as list\n");
        goto end;
    }

    cells_hlen = PySequence_Size(pListCells);

    if ((pppCells = malloc(cells_hlen * sizeof(*pppCells))) == NULL)
        goto end;

    /* Allocation is based on the length of the first row */
    pCells = PySequence_GetItem(pListCells, 0);
    if (!PySequence_Check(pCells)) {
        fprintf(stderr, "ERROR: Unable to get list item\n");
        goto end;
    }

    /* Do str dups */
    cells_vlen = PySequence_Size(pCells);
    for (i = 0; i < cells_hlen; i++) {
        /* Get, check and copy messages refs */
        pCells = PySequence_GetItem(pListCells, i);
        if (!PySequence_Check(pCells))
            goto end2;
        if ((pppCells[i] = malloc(cells_vlen * sizeof(**pppCells))) == NULL)
            goto end2;
        for (j = 0; j < cells_vlen; j++) {
            /* Get, check and copy cells */
            pCell = PySequence_GetItem(pCells, j);
            if (!PyBytes_Check(pCell))
                goto end2;
            if ((pppCells[i][j] = malloc(PyBytes_Size(pCell) * sizeof(**pppCells))) == NULL)
                goto end2;
            strcpy(pppCells[i][j], PyBytes_AsString(pCell));
        }
    }
    relation_find(&dm, (const char***)pppCells, cells_hlen, cells_vlen);
    pDm = create_python_dm(dm);

 end2:
    for (i = 0; i < cells_hlen; i++) {
        if (pppCells[i] != NULL)
            for (j = 0; j < cells_vlen; j++)
                if (pppCells[i][j] != NULL)
                    free(pppCells[i][j]);
        free(pppCells[i]);
    }
 end:
    if (pppCells != NULL)
        free(pppCells);
    return pDm;
}

/*
 * Convert the native datamodel to a Python structure.
 */
static PyObject*
create_python_dm(struct relation_datamodel* dm)
{
    struct relation_datamodel* dm_it = dm;
    struct relation_matches* matches;
    struct relation_matches* matches_tmp;
    PyObject* pDm = NULL;
    PyObject* pAlgoName;
    PyObject* pRefs;
    PyObject* pRefConfig;
    PyObject* pRels;
    PyObject* pRelConfig;

    if (!(pDm = PyDict_New()))
        goto error;
    while (dm_it) {
        pAlgoName = PyBytes_FromString(dm_it->algo_name);

        /* Amend/append a algo/match node */
        if (!(pRefs = PyDict_GetItem(pDm, pAlgoName)))
            if (!(pRefs = PyList_New(0)))
                goto error;

        matches = dm_it->matches;
        while (matches != NULL) {
            pRelConfig = Py_BuildValue("(Ikk)",
				       matches->match.cell_rel_idx,
				       matches->match.cell_rel_off,
				       matches->match.cell_rel_size);
            pRels = Py_BuildValue("[O]", pRelConfig);

            pRefConfig = Py_BuildValue("(IOOO)",
				       matches->match.cell_ref_idx,
				       Py_None,
				       Py_None,
				       pRels);
            PyList_Append(pRefs, pRefConfig);

            matches_tmp = matches->next;
            free(matches);
            matches = matches_tmp;
        }

        /* Append configuration of reference as tuple */
        PyDict_SetItem(pDm, pAlgoName , pRefs);

        /* next algo */
        dm_it = dm_it->next;
    }
    return pDm;
 error:
    Py_RETURN_NONE;
}
