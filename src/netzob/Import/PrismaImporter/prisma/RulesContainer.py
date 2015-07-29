#!/usr/bin/env python


class RulesContainer(object):
    def __init__(self):
        self.rules = {}

    def __str__(self):
        s = ''
        for key in self.rules:
            for value in self.rules[key]:
                s += str(value) + ', '
        return s[:-2]

    def __getitem__(self, key):
        return self.rules[key]

    def __iter__(self):
        return self.rules.items().__iter__()

    def keys(self):
        return self.rules.keys()

    def __len__(self):
        return len(self.rules)

    def add(self, rule):
        if rule.hist not in self.rules:
            self.rules[rule.hist] = []
        self.rules[rule.hist].append(rule)

