#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (c) 2014-2020 by Paweł Tomulik
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE

__docformat__ = "restructuredText"


"""
Ensure that GCovInjectObjectEmitters() works.
"""

import TestSCons
import sys
import os

_exe = TestSCons._exe

##############################################################################
#  GCovInjectObjectEmitters() with default settings
##############################################################################
if sys.platform == 'win32':
    test = TestSCons.TestSCons(program='scons.bat', interpreter=None)
else:
    test = TestSCons.TestSCons()

if sys.platform == 'win32':
    gcc = test.where_is('gcc')
    if not gcc:
        test.skip_test('gcc not found. Skipping test...\n')
    _env_args_ = "tools=['mingw', 'gcccov'], ENV={'TEMP':'.', 'PATH': %r}" % os.environ['PATH']
    _shobj = '.o'
else:
    _env_args_ = "tools=['default', 'gcccov']"
    _shobj = '.os'


test.subdir(['t1'])
test.subdir(['t1', 'site_scons'])
test.subdir(['t1', 'site_scons', 'site_tools'])
test.subdir(['t1', 'site_scons', 'site_tools', 'gcccov'])
test.dir_fixture('../../../..', 't1/site_scons/site_tools/gcccov')
test.write( ['t1', 'SConstruct'],
"""
import SCons.Builder
env = Environment( %(_env_args_)s )
env.GCovInjectObjectEmitters()
for bn in ['Object', 'StaticObject', 'SharedObject']:
    builder = env['BUILDERS'][bn].builder
    suffixes = list(set(builder.emitter.keys()) & set(env['GCCCOV_OBJECT_BUILDERS']))
    for sfx in suffixes:
        emitter = builder.emitter[sfx]
        try:
            emitter.original_emitter
        except AttributeError:
            raise RuntimeError("%%r emitter for suffix %%r is %%r and has no original_emitter attribute!!!" %% (bn,sfx,emitter))
""" % locals())
test.run(chdir = 't1')

##############################################################################
#  GCovInjectObjectEmitters() with env['GCCCOV_OBJECT_BUILDERS'] = []
##############################################################################
if sys.platform == 'win32':
    test = TestSCons.TestSCons(program='scons.bat', interpreter=None)
else:
    test = TestSCons.TestSCons()
test.subdir(['t2'])
test.subdir(['t2', 'site_scons'])
test.subdir(['t2', 'site_scons', 'site_tools'])
test.subdir(['t2', 'site_scons', 'site_tools', 'gcccov'])
test.dir_fixture('../../../..', 't2/site_scons/site_tools/gcccov')
test.write( ['t2', 'SConstruct'],
"""
import SCons.Builder
env = Environment( %(_env_args_)s )
env['GCCCOV_OBJECT_BUILDERS'] = []
env.GCovInjectObjectEmitters()
for bn in ['Object', 'StaticObject', 'SharedObject']:
    builder = env['BUILDERS'][bn].builder
    for (sfx,emitter) in builder.emitter.items():
        try:
            emitter.original_emitter
        except AttributeError:
            pass
        else:
            raise RuntimeError("%%r emitter for suffix %%r is %%r and has original_emitter attribute!!!" %% (bn,sfx,emitter))
""" % locals())
test.run(chdir = 't2')

##############################################################################
#  GCovInjectObjectEmitters() with env['GCCCOV_OBJECT_BUILDERS'] = None
##############################################################################
if sys.platform == 'win32':
    test = TestSCons.TestSCons(program='scons.bat', interpreter=None)
else:
    test = TestSCons.TestSCons()
test.subdir(['t3'])
test.subdir(['t3', 'site_scons'])
test.subdir(['t3', 'site_scons', 'site_tools'])
test.subdir(['t3', 'site_scons', 'site_tools', 'gcccov'])
test.dir_fixture('../../../..', 't3/site_scons/site_tools/gcccov')
test.write( ['t3', 'SConstruct'],
"""
import SCons.Builder
env = Environment( %(_env_args_)s )
env['GCCCOV_OBJECT_BUILDERS'] = None
env.GCovInjectObjectEmitters()
for bn in ['Object', 'StaticObject', 'SharedObject']:
    builder = env['BUILDERS'][bn].builder
    for (sfx,emitter) in builder.emitter.items():
        try:
            emitter.original_emitter
        except AttributeError:
            pass
        else:
            raise RuntimeError("%%r emitter for suffix %%r is %%r and has original_emitter attribute!!!" %% (bn,sfx,emitter))
""" % locals())
test.run(chdir = 't3')

##############################################################################
#  GCovInjectObjectEmitters() with env['GCCCOV_OBJECT_BUILDERS'] undefined
##############################################################################
if sys.platform == 'win32':
    test = TestSCons.TestSCons(program='scons.bat', interpreter=None)
else:
    test = TestSCons.TestSCons()
test.subdir(['t4'])
test.subdir(['t4', 'site_scons'])
test.subdir(['t4', 'site_scons', 'site_tools'])
test.subdir(['t4', 'site_scons', 'site_tools', 'gcccov'])
test.dir_fixture('../../../..', 't4/site_scons/site_tools/gcccov')
test.write( ['t4', 'SConstruct'],
"""
import SCons.Builder
env = Environment( %(_env_args_)s )
del(env['GCCCOV_OBJECT_BUILDERS'])
env.GCovInjectObjectEmitters()
for bn in ['Object', 'StaticObject', 'SharedObject']:
    builder = env['BUILDERS'][bn].builder
    for (sfx,emitter) in builder.emitter.items():
        try:
            emitter.original_emitter
        except AttributeError:
            pass
        else:
            raise RuntimeError("%%r emitter for suffix %%r is %%r and has original_emitter attribute!!!" %% (bn,sfx,emitter))
""" % locals())
test.run(chdir = 't4')

##############################################################################
#  GCovInjectObjectEmitters() with GCCCOV_OBJECT_BUILDERS = ['SharedObject']
##############################################################################
if sys.platform == 'win32':
    test = TestSCons.TestSCons(program='scons.bat', interpreter=None)
else:
    test = TestSCons.TestSCons()
test.subdir(['t5'])
test.subdir(['t5', 'site_scons'])
test.subdir(['t5', 'site_scons', 'site_tools'])
test.subdir(['t5', 'site_scons', 'site_tools', 'gcccov'])
test.dir_fixture('../../../..', 't5/site_scons/site_tools/gcccov')
test.write( ['t5', 'SConstruct'],
"""
import SCons.Builder
env = Environment( %(_env_args_)s )
env.GCovInjectObjectEmitters(GCCCOV_OBJECT_BUILDERS = ['SharedObject'])
for bn in ['SharedObject']:
    builder = env['BUILDERS'][bn].builder
    suffixes = list(set(builder.emitter.keys()) & set(env['GCCCOV_OBJECT_BUILDERS']))
    for sfx in suffixes:
        emitter = builder.emitter[sfx]
        try:
            emitter.original_emitter
        except AttributeError:
            raise RuntimeError("%%r emitter for suffix %%r is %%r and has no original_emitter attribute!!!" %% (bn,sfx,emitter))
for bn in ['Object', 'StaticObject']:
    builder = env['BUILDERS'][bn].builder
    for (sfx,emitter) in builder.emitter.items():
        try:
            emitter.original_emitter
        except AttributeError:
            pass
        else:
            raise RuntimeError("%%r emitter for suffix %%r is %%r and has original_emitter attribute!!!" %% (bn,sfx,emitter))
""" % locals())
test.run(chdir = 't5')

##############################################################################
#  GCovInjectObjectEmitters() with GCCCOV_OBJECT_BUILDERS = []
##############################################################################
if sys.platform == 'win32':
    test = TestSCons.TestSCons(program='scons.bat', interpreter=None)
else:
    test = TestSCons.TestSCons()
test.subdir(['t6'])
test.subdir(['t6', 'site_scons'])
test.subdir(['t6', 'site_scons', 'site_tools'])
test.subdir(['t6', 'site_scons', 'site_tools', 'gcccov'])
test.dir_fixture('../../../..', 't6/site_scons/site_tools/gcccov')
test.write( ['t6', 'SConstruct'],
"""
import SCons.Builder
env = Environment( %(_env_args_)s )
env.GCovInjectObjectEmitters(GCCCOV_OBJECT_BUILDERS = [])
for bn in ['Object', 'StaticObject', 'SharedObject']:
    builder = env['BUILDERS'][bn].builder
    for (sfx,emitter) in builder.emitter.items():
        try:
            emitter.original_emitter
        except AttributeError:
            pass
        else:
            raise RuntimeError("%%r emitter for suffix %%r is %%r and has original_emitter attribute!!!" %% (bn,sfx,emitter))
""" % locals())
test.run(chdir = 't6')

##############################################################################
#  GCovInjectObjectEmitters() with GCCCOV_OBJECT_BUILDERS = None
##############################################################################
if sys.platform == 'win32':
    test = TestSCons.TestSCons(program='scons.bat', interpreter=None)
else:
    test = TestSCons.TestSCons()
test.subdir(['t7'])
test.subdir(['t7', 'site_scons'])
test.subdir(['t7', 'site_scons', 'site_tools'])
test.subdir(['t7', 'site_scons', 'site_tools', 'gcccov'])
test.dir_fixture('../../../..', 't7/site_scons/site_tools/gcccov')
test.write( ['t7', 'SConstruct'],
"""
import SCons.Builder
env = Environment( %(_env_args_)s )
env.GCovInjectObjectEmitters(GCCCOV_OBJECT_BUILDERS = None)
for bn in ['Object', 'StaticObject', 'SharedObject']:
    builder = env['BUILDERS'][bn].builder
    for (sfx,emitter) in builder.emitter.items():
        try:
            emitter.original_emitter
        except AttributeError:
            pass
        else:
            raise RuntimeError("%%r emitter for suffix %%r is %%r and has original_emitter attribute!!!" %% (bn,sfx,emitter))
""" % locals())
test.run(chdir = 't7')

##############################################################################
#  Build an Object file and check if it has *.gcno side effect
##############################################################################
if sys.platform == 'win32':
    test = TestSCons.TestSCons(program='scons.bat', interpreter=None)
else:
    test = TestSCons.TestSCons()
test.subdir(['t8'])
test.subdir(['t8', 'site_scons'])
test.subdir(['t8', 'site_scons', 'site_tools'])
test.subdir(['t8', 'site_scons', 'site_tools', 'gcccov'])
test.dir_fixture('../../../..', 't8/site_scons/site_tools/gcccov')
test.write( ['t8', 'foo.c' ],
"""
int foo() { return 0; }
""")
test.write( ['t8', 'SConstruct'],
"""
import SCons.Builder
env = Environment( %(_env_args_)s )
env.GCovInjectObjectEmitters()
obj = env.Object('foo')
gcno = env.File('foo.gcno')
if obj[0] not in gcno.all_children():
    raise RuntimeError("'%%s' should be a child of '%%s'" %% (obj[0],gcno))
""" % locals())
test.run(chdir = 't8')
test.must_exist(['t8','foo.o'])

##############################################################################
#  Build a SharedObject file and check if it has *.gcno side effect
##############################################################################
if sys.platform == 'win32':
    test = TestSCons.TestSCons(program='scons.bat', interpreter=None)
else:
    test = TestSCons.TestSCons()
test.subdir(['t9'])
test.subdir(['t9', 'site_scons'])
test.subdir(['t9', 'site_scons', 'site_tools'])
test.subdir(['t9', 'site_scons', 'site_tools', 'gcccov'])
test.dir_fixture('../../../..', 't9/site_scons/site_tools/gcccov')
test.write( ['t9', 'foo.c' ],
"""
int foo() { return 0; }
""")
test.write( ['t9', 'SConstruct'],
"""
import SCons.Builder
env = Environment( %(_env_args_)s )
env.GCovInjectObjectEmitters()
obj = env.SharedObject('foo')
gcno = env.arg2nodes('foo.gcno')
if obj[0] not in gcno[0].all_children():
    raise RuntimeError("'%%s' should be a child of '%%s'" %% (obj[0],gcno[0]))
if not gcno[0].side_effect:
    raise RuntimeError("'%%s' should be a side effect of '%%s'" %% (gcno[0],obj[0]))
""" % locals())
test.run(chdir = 't9')
test.must_exist(['t9','foo%s' % _shobj])

##############################################################################
#  Build multiple Object files and check if each one has *.gcno side effect
##############################################################################
if sys.platform == 'win32':
    test = TestSCons.TestSCons(program='scons.bat', interpreter=None)
else:
    test = TestSCons.TestSCons()
test.subdir(['tA'])
test.subdir(['tA', 'site_scons'])
test.subdir(['tA', 'site_scons', 'site_tools'])
test.subdir(['tA', 'site_scons', 'site_tools', 'gcccov'])
test.dir_fixture('../../../..', 'tA/site_scons/site_tools/gcccov')
test.write( ['tA', 'foo.c' ],
"""
int foo() { return 0; }
""")
test.write( ['tA', 'bar.c' ],
"""
int bar() { return 0; }
""")
test.write( ['tA', 'SConstruct'],
"""
import SCons.Builder
env = Environment( %(_env_args_)s )
env.GCovInjectObjectEmitters()
obj = env.Object(['foo','bar'])
gcno = env.arg2nodes(['foo.gcno', 'bar.gcno'])
for i in range(0,2):
    if obj[i] not in gcno[i].all_children():
        raise RuntimeError("'%%s' should be a child of '%%s'" %% (obj[i],gcno[i]))
    if not gcno[i].side_effect:
        raise RuntimeError("'%%s' should be a side effect of '%%s'" %% (gcno[i],obj[i]))
""" % locals())
test.run(chdir = 'tA')
test.must_exist(['tA','foo.o'])
test.must_exist(['tA','bar.o'])

##############################################################################
#  Build a Program and check if each object file has *.gcno side effect
##############################################################################
if sys.platform == 'win32':
    test = TestSCons.TestSCons(program='scons.bat', interpreter=None)
else:
    test = TestSCons.TestSCons()
test.subdir(['tB'])
test.subdir(['tB', 'site_scons'])
test.subdir(['tB', 'site_scons', 'site_tools'])
test.subdir(['tB', 'site_scons', 'site_tools', 'gcccov'])
test.dir_fixture('../../../..', 'tB/site_scons/site_tools/gcccov')
test.write( ['tB', 'foo.c' ],
"""
int bar();
int main(int argc, char* argv[])
{
  bar();
  return 0;
}
""")
test.write( ['tB', 'bar.c' ],
"""
int bar() { return 0; }
""")
test.write( ['tB', 'SConstruct'],
"""
import SCons.Builder
env = Environment( %(_env_args_)s )
env.GCovInjectObjectEmitters()
env.Program('foo', ['foo.c','bar.c'])
obj = env.arg2nodes(['foo.o', 'bar.o'])
gcno = env.arg2nodes(['foo.gcno', 'bar.gcno'])
for i in range(0,2):
    if obj[i] not in gcno[i].all_children():
        raise RuntimeError("'%%s' should be a child of '%%s'" %% (obj[i],gcno[i]))
    if not gcno[i].side_effect:
        raise RuntimeError("'%%s' should be a side effect of '%%s'" %% (gcno[i],obj[i]))
""" % locals())
test.run(chdir = 'tB')
test.must_exist(['tB','foo.o'])
test.must_exist(['tB','bar.o'])
test.must_exist(['tB','foo%s' % _exe])

test.pass_test()

# Local Variables:
# # tab-width:4
# # indent-tabs-mode:nil
# # End:
# vim: set syntax=python expandtab tabstop=4 shiftwidth=4:
