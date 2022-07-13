---
title: "Django Readonly Field - Chapter 3 - Testing and Continuous Integration"
icon: flask
---

Hello folks !

This is the third article on a [series]({% post_url 2016-10-22-django-readonly-field-1-lib %}) I'm trying to make about Django Readonly Field. This one is not about Django Readonly field. Or more precisely it's not specific to Django Readonly Field. I'll talk about all the (quite classical) tools I use to be confident that a package I'm making works. I might also talk about project organization, docs and such.

Tests
=====

Coding habits include testing your code. Good coding habits include writing automated testing. Great coding habits include writing your tests even before you write your code. On that matter, I have to recommand [Harry Percival's excellent Test Driven Development with Python](http://chimera.labs.oreilly.com/books/1234000000754) (_Obey the testing goat !_)

:warning: I'm not an expert in writing a good quality maintainable test suite (not any more than anything in this blog, even if I probably make a good job pretending so). Don't take my word for it on anything. If you know I'm wrong, please correct me. If you're unsure, find reliable sources :smile:

A bit of theory.
----------------

There are several species of tests

Coverage
========

Tox
===

Makefile
========

Travis
======

DJ-Database-URL
===============
