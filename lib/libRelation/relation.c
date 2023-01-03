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

#define _GNU_SOURCE

#include <dirent.h>
#include <dlfcn.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "relation.h"

static const char* algorithm_path = "lib/libRelation/algorithms";

/*
 * Build a native datamodel containing results.
 */
void
relation_find(struct relation_datamodel** dm,
	      const char*** data,
	      size_t vlen, size_t hlen)
{
    unsigned int i, j;
    struct relation_matches* matches;
    struct relation_algorithm_operations_list* algo_opers;

    algo_opers = search_algorithms();
    while (algo_opers) {
        DLOG("ALGO %s\n", algo_opers->data.name);
        for (i = 0; i < vlen; i++) {
            for (j = 0; j < hlen; j++) {
	      DLOG("-- idx = %d\n", j);
                matches = algo_opers->data.find(data, i, j, vlen, hlen);
                if (matches != NULL)
                    append_algo_matches(dm, algo_opers, matches);
            }
            /* only search over the first row, others are useless */
            break;
        }
        algo_opers = algo_opers->next;
    }
    clean_algo(algo_opers);
}

/*
 * Append a result to the datamodel structure.
 */
struct relation_datamodel*
append_algo_matches(struct relation_datamodel** dm,
		    struct relation_algorithm_operations_list* opers,
		    struct relation_matches* matches)
{
    struct relation_datamodel* new;

    if (!(new = malloc(sizeof(*new))))
        return NULL;
    new->next = *dm;
    new->matches = matches;
    new->algo_name = opers->data.name;
    *dm = new;
    return new;
}

/*
 * Build a list of libRelation algorithm.
 * This structure contains a handle returned by dlopen() of libraries.
 */
struct relation_algorithm_operations_list*
search_algorithms(void)
{
    DIR* pDir;
    struct dirent* entry;
    void* pLib;
    char* libPath;
    int libPathLen;
    struct relation_algorithm_operations* algo_oper;
    struct relation_algorithm_operations_list* algo_opers = NULL;
    struct relation_algorithm_operations_list* algo_opers_prev = NULL;

    DLOG("Searching in %s\n", algorithm_path);
    if ((pDir = opendir(algorithm_path)) == NULL)
        goto end;
    while ((entry = readdir(pDir)) != NULL) {
        if (strstr(entry->d_name, ".so") != NULL) {
            libPathLen = strlen(algorithm_path) + 1 + strlen(entry->d_name);
            if (!(libPath = malloc(sizeof(*libPath) * (libPathLen + 1)))) {
                perror("search_algorithms()");
                goto end;
            }
            if (snprintf(libPath, libPathLen + 1, "%s/%s", algorithm_path, entry->d_name) != libPathLen) {
                fprintf(stderr, "snprintf() failed at %s:%d\n", __FILE__, __LINE__);
                fprintf(stderr, " %s\n", libPath);
                goto end;
            }
            if (!(pLib = dlopen(libPath, RTLD_NOW|RTLD_GLOBAL))) {
                DLOG("Skipping '%s'\n", libPath);
                goto next;
            }
            dlerror(); // clear last error
            algo_oper = dlsym(pLib, "operations");
            /* Check current error flag */
            if (dlerror() != NULL)
                goto next;
            DLOG("[%s] Operations loaded\n", libPath);
            if (!(algo_opers = malloc(sizeof(*algo_opers))))
                goto next;
            algo_opers->next = algo_opers_prev;
            algo_opers->pHandle = pLib;
            memcpy(&algo_opers->data, algo_oper, sizeof(*algo_oper));
            algo_opers_prev = algo_opers;
            DLOG("[%s] Algo added\n", algo_opers->data.name);
        next:
            free(libPath);
            continue;
        }
    }

    closedir(pDir);
 end:
    return algo_opers;
}

/*
 * Correctly free a relation_algorithm_operations_list recursively.
 */
void
clean_algo(struct relation_algorithm_operations_list* algo)
{
    struct relation_algorithm_operations_list* cur = algo;
    struct relation_algorithm_operations_list* next;

    while (cur) {
        if (cur->pHandle)
            dlclose(cur->pHandle);
        next = cur->next;
        free(cur);
        cur = next;
    }
}
