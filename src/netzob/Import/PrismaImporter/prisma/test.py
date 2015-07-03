#!/usr/bin/env python

from PrismaState import PrismaState as S
from MarkovModel import MarkovModel
from MarkovTransition import MarkovTransition as P

if __name__ == '__main__':
    print('init state A a|b -> b|c')
    stateA = P(S('a','b'),S('b','c'))
    print(stateA)
    print('init state B b|c -> c|d')
    stateB = P(S('b','c'),S('c','d'))
    print(stateB)
    print('A==B')
    print(stateA==stateB)
    print('B==B')
    print(stateB==stateB)
    print('B==A')
    print(stateB==stateA)
    print('illegal state a|b -> c|d')
    try:
        stateC =P(S('a','b'),S('c','d'))
        print(stateC)
    except RuntimeError as e:
        print(e)
    model = MarkovModel()
    model.add(stateA)
    model.add(stateB)
    stateC = P(S('b','c'),S('c','f'))
    stateCC = P(S('"b"','"c"'),S('"c"','"f"'))
    stateD = P(S('d','c'),S('c','d'))
    stateE = P(S('b','e'),S('e','d'))
    print(stateC.__repr__())
    print(stateC==stateCC)
    model.add(stateC)
    model.add(stateCC)
    model.add(stateD)
    model.add(stateE)
    for i,j in model:
        print(i,list(map(str,j)))
    exit()
