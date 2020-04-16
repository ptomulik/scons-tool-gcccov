scons-tool-gcccov - developer's notes
=====================================

This module is designed to be developed with the help of pipenv_.

Initialization
--------------

On a fresh clone do::

   pipenv install --dev
   pipenv run bin/downloads.py

Running tests
-------------

There are some end-to-end tests. They can be ran this way::

   pipenv run python runtest -e test/system


Creating package for distribution
---------------------------------

.. code:: shell

   pipenv run python setup.py sdist bdist_wheel


Uploading to test.pypi.org_
---------------------------

.. code:: shell

   pipenv run twine upload -r testpypi dist/*

Uploading to pypi.org_
-----------------------

.. code:: shell

   pipenv run twine upload dist/*

LICENSE
-------

Copyright (c) 2018-2020 by Paweł Tomulik <ptomulik@meil.pw.edu.pl>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE

.. _scons-tool-gcccov: https://github.com/ptomulik/scons-tool-gcccov
.. _pipenv: https://pipenv.readthedocs.io/
.. _test.pypi.org: https://test.pypi.org/
.. _pypi.org: https://pypi.org/

.. <!--- vim: set expandtab tabstop=2 shiftwidth=2 syntax=rst: -->
