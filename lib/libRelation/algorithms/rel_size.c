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
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include "relation.h"

static unsigned int MIN_SIZE = 2;

/*
 * wrapper of string comparison used to detect a relation with the
 * specified parameters.
 */
static int
get_match(const char* cell_ref, const char* cell_rel,
	  size_t start, size_t len)
{
    int ret = -1;
    size_t size_ref, size_rel;
    char* remaining_str;
    unsigned long val_integer;
    char* tmp_cell_rel;

    DLOG("    ref=%s, rel=%s, start=%d, len=%d\n", cell_ref, cell_rel, start, len);

#if defined(__DEBUG__) && false
    char* new_rel;
    if ((new_rel = malloc((len + 1) * sizeof(*new_rel)))) {
        new_rel[len] = '\0';
        DLOG("%s == %s ?", cell_ref, strncpy(new_rel, &cell_rel[start], len));
        free(new_rel);
    }
#endif

    tmp_cell_rel = malloc(len + 1);
    strncpy(tmp_cell_rel, &cell_ref[start], len);
    tmp_cell_rel[2] = '\0';
    val_integer = strtoul(tmp_cell_rel, &remaining_str, 16);
    // printf("PANNNN: %s\n", tmp_cell_rel);
    // printf("PANNNN: %ud\n\n", val_integer);
    free(tmp_cell_rel);

    DLOG("strlen(cell_rel)=%d\n", strlen(cell_rel));
    if (val_integer != 0 && val_integer == (strlen(cell_rel) / 2)) {
      DLOG("      OK!!\n");
      ret = 0;
    }
    else
      ret = -1;

    //    ret = strncmp(cell_ref, &cell_rel[start], len);
#if defined(__DEBUG__) && false
    DLOG(" %d\n", ret);
#endif
    return ret;
}

/*
 * Append a node to the set of matches.
 */
static struct relation_matches*
append_match(struct relation_matches** matches,
	     const struct relation_match* match)
{
    struct relation_matches* new = NULL;

    if (!(new = malloc(sizeof(*new))))
        return NULL;
    new->next = *matches;
    memcpy(&new->match, match, sizeof(new->match));
    *matches = new;
    return new;
}

/*
 * Returns the first non-matching message index.
 */
static int
verify_match(const char*** messages, size_t msgs_len, size_t cells_len,
	     const struct relation_match* match)
{
    int i;
    int ret = 0;
    const char** cells;
    const char* ref;
    const char* rel;

    DLOG("Verifying M%04d", 0);
    for (i = 0; i < msgs_len; i++) {
        if (i == match->message_idx)
            continue;
        cells = messages[i];
        ref = cells[match->cell_ref_idx];
        rel = cells[match->cell_rel_idx];
        DLOG2("\b\b\b\b%04d", i);
        if (get_match(ref, rel, match->cell_rel_off, match->cell_rel_size)) {
            ret = i;
            break;
        }
    }
    DLOG2("\n");
    return ret;
}

/*
 * Main function used to build a set of matches.
 */
static struct relation_matches*
relation_size_find(const char*** messages, int row, int idx,
		       size_t vlen, size_t hlen)
{
    int i, ret;
    size_t off;
    int found = 0;
    int match_res;
    const char** cells;
    const char* ref;
    size_t ref_len;
    const char* rel;
    size_t rel_len;
    struct relation_matches* matches = NULL;
    struct relation_match match;

    cells = messages[row];
    ref = cells[idx];
    ref_len = strlen(ref);

    for (i = 0; i < hlen; i++) {
      if (idx == 5)
	DLOG("   i = %d\n", i);
        rel = cells[i];
        rel_len = strlen(rel);
        if (i != idx && rel && ref_len >= MIN_SIZE) {
	  off = 0;
	  //            for (off = 0; off <= rel_len; off++) {
                if (!(match_res = get_match(ref, rel, off, ref_len))) {
                    match.message_idx = row;
                    match.cell_ref_idx = idx;
                    match.cell_rel_idx = i;
                    match.cell_rel_off = off;
                    match.cell_rel_size = ref_len;
                    DLOG("possible match found: M%d F%d[:], F%d[%ld:%ld] (%s)\n",
			 row, idx, i, off, off+ref_len, ref);
                    if ((ret = verify_match(messages, vlen, hlen,
					    (const struct relation_match*)&match)) != 0) {
                        DLOG("verification failed at M%d\n", ret);
                        continue;
                    }
                    DLOG("MATCH FOUND\n");
                    DLOG(">> %p\n", matches);
                    append_match(&matches, (const struct relation_match*)&match);
                    DLOG(">> %p\n", matches);
                }
		//            }
        }
    }
    return matches;
}

struct relation_algorithm_operations operations = {
    .name = "size",
    .find = relation_size_find
};
