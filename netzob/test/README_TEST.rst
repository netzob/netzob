==========================================
Netzob : Inferring Communication Protocols
==========================================

Testing Netzob
==============

In this README, we detail how we test Netzob.
After few releases, we acknowledged the fact that Netzob is in beta
and that lots of bugs and errors limit user experience. 

We therefore introduced more testing to increase the user experience and limit the development cost 
due to useless bug hunting. 

However, we also consider tests to be a nice way to document netzob's core and its usage. 

How to Test Netzob
==================

$ python setup.py test

The simplest way to execute tests is to use the specific 'test' command we provided in the setup.py file. 
It fetches the 'global_suite' tests detailled in 'test/src/test_netzob/suite_Global.py'.
Results are either written in stdout or under an xml pyTest (jtest) format. 

How to Configure Tests Reports
------------------------------

Enable stdout reporting with the following test section in setup.cfg
[test]
reportfile=

Enable a pyTest file reporting with the following test section in setup.cfg
[test]
reportfile=unittest-results.xml

How to Write a Test
===================

Let's say you want to write a test (or an example) of a code in Netzob core.
Two solutions are available, 
1) create a unittest 
2) create a doctest.

In the first solution, you pick (or create) a test category and add your test module in its suite (see examples in 'test/src/test_netzob/suite_Tutorials.py').
In the second solution, you write your test directly in the docstring of a Netzob object and reference the object in 'test/src/test_netzob/suite_DocTests.py'





