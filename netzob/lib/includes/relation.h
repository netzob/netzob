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

#ifndef  RELATION_H
# define RELATION_H

# include <stdio.h>
/* only request size_t to stddef.h */
# define __need_size_t
# include <stddef.h>
# undef  __need_size_t

struct relation_datamodel {
    const char* algo_name;
    struct relation_matches* matches;
    struct relation_datamodel* next;
};

struct relation_match {
    unsigned int message_idx;
    unsigned int cell_ref_idx;
    unsigned int cell_rel_idx;
    size_t cell_rel_off;
    size_t cell_rel_size;
};

struct relation_matches {
    struct relation_match match;
    struct relation_matches* next;
};

struct relation_algorithm_operations {
    const char* name;
    struct relation_matches* (*find) (const char***, int, int, size_t, size_t);
};

struct relation_algorithm_operations_list {
    void* pHandle;
    struct relation_algorithm_operations data;
    struct relation_algorithm_operations_list* next;
};

void relation_find(struct relation_datamodel**, const char***, size_t, size_t);
struct relation_datamodel*
append_algo_matches(struct relation_datamodel**,
                                        struct relation_algorithm_operations_list*,
                                        struct relation_matches*);
struct relation_algorithm_operations_list* search_algorithms(void);
void clean_algo(struct relation_algorithm_operations_list* algo);

# ifdef __DEBUG__
#  define DLOG(...) {						\
    fprintf(stderr, "[%s:%d] ", __FILE__, __LINE__);			\
    DLOG2(__VA_ARGS__);							\
  }
#  define DLOG2(...) fprintf(stderr, __VA_ARGS__)
# else
#  define DLOG(...)
#  define DLOG2(...)
# endif /* __DEBUG__ */

#endif /* RELATION_H */
