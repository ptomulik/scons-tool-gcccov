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
TODO: write documentation here
"""

import sys
import TestSCons

if sys.platform == 'win32':
    test = TestSCons.TestSCons(program='scons.bat', interpreter=None)
else:
    test = TestSCons.TestSCons()


##############################################################################
# Initialization test 1
##############################################################################
test.subdir(['t1'])
test.subdir(['t1', 'site_scons'])
test.subdir(['t1', 'site_scons', 'site_tools'])
test.subdir(['t1', 'site_scons', 'site_tools', 'gcccov'])
test.dir_fixture('../../../..', 't1/site_scons/site_tools/gcccov')
test.write( ['t1', 'SConstruct'],
"""
env = Environment( tools = ["default", "gcccov"] )
""")
test.run(chdir = 't1')

##############################################################################
# Initialization test 2
##############################################################################
test.subdir(['t2'])
test.subdir(['t2', 'site_scons'])
test.subdir(['t2', 'site_scons', 'site_tools'])
test.subdir(['t2', 'site_scons', 'site_tools', 'gcccov'])
test.dir_fixture('../../../..', 't2/site_scons/site_tools/gcccov')
test.write( ['t2', 'SConstruct'],
"""
env = Environment( tools = ["gcccov"] )
""")
test.run(chdir = 't2')

##############################################################################
# Initialization test 3
##############################################################################
test.subdir(['t3'])
test.subdir(['t3', 'site_scons'])
test.subdir(['t3', 'site_scons', 'site_tools'])
test.subdir(['t3', 'site_scons', 'site_tools', 'gcccov'])
test.dir_fixture('../../../..', 't3/site_scons/site_tools/gcccov')
test.write( ['t3', 'SConstruct'],
"""
env = Environment( tools = [] )
env.Tool('gcccov')
""")
test.run(chdir = 't3')

test.pass_test()

# Local Variables:
# # tab-width:4
# # indent-tabs-mode:nil
# # End:
# vim: set syntax=python expandtab tabstop=4 shiftwidth=4:
