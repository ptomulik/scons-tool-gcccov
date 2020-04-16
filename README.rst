scons-tool-gcccov
=================

.. image:: https://badge.fury.io/py/scons-tool-gcccov.svg
    :target: https://badge.fury.io/py/scons-tool-gcccov
    :alt: PyPi package version

.. image:: https://travis-ci.org/ptomulik/scons-tool-gcccov.svg?branch=master
    :target: https://travis-ci.org/ptomulik/scons-tool-gcccov
    :alt: Travis CI build status

.. image:: https://ci.appveyor.com/api/projects/status/github/ptomulik/scons-tool-gcccov?svg=true
    :target: https://ci.appveyor.com/project/ptomulik/scons-tool-gcccov


Support for gcc_ code coverage features. Note, this is not a tool for running
gcov_ program.

Overview
--------

gcc_ (and clang_) is able to generate coverage info for gcov_ tool. You can use
gcov_ to test code coverage in your programs. It helps discover where your
optimization efforts will best affect your code.

gcov_ uses two files for profiling, see `gcov files`_.  The names of these
files are derived from the original *object* file by substituting the file
suffix with either ``.gcno``, or ``.gcda``. The ``.gcno`` notes file is
generated when the source file is compiled. The ``.gcda`` count data file is
generated when a program containing object files is executed. A separate
``.gcda`` file is created for each object file.

The purpose of **scons-tool-gcccov** is to help to incorporate the above gcov
files into project's dependency tree. Thanks to this, builders that depend on
coverage data (for example gcov report builders or test runners) may be
executed at right moments. This also helps to clean-up coverage data when the
project gets cleaned up.

Installation
------------

There are few ways to install this tool for your project.

From pypi_
^^^^^^^^^^

This method may be preferable if you build your project under a virtualenv. To
add gcccov tool from pypi_, type (within your wirtualenv):

.. code-block:: shell

   pip install scons-tool-loader scons-tool-gcccov

or, if your project uses pipenv_:

.. code-block:: shell

   pipenv install --dev scons-tool-loader scons-tool-gcccov

Alternatively, you may add this to your ``Pipfile``

.. code-block::

   [dev-packages]
   scons-tool-loader = "*"
   scons-tool-gcccov = "*"


The tool will be installed as a namespaced package ``sconstool.gcccov``
in project's virtual environment. You may further use scons-tool-loader_
to load the tool.

As a git submodule
^^^^^^^^^^^^^^^^^^

#. Create new git repository:

   .. code-block:: shell

      mkdir /tmp/prj && cd /tmp/prj
      touch README.rst
      git init

#. Add the `scons-tool-gcccov`_ as a submodule:

   .. code-block:: shell

      git submodule add git://github.com/ptomulik/scons-tool-gcccov.git site_scons/site_tools/gcccov

#. For python 2.x create ``__init__.py`` in ``site_tools`` directory:

   .. code-block:: shell

      touch site_scons/site_tools/__init__.py

   this will allow to directly import ``site_tools.gcccov`` (this may be required by other tools).

Other projects
^^^^^^^^^^^^^^

#. Download and copy this source tree to ``site_scons/site_tools/gcccov/``
   subdirectory of your project:

   .. code-block:: shell

      mkdir -p site_scons/site_tools/gcccov && \
        (cd site_scons/site_tools/gcccov && \
          curl -L https://github.com/ptomulik/scons-tool-gcccov/tarball/master | \
          tar --strip-components=1 -xz)

Usage
-----

Simple project with variant build and one shared library
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

#. Create some source files, for example ``src/main.c`` and ``src/bar.c``:

   .. code-block:: cpp

      // src/main.c
      extern int bar();
      int main(int argc, char *argv[])
      {
        return bar();
      }

   .. code-block:: cpp

      // src/bar.c
      int bar()
      {
        return 0;
      }

#. Write the top level ``SConstruct`` file:

   .. code-block:: python

      # SConstruct
      env = Environment(tools = ['default', 'gcccov'])
      # Generate correct dependencies of `*.gcno' and `*.gcda' files on object
      # files being built from now on.
      env.GCovInjectObjectEmitters()
      env.Replace(CCFLAGS = ['-g', '-O0', '--coverage'], LINKFLAGS = ['--coverage'])
      SConscript('src/SConscript', variant_dir = 'build', duplicate = 0, exports = [ 'env' ])

#. Write ``src/SConscript``:

   .. code-block:: python

      # src/SConscript
      Import(['env'])
      bar = env.SharedLibrary(['bar'], ['bar.c'])
      pro = env.Program('main.c', LIBS = ['bar'], LIBPATH = ['.'])
      run = env.Action("LD_LIBRARY_PATH=%s %s" % (env.Dir('.').path, pro[0].path))
      env.Alias('check', pro, run)
      env.AlwaysBuild('check')

#. Try it out, first we run pure build:

   .. code-block:: shell

       ptomulik@barakus:$ scons -Q
       gcc -o build/bar.os -c -g -O0 --coverage -fPIC src/bar.c
       gcc -o build/libbar.so --coverage -shared build/bar.os
       gcc -o build/main.o -c -g -O0 --coverage src/main.c
       gcc -o build/main --coverage build/main.o -Lbuild -Lsrc -lbar

   Note the ``*.gcno`` files generated under ``build/`` directory:

   .. code-block:: shell

      ptomulik@barakus:$ ls build/*.gc*
      build/bar.gcno  build/main.gcno

   Now, cleanup project:

   .. code-block:: shell

      ptomulik@barakus:$ scons -Q -c
      Removed build/bar.os
      Removed build/bar.gcno
      Removed build/libbar.so
      Removed build/main.o
      Removed build/main.gcno
      Removed build/main

   Note the ``*.gcno`` files get cleaned as well. Now we'll build and run test
   program:

   .. code-block:: shell

      ptomulik@barakus:$ scons -Q check
      gcc -o build/main.o -c -g -O0 --coverage src/main.c
      gcc -o build/bar.os -c -g -O0 --coverage -fPIC src/bar.c
      gcc -o build/libbar.so --coverage -shared build/bar.os
      gcc -o build/main --coverage build/main.o -Lbuild -Lsrc -lbar
      LD_LIBRARY_PATH=build build/main

   and list the coverage files again:

   .. code-block:: shell

      ptomulik@barakus:$ ls build/*.gc*
      build/bar.gcda  build/bar.gcno  build/main.gcda  build/main.gcno

   Cleanup the project again:

   .. code-block:: shell

      ptomulik@barakus:$ scons -Q -c
      Removed build/bar.os
      Removed build/bar.gcno
      Removed build/bar.gcda
      Removed build/libbar.so
      Removed build/main.o
      Removed build/main.gcno
      Removed build/main.gcda
      Removed build/main

   as you see, the ``*.gcda`` files get cleaned as well.

Integrating with cxxtest_
^^^^^^^^^^^^^^^^^^^^^^^^^

In this example we create a simple test runner using cxxtest_ suite. To drive
everything from SCons_, we'll use a scons-tool-cxxtest_ tool derived from the
original SCons tool available in cxxtest_ repository.

#. Install cxxtest_ framework:

   .. code-block:: shell

      sudo apt-get install cxxtest

#. Create new git repository:

   .. code-block:: shell

      mkdir /tmp/prj && cd /tmp/prj
      touch README.rst
      git init

#. Add **scons-tool-gcccov** as submodule:

   .. code-block:: shell

      git submodule add git://github.com/ptomulik/scons-tool-gcccov.git site_scons/site_tools/gcccov

#. Add scons-tool-cxxtest_ tool as submodule:

   .. code-block:: shell

      git submodule add git://github.com/ptomulik/scons-tool-cxxtest.git site_scons/site_tools/cxxtest

#. Create source file ``src/bar.cpp``:

   .. code-block:: cpp

      // src/bar.cpp
      int bar()
      {
        return 0;
      }

#. Create test file ``src/test.t.h``

   .. code-block:: cpp

      // src/test.t.h
      #include <cxxtest/TestSuite.h>

      extern int bar();
      class BarTestSuite1 : public CxxTest::TestSuite
      {
      public:
          void testBar(void)
          {
              TS_ASSERT_EQUALS(bar(), 0);
          }
      };

#. Write the top level ``SConstruct`` file:

   .. code-block:: python

      # SConstruct
      import os
      env = Environment(ENV = os.environ, tools = ['default', 'cxxtest', 'gcccov'])
      # Generate correct dependencies of `*.gcno' and `*.gcda' files on object
      # files being built from now on.
      env.GCovInjectObjectEmitters()
      env.Replace(CCFLAGS = ['-g', '-O0', '--coverage'], LINKFLAGS = ['--coverage'])
      SConscript('src/SConscript', variant_dir = 'build', duplicate = 0, exports = [ 'env' ])

#. Write ``src/SConscript``:

   .. code-block:: python

      # src/SConscript
      Import(['env'])
      bar = env.SharedLibrary(['bar'], ['bar.cpp'])
      env.CxxTest('test.t.h', LIBS = bar)

#. Try it out:

   .. code-block:: shell

      ptomulik@barakus:$ LD_LIBRARY_PATH=build scons -Q check
      Loading CxxTest tool...
      /usr/bin/python /usr/bin/cxxtestgen --runner=ErrorPrinter -o build/test.cpp src/test.t.h
      g++ -o build/test.o -c -g -O0 --coverage -I. build/test.cpp
      g++ -o build/bar.os -c -g -O0 --coverage -fPIC src/bar.cpp
      g++ -o build/libbar.so --coverage -shared build/bar.os
      g++ -o build/test --coverage build/test.o -Lbuild -Lsrc -lbar
      /tmp/prj/build/test
      Running cxxtest tests (1 test).OK!

#. Check the gcov_ files created:

   .. code-block:: shell

      ptomulik@barakus:$ ls build/*.gc*
      build/bar.gcda  build/bar.gcno  build/test.gcda  build/test.gcno

#. Cleanup project:

   .. code-block:: shell

      ptomulik@barakus:$ scons -Q -c
      Loading CxxTest tool...
      Removed build/bar.os
      Removed build/bar.gcno
      Removed build/bar.gcda
      Removed build/libbar.so
      Removed build/test.cpp
      Removed build/test.o
      Removed build/test.gcno
      Removed build/test.gcda
      Removed build/test

   As you see, all the generated gcov_ side effects are cleaned up as expected.

Finding out ``*.gcda`` files generated by a program run
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you need a list of ``*.gcda`` files generated when a program built with
SCons is executed, you may use ``GCovFindGcdaNodes``:

  .. code-block:: python

      prog = env.Program('foo.c')
      gcda = env.GCovFindGcdaNodes(prog[0])

This method is kinda dangerous and may break some builds. It internally scans
for dependencies, and this is done at the time the SConscript file is
processed. This may cause a problem with .sconsing file being written to wrong
directory. More details are given in `this thread
<http://scons.tigris.org/ds/viewMessage.do?dsForumId=1272&dsMessageId=2411741>`_.

As a conclusion I would say, that you should not use it in normal workflow.
However, it may be handy for development, code maintenance and such. For these
purposes I would suggest to add special CLI options or targets to your SCons
script, to use it only when explicitly requested.

Module description
------------------

The scons-tool-gcccov tool provides three methods:

- ``env.GCovInjectObjectEmitters(**overrides)``,
- ``env.GCovFindGcdaNodes(root)``,
- ``env.GCovGcdaGenerator(target, target_factory=_null, **overrides)``.

The first method, ``GCovInjectObjectEmitters`` is the only you'll need in most
projects. It injects special emitter to builders which create C/C++ object
files such that their corresponding ``*.gcno`` and ``*.gcda`` files get added
to dependency tree. The method should be invoked somewhere on the top of your
SConstruct, before you specify first C/C++ file to be compiled. For example,
this is incorrect:

  .. code-block:: python

      # SConstruct
      env.Program('foo')
      env.GCovInjectObjectEmitters()

and this is correct:

  .. code-block:: python

      # SConstruct
      env.GCovInjectObjectEmitters()
      env.Program('foo')

The remaining two methods should not be used in normal workflow. The
``GCovFindGcdaNodes`` determines what ``*.gcda`` files would be generated when
running certain program(s) built with SCons. The ``GCovGcdaGenerator(alias)``
tells SCons that ``alias`` target generates these ``*.gcda`` files as a side
effect (the alias should run a program/test runner and should have the program
in its dependencies). The method should not be used currently, however, as it
may break some builds, see `this thread
<http://scons.tigris.org/ds/viewMessage.do?dsForumId=1272&dsMessageId=2411741>`_.
Currently it's here only for experiments.

Construction variables
^^^^^^^^^^^^^^^^^^^^^^

The tool uses construction variables listed in the table below:

========================= ==================================================================================
 Option                    Description
========================= ==================================================================================
 GCCCOV_DISABLE            Disable gcccov functionality.
 GCCCOV_EXCLUDE            Files (``*.gcno``, ``*.gcda``, objects, etc.) to be excluded from processing.
 GCCCOV_GCDA_SUFFIX        Suffix for ``*.gcda`` files used by gcov dependency machinery.
 GCCCOV_GCNO_SUFFIX        Suffix for ``*.gcno`` files used by gcov dependency machinery.
 GCCCOV_MAX_RECURSION      Maximum recursion depth allowed when searching for ``*.gcda`` nodes.
 GCCCOV_NOCLEAN            List of gcov files which shouldn't be Cleaned up.
 GCCCOV_NOIGNORE           List of gcov files which shouldn't be Ignored from main target.
 GCCCOV_RUNTEST_FACTORY    Factory used to build runtest target (defaults to env.ans.Alias)
 GCCCOV_RUNTEST_TARGETS    List of targets (usually aliases) that run test runners.
 GCCCOV_SOURCE_SUFFIXES    List of source file suffixes for which dependency injector should be enabled.
========================= ==================================================================================

GENERATING DOCUMENTATION
------------------------

API DOCUMENTATION
^^^^^^^^^^^^^^^^^

You need few prerequisites to generate API documentation:

- epydoc_,
- python-docutils_,
- python-pygments_.

Install them with

.. code-block:: shell

   sudo apt-get install python-epydoc python-docutils python-pygments

The API documentation may be generated with:

.. code-block:: shell

   scons api-doc

The resultant html files get written to ``build/doc/api`` directory.



LICENSE
-------

Copyright (c) 2014-2020 by Paweł Tomulik <ptomulik@meil.pw.edu.pl>

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

.. <!-- Links -->
.. _SCons: http://scons.org
.. _gcov: http://gcc.gnu.org/onlinedocs/gcc/Gcov.html
.. _gcc: http://gcc.gnu.org/
.. _clang: http://clang.llvm.org/
.. _gcov files: http://gcc.gnu.org/onlinedocs/gcc/Gcov-Data-Files.html#Gcov-Data-Files
.. _cxxtest: http://cxxtest.com
.. _scons-tool-gcccov: https://github.com/ptomulik/scons-tool-gcccov
.. _scons-tool-cxxtest: https://github.com/ptomulik/scons-tool-cxxtest
.. _scons-tool-loader: https://github.com/ptomulik/scons-tool-loader
.. _epydoc: http://epydoc.sourceforge.net/
.. _python-docutils: http://pypi.python.org/pypi/docutils
.. _python-pygments: http://pygments.org/
.. _pipenv: https://pipenv.readthedocs.io/
.. _pypi: https://pypi.org/

.. <!--- vim: set expandtab tabstop=2 shiftwidth=2 syntax=rst: -->
