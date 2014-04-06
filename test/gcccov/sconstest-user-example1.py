#! /usr/bin/env python
#
# Copyright (c) 2014 by Pawel Tomulik
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
TODO: write documentation here
"""

import TestSCons

##############################################################################
#  User example 1 from README.rst
##############################################################################
test = TestSCons.TestSCons()
test.subdir(['ex1'])
test.subdir(['ex1', 'src'])
test.dir_fixture('../..', 'ex1/site_scons/site_tools/gcccov')
test.write( ['ex1', 'src', 'main.c'], 
"""
// src/main.c
extern int bar();
int main(int argc, char *argv[])
{
      return bar();
}
""")
test.write( ['ex1', 'src', 'bar.c'], 
"""
// src/bar.c
int bar()
{
      return 0;
}
""")
test.write( ['ex1', 'src', 'SConscript'], 
"""
# src/SConscript
Import(['env'])
bar = env.SharedLibrary(['bar'], ['bar.c'])
pro = env.Program('main.c', LIBS = ['bar'], LIBPATH = ['.'])
run = env.Action("LD_LIBRARY_PATH=%s %s" % (env.Dir('.').path, pro[0].path))
env.Alias('check', pro, run)
env.AlwaysBuild('check')
""")
test.write( ['ex1', 'SConstruct'],
"""
# SConstruct
env = Environment(tools = ['default', 'gcccov'])
# Generate correct dependencies of `*.gcno' and `*.gcda' files on object
# files being built from now on.
env.GCovInjectObjectEmitters()
env.Replace(CCFLAGS = ['-g', '-O0', '--coverage'], LINKFLAGS = ['--coverage'])
SConscript('src/SConscript', variant_dir = 'build', duplicate = 0, exports = [ 'env' ])
""")
test.run(chdir = 'ex1', arguments = ['-Q'])
test.must_exist(['ex1','build','bar.gcno'])
test.must_exist(['ex1','build','main.gcno'])
test.must_not_exist(['ex1','build','bar.gcda'])
test.must_not_exist(['ex1','build','main.gcda'])

test.run(chdir = 'ex1', arguments = ['-Q','-c'])
test.must_not_exist(['ex1','build','bar.gcno'])
test.must_not_exist(['ex1','build','main.gcno'])
test.must_not_exist(['ex1','build','bar.gcda'])
test.must_not_exist(['ex1','build','main.gcda'])

test.run(chdir = 'ex1', arguments = ['-Q', 'check'])
test.must_exist(['ex1','build','bar.gcno'])
test.must_exist(['ex1','build','main.gcno'])
test.must_exist(['ex1','build','bar.gcda'])
test.must_exist(['ex1','build','main.gcda'])

test.run(chdir = 'ex1', arguments = ['-Q','-c'])
test.must_not_exist(['ex1','build','bar.gcno'])
test.must_not_exist(['ex1','build','main.gcno'])
test.must_not_exist(['ex1','build','bar.gcda'])
test.must_not_exist(['ex1','build','main.gcda'])


# Local Variables:
# # tab-width:4
# # indent-tabs-mode:nil
# # End:
# vim: set syntax=python expandtab tabstop=4 shiftwidth=4:
