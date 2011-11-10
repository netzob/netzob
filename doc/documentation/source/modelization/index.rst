.. currentmodule:: netzob

.. _modelization:

************
Modelization
************

A communication protocol can be defined through its :

* Vocabulary (set of valid words)
* Grammar (set of valid sentences)

Netzob provides a framework for the modelization (inference) of communication protocols, i.e. inferring its vocabular and grammar.

[INCLURE GRAPH]

* Vocabular inference
   * Message structure inference (based on sequence alignment)
   * Regoupment of similar message structures
   * Field type inference
   * Field dependencies from the same message and from the environment
   * Field semantic inference
* Grammar inference
   * Identification of the automata of the protocol
   * Fields dependencies with messages of previous states

All the functionalities of the framework are detailled in this chapter.

.. toctree::
   :maxdepth: 2

   vocabular
   grammar
