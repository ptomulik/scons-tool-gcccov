scons-tool-gcccov
=================

.. image:: https://travis-ci.org/ptomulik/scons-tool-gcccov.png?branch=master   :target: https://travis-ci.org/ptomulik/scons-tool-gcccov

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

Git-based projects
^^^^^^^^^^^^^^^^^^

#. Create new git repository::

      mkdir /tmp/prj && cd /tmp/prj
      touch README.rst
      git init

#. Add **scons-tool-gcccov** as submodule::

      git submodule add git://github.com/ptomulik/scons-tool-gcccov.git site_scons/site_tools/gcccov

Usage
-----

Simple project with variant build and one shared library
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

#. Create some source files, for example ``src/main.c`` and ``src/foo.c``:

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

      # Generate correct dependencies of `*.gcda` files on test runner.
      env.GCovInjectRuntestSideEffects('check')

#. Write ``src/SConscript``:

   .. code-block:: python

      # src/SConscript                                                          
      Import(['env'])                                                           
      bar = env.SharedLibrary(['bar'], ['bar.c'])                                         
      pro = env.Program('main.c', LIBS = bar)                  
      run = env.Action("LD_LIBRARY_PATH=%s %s" % (env.Dir('.').path, pro[0].path))
      env.Alias('check', pro, run)
      env.AlwaysBuild('check')

#. Try it out, first we run pure build

   .. code-block::

       ptomulik@barakus:$ scons -Q
       gcc -o build/bar.os -c -g -O0 --coverage -fPIC src/bar.c
       gcc -o build/libbar.so --coverage -shared build/bar.os
       gcc -o build/main.o -c -g -O0 --coverage src/main.c
       gcc -o build/main --coverage build/main.o -Lbuild -Lsrc -lbar

   Note the ``*.gcno`` files generated under ``build/`` directory:

   .. code-block::
      
      ptomulik@barakus:$ ls build/*.gc*
      build/bar.gcno  build/main.gcno

   Now, cleanup project:

   .. code-block::

      ptomulik@barakus:$ scons -Q -c
      Removed build/bar.os
      Removed build/bar.gcno
      Removed build/libbar.so
      Removed build/main.o
      Removed build/main.gcno
      Removed build/main

   Note the ``*.gcno`` files get cleaned as well. Now we'll build and run test
   program:

   .. code-block::

      ptomulik@barakus:$ scons -Q check
      gcc -o build/main.o -c -g -O0 --coverage src/main.c
      gcc -o build/bar.os -c -g -O0 --coverage -fPIC src/bar.c
      gcc -o build/libbar.so --coverage -shared build/bar.os
      gcc -o build/main --coverage build/main.o -Lbuild -Lsrc -lbar
      LD_LIBRARY_PATH=build build/main

   and list the coverage files again:

   .. code-block::
      
      ptomulik@barakus:$ ls build/*.gc*
      build/bar.gcda  build/bar.gcno  build/main.gcda  build/main.gcno

   Cleanup the project again:

   .. code-block::

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

Module description
------------------

Construction variables
^^^^^^^^^^^^^^^^^^^^^^

======================= ==================================================================================
 Option                    Description
======================= ==================================================================================
 GCOV_DISABLE            Disable gcov dependency injector.
 GCOV_EXCLUDE            Files (``*.gcno``, ``*.gcda`` and objects) to be excluded from processing.
 GCOV_GCDA_SUFFIX        Suffix for ``*.gcno`` files used by gcov dependency machinery.
 GCOV_GCNO_SUFFIX        Suffix for ``*.gcno`` files used by gcov dependency machinery.
 GCOV_SUFFIX             Suffix for ``*.gcov`` files produced by gcov_ tool.
 GCOV_MAX_RECURSION
 GCOV_NOCLEAN            List of gcov files which shouldn't be cleaned up.
 GCOV_NOIGNORE
 GCOV_RUNTEST_FACTORY    Factory used to build runtest target (defaults to env.ans.Alias)
 GCOV_RUNTEST_TARGETS    List of targets (usually aliases) that run test runners.
 GCOV_SOURCE_SUFFIXES    List of source file suffixes for which dependency injector should be enabled.
======================= ==================================================================================

GENERATING DOCUMENTATION
------------------------

TODO:

TESTING
-------

To run tests you first need to download testsuite framework to the local source
tree::

    ./bin/download-test-framework.sh

Running all tests is as simple as::

    SCONS_EXTERNAL_TEST=1 python runtest.py -a

LICENSE
-------

Copyright (c) 2014 by Pawel Tomulik <ptomulik@meil.pw.edu.pl>

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

.. <!--- vim: set expandtab tabstop=2 shiftwidth=2 syntax=rst: -->
