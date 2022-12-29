
.. _fuzzing:

..
   Fuzzing with Netzob
   ===================

.. _fuzzing_symbols:

Format Message Fuzzing
----------------------

The Preset class can also be used to apply format message fuzzing. Fuzzing configuration is provided by the :meth:`fuzz` method.

.. automethod:: netzob.Model.Vocabulary.Preset.Preset.fuzz(key, mode=None, generator=None, seed=None, counterMax=None, kwargs=None)

.. automethod:: netzob.Model.Vocabulary.Preset.Preset.setFuzzingCounterMax

.. automethod:: netzob.Model.Vocabulary.Preset.Preset.getFuzzingCounterMax

.. automethod:: netzob.Model.Vocabulary.Preset.Preset.unset


.. raw:: latex

   \newpage


.. _fuzzing_automata:

Fuzzing Automata
----------------

Mutation of a protocol state machine is provided by the :meth:`mutate` method of the :class:`Automata <netzob.Model.Grammar.Automata.Automata>` class.

.. automethod:: netzob.Model.Grammar.Automata.Automata.mutate

.. raw:: latex

   \newpage
