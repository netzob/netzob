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
#include "regex.h"

char* mError = NULL;

/*************************
 *	answer: must be deallocated after the call to match and align iif succeeded
 *	regex: regex string
 *	tomatch: the string to match with the regex
 *
 **************************/
int matchandalign(char** answer, char* regex, char* tomatch, int exactlymatch,
		int cimpl) {
	int indFields;
	Fields fields[MaxFields];

	indFields = match(regex, tomatch, fields, exactlymatch);
	if (indFields < 0) {
		char* errormsg;
		errormsg = (char*) calloc((strlen(regex) + 512), sizeof(char));
		doerrormessage(errormsg, indFields);
		fprintf(stderr, "%s\n\n", errormsg);
		dealloc((void **) &errormsg);
		return indFields;
	} else {
		*answer = (char*) calloc((strlen(tomatch) * 2 + 1), sizeof(char));
		computeAlignement(fields, exactlymatch, indFields, *answer, tomatch,
				cimpl);
		if (cimpl)
			showans(tomatch, *answer); // print the answer
		return 0;
	}

}

int matchonly(char* regex, char* tomatch) {
	int indFields;
	Fields fields[MaxFields];
	indFields = match(regex, tomatch, fields, 0);
	return indFields;
}

char* createtoken(unsigned int size, char* from) {
	char* nt;
	nt = (char *) calloc(size, sizeof(char));
	strncat(nt, from, size - 1);
	return nt;

}
int parsegroup(char* token, char ** groups) {
	int nbdifferentfield = 0;
	char* dot;
	char* nextdot;
	char* nextbrack;
	unsigned int ntsize = 0;

	dot = strchr(token, '.');
	while (dot != NULL) {
		nextbrack = strchr(dot, '}');
		nextdot = strchr(dot + 1, '.');
		if (dot != token) {
			ntsize = (unsigned int) (dot - token + 1);
			groups[nbdifferentfield] = createtoken(ntsize, token);
			nbdifferentfield++;
			token = dot;
		} else {
			//There are no more variable fields
			if (nextdot == NULL) {
				if (nextbrack == NULL) {
					ntsize = 2;
					groups[nbdifferentfield] = createtoken(ntsize, token);
					nbdifferentfield++;
					token = dot + 1;
				} else {
					ntsize = (unsigned int) (nextbrack - dot + 2);
					groups[nbdifferentfield] = createtoken(ntsize, token);
					nbdifferentfield++;
					token = nextbrack + 1;
				}
			}
			//There exist other variable fields
			else {
				//.__.{} case
				if (nextbrack == NULL || (nextbrack >= nextdot)) {
					ntsize = 2;
					groups[nbdifferentfield] = createtoken(ntsize, token);
					nbdifferentfield++;
					token = dot + 1;
				}
				//.{,}__. case
				else {
					ntsize = (unsigned int) (nextbrack - dot + 2);
					groups[nbdifferentfield] = createtoken(ntsize, token);
					nbdifferentfield++;
					token = nextbrack + 1;

				}
				ntsize = (unsigned int) (nextdot - token + 1);
				if (ntsize > 1) {
					groups[nbdifferentfield] = createtoken(ntsize, token);
					nbdifferentfield++;
				}
				token = nextdot;
			}
			dot = nextdot;
		}

	}
	if (strlen(token) > 0) {
		ntsize = (unsigned int) (strlen(token) + 1);
		groups[nbdifferentfield] = createtoken(ntsize, token);
		nbdifferentfield++;
	}
	return nbdifferentfield;
}

/*
 rollBack
 *********************************************
 shift:
 ind:     index of the previous variable field

 .......aaaaaa................bbbbbbb
 ^                ^
 |                |
 previous        too long
 */
int rollBack(unsigned int shift, int ind, Fields* fields, char* tomatch,
		int first, int lastvar) {
	char* nextmatching;
	Fields* stat = NULL;
	if (lastvar == 0)
		stat = (&fields[ind + 1]);
	Fields* var = (&fields[ind]);
	int retvalue = 0;
	if (first) {
		if (ind >= 2) {
			while (1) {
				if (!lastvar)
					shift = (unsigned int) (stat->add - var->add - var->max);
				retvalue = rollBack(shift, ind - 2, fields, tomatch, 0, 0);
				if (retvalue == 0) {
					var->add = fields[ind - 1].add + fields[ind - 1].len;
					if (!lastvar) {
						if (stat->add - var->add >= var->min) {
							var->len = (unsigned int) (stat->add - var->add);
							return 0;
						} else {
							nextmatching = strstr(var->add + var->min,
									stat->value);
							if (nextmatching == NULL) {
								return -1;
							} else {
								stat->add = nextmatching;
								var->len = (unsigned int) (nextmatching
										- var->add);
								if (var->len <= var->max)
									return 0;
							}
						}
					} else {
						var->add = fields[ind - 1].add + fields[ind - 1].len;
						if (strlen(var->add) >= var->min) {
							var->len = (unsigned int) (strlen(var->add));
							return 0;
						} else {
							return -1;
						}
					}
				} else
					return -1;
			}
		} else {
			return -1;
		}
	} else {
		nextmatching = strstr(stat->add + shift, stat->value);
		// Cannot shift the previous static field
		if (nextmatching == NULL) {
			return -1;
		}
		// The next matching of aaaaa is such as the len of the variable field is lower than the max authorized
		else if ((unsigned int) (nextmatching - var->add) <= var->max) {
			stat->add = nextmatching;
			var->len = (unsigned int) (nextmatching - var->add);
			return 0;
		} else if (ind >= 2) {
			shift = (unsigned int) (nextmatching - var->add - var->max);
			retvalue = rollBack(shift, ind - 2, fields, tomatch, 0, 0);
			if (retvalue == 0) {
				var->add = fields[ind - 1].add + fields[ind - 1].len;
				if (nextmatching - var->add >= var->min) {
					stat->add = nextmatching;
					var->len = (unsigned int) (nextmatching - var->add);
					return 0;
				} else {
					nextmatching = strstr(var->add + var->min, stat->value);
					if (nextmatching == NULL) {
						return -1;
					} else {
						stat->add = nextmatching;
						var->len = (unsigned int) (nextmatching - var->add);
						return 0;
					}
				}
			} else
				return -1;
		} else
			return -1;
	}
	return 0;
}

/*
 match
 *********************************************
 return:
 ind = last field index
 -1 : "format error"
 -2 : "not matching"


 */
int match(char* regex, char* tomatch, Fields* fields, int options) {
#define isgood(c) isalnum(c)||c==46

	//char delim='.';
	//char border[]="()";
	int ind = 0;
	unsigned int size = 0;
	char* posmatch;
	int maxlimit = strlen(tomatch);

	int rollret = 0;
	char* tomatchcopy = tomatch;
	int retvalue = 0;
	char* tempgroup;
	char* token;
	char* groups[MaxFields];
	int nbsubtoken = 0;
	int i;

	char opengroup = '(';
	char closegroup = ')';
	char* begin;
	char* end;
	int last = 0;
	int groupindex = 0;
	int decalgroup_index = 0;

	if (strlen(regex) <= 0)
		return -4;
	if (strlen(tomatch) <= 0)
		return -5;

	for (i = 0; i < MaxFields; i++) {
		fields[i].set = 0;
		fields[i].subfields = NULL;
		fields[i].lastfields = NULL;
	}

	while (1) {
		if (last || strlen(regex) == 0)
			break;
		begin = strchr(regex, opengroup);
		end = strchr(regex, closegroup);

		//Error of syntax
		if ((begin == NULL && end != NULL) || (begin != NULL && end == NULL)
				|| (end < begin) || (end == begin + 1)
				|| (begin != NULL && end != NULL
						&& strchr(begin + 1, opengroup) != NULL
						&& strchr(begin + 1, opengroup) < end)) {
			mError = (char*) malloc((strlen(regex) + 1) * sizeof(char));
			memset(mError, 0, (strlen(regex) + 1));

			freeFieldsCompletly(fields, ind + 1);
			if (end == NULL) {
				strcat(mError, regex);
				return -6;
			} else if (begin == NULL) {
				strcat(mError, regex);
				return -7;
			} else if (end == begin + 1) {
				strcat(mError, regex);
				return -8;
			} else if (begin != NULL && end != NULL
					&& strchr(begin + 1, opengroup) < end) {
				strcat(mError, begin);
				return -9;
			} else
				return -1;
		}
		//There is no more group
		else if (begin == NULL && end == NULL) {
			//If option: we want only the variable field
			if (options) {
				decalgroup_index = 1;
			}
			last = 1;
			tempgroup = regex;
			regex += strlen(regex);
			if (groupindex > 0)
				groupindex = 0;
			--groupindex;
		}
		//We enter a group
		else if (begin == regex) {
			//If option: reset decalgroup_index to 0 as we are in a group:
			//In a group: variable and constant field are put together
			if (options) {
				decalgroup_index = 0;
			}
			tempgroup = (char *) malloc((end - begin) * sizeof(char));
			memset(tempgroup, 0, (end - begin));
			strncpy(tempgroup, begin + 1, (end - begin - 1));
			regex = end + 1;
			if (groupindex < 0)
				groupindex = 0;
			++groupindex;
		}
		//abcd(foo) case: we take the abcd part
		else {
			//If option: we want only the variable field
			if (options) {
				decalgroup_index = 1;
			}
			tempgroup = (char *) malloc((begin - regex + 1) * sizeof(char));
			memset(tempgroup, 0, (begin - regex + 1));
			strncpy(tempgroup, regex, (begin - regex));
			regex = begin;
			if (groupindex > 0)
				groupindex = 0;
			--groupindex;
		}
		nbsubtoken = parsegroup(tempgroup, groups);
		if (!last) {
			free(tempgroup);
			tempgroup = NULL;
		}
		if (nbsubtoken <= 0) {
			freeFieldsCompletly(fields, ind + 1);
			return -1;
		}

		for (i = 0; i < nbsubtoken; i++) {
			token = groups[i];
			//Very first field
			if (fields[ind].set == 0) {
				groupindex -= (decalgroup_index
						+ (!options) * (groupindex < 0 ? 1 : 0));
				retvalue = newField(&fields[ind], isStatic(token, '.'), tomatch,
						token, maxlimit, groupindex);
				if (retvalue < 0) {
					freeFieldsCompletly(fields, ind + 1);
					freeTokens(groups, i + 1, nbsubtoken);
					return retvalue;
				}
				size += strlen(token);
			}

			//New type of field
			else if (fields[ind].isStatic != isStatic(token, '.')) {
				if (fields[ind].isStatic) {
					setFieldvalue(&fields[ind]);
					if (ind == 0) {
						posmatch = strstr(tomatch, fields[ind].value);
						if (posmatch != tomatch) {
							freeFieldsCompletly(fields, ind + 1);
							freeTokens(groups, i, nbsubtoken); //index == i as we didn't put the token anywhere for now
							return -2;
						} else {
							setAdd(&fields[ind], posmatch);
							tomatch = posmatch + fields[ind].len;
						}
					} else {
						posmatch = strstr(tomatch + fields[ind - 1].min,
								fields[ind].value);
						if (posmatch == NULL) {
							freeFieldsCompletly(fields, ind + 1);
							freeTokens(groups, i, nbsubtoken); //index == i as we didn't put the token anywhere for now
							return -2;
						} else if ((unsigned int) (posmatch - tomatch)
								> fields[ind - 1].max) {
							rollret = rollBack(0, ind - 1, fields, tomatchcopy,
									1, 0);
							if (rollret != 0) {
								freeFieldsCompletly(fields, ind + 1);
								freeTokens(groups, i, nbsubtoken); //index == i as we didn't put the token anywhere for now
								return -2;
							}
							//fields[ind-1].len = (int)(fields[ind].add-fields[ind-1].add);
							tomatch = fields[ind].add + fields[ind].len;
						} else {
							fields[ind - 1].len = (int) (posmatch - tomatch);
							setAdd(&fields[ind], posmatch);
							tomatch = posmatch + fields[ind].len;
						}
					}
				} // End if(fields[ind].isStatic)
				size = 0;
				ind++;
				if (ind >= MaxFields - 1) {
					freeFieldsCompletly(fields, ind);
					freeTokens(groups, i, nbsubtoken); //index == i as we didn't put the token anywhere for now
					return -3;
				}
				groupindex -= (decalgroup_index
						+ (!options) * (groupindex < 0 ? 1 : 0));
				retvalue = newField(&fields[ind], isStatic(token, '.'), tomatch,
						token, maxlimit, groupindex);
				if (retvalue < 0) {
					freeFieldsCompletly(fields, ind + 1);
					freeTokens(groups, i + 1, nbsubtoken);
					return retvalue;
				}
				size += strlen(token);
			}

			//Same type of field => push the subfield in the chainlist
			else {
				groupindex -= (decalgroup_index
						+ (!options) * (groupindex < 0 ? 1 : 0));
				retvalue = addSubfield(&fields[ind], token, maxlimit,
						groupindex);
				if (retvalue < 0) {
					freeFieldsCompletly(fields, ind + 1);
					freeTokens(groups, i + 1, nbsubtoken);
					return retvalue;
				}
				size += strlen(token);
			}

		} //end for subtoken

	}
	/*******************************************************/
	//last field
	//Last field is static
	if (fields[ind].isStatic) {
		setFieldvalue(&fields[ind]);
		if (ind == 0) {
			posmatch = strstr(tomatch, fields[ind].value);
			if (posmatch != tomatch) {
				freeFieldsCompletly(fields, ind + 1);
				return -2;
			} else {
				setAdd(&fields[ind], posmatch);
				tomatch = posmatch + fields[ind].len;
			}
		} else {
			posmatch = strstr(tomatch + fields[ind - 1].min, fields[ind].value);
			if (posmatch == NULL) {
				freeFieldsCompletly(fields, ind + 1);
				return -2;
			}

			if (strcmp(tomatch + (strlen(tomatch) - strlen(fields[ind].value)),
					fields[ind].value) != 0) {
				freeFieldsCompletly(fields, ind + 1);
				return -2;
			} else {
				posmatch = tomatch
						+ (strlen(tomatch) - strlen(fields[ind].value));
				setAdd(&fields[ind], posmatch);
			}
			if ((unsigned int) (posmatch - tomatch) > fields[ind - 1].max) {
				rollret = rollBack(0, ind - 1, fields, tomatchcopy, 1, 0);
				if (rollret != 0) {
					freeFieldsCompletly(fields, ind + 1);
					return -2;
				}
				tomatch = fields[ind].add + fields[ind].len;
			} else {
				fields[ind - 1].len = (int) (posmatch - tomatch);
				setAdd(&fields[ind], posmatch);
				tomatch = posmatch + fields[ind].len;
			}
		}
	}
	//Last field is dynamic
	else {
		fields[ind].len = strlen(tomatch);
		if (strlen(tomatch) > fields[ind].max) {
			rollret = rollBack(strlen(tomatch) - fields[ind].max, ind, fields,
					tomatchcopy, 1, 1);
			if (rollret != 0) {
				freeFieldsCompletly(fields, ind + 1);
				return -2;
			}
		} else if (strlen(tomatch) < fields[ind].min) {
			freeFieldsCompletly(fields, ind + 1);
			return -2;
		}

	}
	freeFields(fields, ind + 1);
	return ind;
}

char* computeAlignement(Fields* fields, int options, int indFields,
		char* answer, char* message, int cimplement) {

	if (indFields >= 0) {
		unsigned int len = (strlen(message) * 2 + 1);
		char* tempans = (char*) malloc(len * sizeof(char));
		memset(tempans, 0, len);
		int groupindex = 0;
		int i;

		for (i = 0; i <= indFields; i++) {
			adjustfield(&fields[i]);
			if (!i)
				groupindex = (fields[i].subfields)->groupindex;
			while (fields[i].subfields != NULL) {
				if ((fields[i].subfields)->groupindex != groupindex) {
					if (!options || (options && strlen(tempans))) {
						strcat(answer, tempans);
						answer[strlen(answer)] = 1;
						//strcat(answer,"\x01");
					}
					memset(tempans, 0, len);
					groupindex = (fields[i].subfields)->groupindex;
				}
				retField(tempans, &fields[i], fields[i].subfields, options);
			}
		}
		if (!options || (options && strlen(tempans))) {
			strcat(answer, tempans);
			if (cimplement)
				answer[strlen(answer)] = 1;
//	        strcat(answer,"\n");
		}
		free(tempans);
		return answer;
	}
	//Error
	return NULL;

}
void retField(char *string, Fields* field, Subfield* sub, int options) {
	field->subfields = sub->next;
	if ((!options)
			|| (options == 1 && (sub->groupindex > 0 || !field->isStatic))
			|| (options == 2 && sub->groupindex > 0)) {
		strncat(string, field->add + sub->offset, sub->len);
	}
	dealloc((void **) &sub);

}

void showans(char* message, char* answer) {
	char* next;
	char* match;
	int len = strlen(message) + 1;
	char* copy = (char*) malloc(len * sizeof(char));
	char* token = (char*) malloc(len * sizeof(char));

	memset(copy, 0, len);
	while (1) {
		memset(token, 0, len);
		next = strchr(answer, '\x01');
		strncat(token, answer, (unsigned int) (next - answer));
		match = strstr(message, token);
		if (match == NULL)
			break;
		if (next == NULL)
			break;
		couleur("0");
		strncat(copy, message, (unsigned int) (match - message));
		printf("%s", copy);
		memset(copy, 0, len);
		couleur("31");
		strncat(copy, match, strlen(token));
		printf("%s", copy);
		memset(copy, 0, len);
		message = match + strlen(token);
		answer = next + 1;
	}
	if (strlen(message) > 0) {
		couleur("0");
		printf("%s\n", message);
	} else {
		printf("\n");
	}
	couleur("0");
	free(copy);
	free(token);
}

