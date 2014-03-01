"""
TestCommon.py:  a testing framework for commands and scripts
                with commonly useful error handling

The TestCommon module provides a simple, high-level interface for writing
tests of executable commands and scripts, especially commands and scripts
that interact with the file system.  All methods throw exceptions and
exit on failure, with useful error messages.  This makes a number of
explicit checks unnecessary, making the test scripts themselves simpler
to write and easier to read.

The TestCommon class is a subclass of the TestCmd class.  In essence,
TestCommon is a wrapper that handles common TestCmd error conditions in
useful ways.  You can use TestCommon directly, or subclass it for your
program and add additional (or override) methods to tailor it to your
program's specific needs.  Alternatively, the TestCommon class serves
as a useful example of how to define your own TestCmd subclass.

As a subclass of TestCmd, TestCommon provides access to all of the
variables and methods from the TestCmd module.  Consequently, you can
use any variable or method documented in the TestCmd module without
having to explicitly import TestCmd.

A TestCommon environment object is created via the usual invocation:

    import TestCommon
    test = TestCommon.TestCommon()

You can use all of the TestCmd keyword arguments when instantiating a
TestCommon object; see the TestCmd documentation for details.

Here is an overview of the methods and keyword arguments that are
provided by the TestCommon class:

    test.must_be_writable('file1', ['file2', ...])

    test.must_contain('file', 'required text\n')

    test.must_contain_all_lines(output, lines, ['title', find])

    test.must_contain_any_line(output, lines, ['title', find])

    test.must_contain_exactly_lines(output, lines, ['title', find])

    test.must_exist('file1', ['file2', ...])

    test.must_match('file', "expected contents\n")

    test.must_not_be_writable('file1', ['file2', ...])

    test.must_not_contain('file', 'banned text\n')

    test.must_not_contain_any_line(output, lines, ['title', find])

    test.must_not_exist('file1', ['file2', ...])

    test.run(options = "options to be prepended to arguments",
             stdout = "expected standard output from the program",
             stderr = "expected error output from the program",
             status = expected_status,
             match = match_function)

The TestCommon module also provides the following variables

    TestCommon.python
    TestCommon._python_
    TestCommon.exe_suffix
    TestCommon.obj_suffix
    TestCommon.shobj_prefix
    TestCommon.shobj_suffix
    TestCommon.lib_prefix
    TestCommon.lib_suffix
    TestCommon.dll_prefix
    TestCommon.dll_suffix

"""

# Copyright 2000-2010 Steven Knight
# This module is free software, and you may redistribute it and/or modify
# it under the same terms as Python itself, so long as this copyright message
# and disclaimer are retained in their original form.
#
# IN NO EVENT SHALL THE AUTHOR BE LIABLE TO ANY PARTY FOR DIRECT, INDIRECT,
# SPECIAL, INCIDENTAL, OR CONSEQUENTIAL DAMAGES ARISING OUT OF THE USE OF
# THIS CODE, EVEN IF THE AUTHOR HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH
# DAMAGE.
#
# THE AUTHOR SPECIFICALLY DISCLAIMS ANY WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
# PARTICULAR PURPOSE.  THE CODE PROVIDED HEREUNDER IS ON AN "AS IS" BASIS,
# AND THERE IS NO OBLIGATION WHATSOEVER TO PROVIDE MAINTENANCE,
# SUPPORT, UPDATES, ENHANCEMENTS, OR MODIFICATIONS.

__author__ = "Steven Knight <knight at baldmt dot com>"
__revision__ = "TestCommon.py 1.3.D001 2010/06/03 12:58:27 knight"
__version__ = "1.3"

import copy
import os
import stat
import sys
import glob

try:
    from collections import UserList
except ImportError:
    # no 'collections' module or no UserList in collections
    exec('from UserList import UserList')

from TestCmd import *
from TestCmd import __all__

__all__.extend([ 'TestCommon',
                 'exe_suffix',
                 'obj_suffix',
                 'shobj_prefix',
                 'shobj_suffix',
                 'lib_prefix',
                 'lib_suffix',
                 'dll_prefix',
                 'dll_suffix',
               ])

try:
    sorted
except NameError:
    # Pre-2.4 Python has no sorted() function.
    #
    # The pre-2.4 Python list.sort() method does not support
    # list.sort(key=) nor list.sort(reverse=) keyword arguments, so
    # we must implement the functionality of those keyword arguments
    # by hand instead of passing them to list.sort().
    def sorted(iterable, cmp=None, key=None, reverse=False):
        if key is not None:
            result = [(key(x), x) for x in iterable]
        else:
            result = iterable[:]
        if cmp is None:
            # Pre-2.3 Python does not support list.sort(None).
            result.sort()
        else:
            result.sort(cmp)
        if key is not None:
            result = [t1 for t0,t1 in result]
        if reverse:
            result.reverse()
        return result

# Variables that describe the prefixes and suffixes on this system.
if sys.platform == 'win32':
    exe_suffix   = '.exe'
    obj_suffix   = '.obj'
    shobj_suffix = '.obj'
    shobj_prefix = ''
    lib_prefix   = ''
    lib_suffix   = '.lib'
    dll_prefix   = ''
    dll_suffix   = '.dll'
elif sys.platform == 'cygwin':
    exe_suffix   = '.exe'
    obj_suffix   = '.o'
    shobj_suffix = '.os'
    shobj_prefix = ''
    lib_prefix   = 'lib'
    lib_suffix   = '.a'
    dll_prefix   = 'cyg'
    dll_suffix   = '.dll'
elif sys.platform.find('irix') != -1:
    exe_suffix   = ''
    obj_suffix   = '.o'
    shobj_suffix = '.o'
    shobj_prefix = ''
    lib_prefix   = 'lib'
    lib_suffix   = '.a'
    dll_prefix   = 'lib'
    dll_suffix   = '.so'
elif sys.platform.find('darwin') != -1:
    exe_suffix   = ''
    obj_suffix   = '.o'
    shobj_suffix = '.os'
    shobj_prefix = ''
    lib_prefix   = 'lib'
    lib_suffix   = '.a'
    dll_prefix   = 'lib'
    dll_suffix   = '.dylib'
elif sys.platform.find('sunos') != -1:
    exe_suffix   = ''
    obj_suffix   = '.o'
    shobj_suffix = '.o'
    shobj_prefix = 'so_'
    lib_prefix   = 'lib'
    lib_suffix   = '.a'
    dll_prefix   = 'lib'
    dll_suffix   = '.so'
else:
    exe_suffix   = ''
    obj_suffix   = '.o'
    shobj_suffix = '.os'
    shobj_prefix = ''
    lib_prefix   = 'lib'
    lib_suffix   = '.a'
    dll_prefix   = 'lib'
    dll_suffix   = '.so'

def is_List(e):
    return isinstance(e, (list, UserList))

def is_Tuple(e):
    return isinstance(e, tuple)

def is_Sequence(e):
    return (not hasattr(e, "strip") and
            hasattr(e, "__getitem__") or
            hasattr(e, "__iter__"))

def is_writable(f):
    mode = os.stat(f)[stat.ST_MODE]
    return mode & stat.S_IWUSR

def separate_files(flist):
    existing = []
    missing = []
    for f in flist:
        if os.path.exists(f):
            existing.append(f)
        else:
            missing.append(f)
    return existing, missing

if os.name == 'posix':
    def _failed(self, status = 0):
        if self.status is None or status is None:
            return None
        return _status(self) != status
    def _status(self):
        return self.status
elif os.name == 'nt':
    def _failed(self, status = 0):
        return not (self.status is None or status is None) and \
               self.status != status
    def _status(self):
        return self.status

class TestCommon(TestCmd):

    # Additional methods from the Perl Test::Cmd::Common module
    # that we may wish to add in the future:
    #
    #  $test->subdir('subdir', ...);
    #
    #  $test->copy('src_file', 'dst_file');

    def __init__(self, **kw):
        """Initialize a new TestCommon instance.  This involves just
        calling the base class initialization, and then changing directory
        to the workdir.
        """
        TestCmd.__init__(self, **kw)
        os.chdir(self.workdir)

    def options_arguments(self, options, arguments):
        """Merges the "options" keyword argument with the arguments."""
        if options:
            if arguments is None:
                return options
            if isinstance(options, str):
                options = [options]
            if isinstance(arguments, str):
                arguments = [arguments]
            arguments = ' '.join(options + arguments)
        return arguments

    def must_be_writable(self, *files):
        """Ensures that the specified file(s) exist and are writable.
        An individual file can be specified as a list of directory names,
        in which case the pathname will be constructed by concatenating
        them.  Exits FAILED if any of the files does not exist or is
        not writable.
        """
        files = [is_List(x) and os.path.join(*x) or x for x in files]
        existing, missing = separate_files(files)
        unwritable = [x for x in existing if not is_writable(x)]
        if missing:
            print "Missing files: `%s'" % "', `".join(missing)
        if unwritable:
            print "Unwritable files: `%s'" % "', `".join(unwritable)
        self.fail_test(missing + unwritable)

    def must_contain(self, file, required, mode = 'rb', find = None):
        """Ensures that the specified file contains the required text.
        """
        file_contents = self.read(file, mode)
        if find is None:
            def find(o, l):
                try:
                    return o.index(l)
                except ValueError:
                    return None
        contains = find(file_contents, required)
        if not contains:
            print "File `%s' does not contain required string." % file
            print self.banner('Required string ')
            print required
            print self.banner('%s contents ' % file)
            print file_contents
            self.fail_test(not contains)

    def must_contain_all_lines(self, output, lines, title=None, find=None):
        """Ensures that the specified output string (first argument)
        contains all of the specified lines (second argument).

        An optional third argument can be used to describe the type
        of output being searched, and only shows up in failure output.

        An optional fourth argument can be used to supply a different
        function, of the form "find(line, output), to use when searching
        for lines in the output.
        """
        if find is None:
            def find(o, l):
                try:
                    return o.index(l)
                except ValueError:
                    return None
        missing = []
        if is_List(output):
            output = '\n'.join(output)

        for line in lines:
            if find(output, line) is None:
                missing.append(line)

        if missing:
            if title is None:
                title = 'output'
            sys.stdout.write("Missing expected lines from %s:\n" % title)
            for line in missing:
                sys.stdout.write('    ' + repr(line) + '\n')
            sys.stdout.write(self.banner(title + ' ') + '\n')
            sys.stdout.write(output)
            self.fail_test()

    def must_contain_any_line(self, output, lines, title=None, find=None):
        """Ensures that the specified output string (first argument)
        contains at least one of the specified lines (second argument).

        An optional third argument can be used to describe the type
        of output being searched, and only shows up in failure output.

        An optional fourth argument can be used to supply a different
        function, of the form "find(line, output), to use when searching
        for lines in the output.
        """
        if find is None:
            def find(o, l):
                try:
                    return o.index(l)
                except ValueError:
                    return None
        for line in lines:
            if find(output, line) is not None:
                return

        if title is None:
            title = 'output'
        sys.stdout.write("Missing any expected line from %s:\n" % title)
        for line in lines:
            sys.stdout.write('    ' + repr(line) + '\n')
        sys.stdout.write(self.banner(title + ' ') + '\n')
        sys.stdout.write(output)
        self.fail_test()

    def must_contain_exactly_lines(self, output, expect, title=None, find=None):
        """Ensures that the specified output string (first argument)
        contains all of the lines in the expected string (second argument)
        with none left over.

        An optional third argument can be used to describe the type
        of output being searched, and only shows up in failure output.

        An optional fourth argument can be used to supply a different
        function, of the form "find(line, output), to use when searching
        for lines in the output.  The function must return the index
        of the found line in the output, or None if the line is not found.
        """
        out = output.splitlines()
        if is_List(expect):
            exp = [ e.rstrip('\n') for e in expect ]
        else:
            exp = expect.splitlines()
        if sorted(out) == sorted(exp):
            # early out for exact match
            return
        if find is None:
            def find(o, l):
                try:
                    return o.index(l)
                except ValueError:
                    return None
        missing = []
        for line in exp:
            found = find(out, line)
            if found is None:
                missing.append(line)
            else:
                out.pop(found)

        if not missing and not out:
            # all lines were matched
            return

        if title is None:
            title = 'output'
        if missing:
            sys.stdout.write("Missing expected lines from %s:\n" % title)
            for line in missing:
                sys.stdout.write('    ' + repr(line) + '\n')
            sys.stdout.write(self.banner('Missing %s ' % title) + '\n')
        if out:
            sys.stdout.write("Extra unexpected lines from %s:\n" % title)
            for line in out:
                sys.stdout.write('    ' + repr(line) + '\n')
            sys.stdout.write(self.banner('Extra %s ' % title) + '\n')
        sys.stdout.flush()
        self.fail_test()

    def must_contain_lines(self, lines, output, title=None, find = None):
        # Deprecated; retain for backwards compatibility.
        return self.must_contain_all_lines(output, lines, title, find)

    def must_exist(self, *files):
        """Ensures that the specified file(s) must exist.  An individual
        file be specified as a list of directory names, in which case the
        pathname will be constructed by concatenating them.  Exits FAILED
        if any of the files does not exist.
        """
        files = [is_List(x) and os.path.join(*x) or x for x in files]
        missing = [x for x in files if not os.path.exists(x) and not os.path.islink(x) ]
        if missing:
            print "Missing files: `%s'" % "', `".join(missing)
            self.fail_test(missing)

    def must_exist_one_of(self, files):
        """Ensures that at least one of the specified file(s) exists.
        The filenames can be given as a list, where each entry may be
        a single path string, or a tuple of folder names and the final
        filename that get concatenated.
        Supports wildcard names like 'foo-1.2.3-*.rpm'.
        Exits FAILED if none of the files exists.
        """
        missing = []
        for x in files:
            if is_List(x) or is_Tuple(x):
                xpath = os.path.join(*x)
            else:
                xpath = is_Sequence(x) and os.path.join(x) or x
            if glob.glob(xpath):
                return
            missing.append(xpath)
        print "Missing one of: `%s'" % "', `".join(missing)
        self.fail_test(missing)

    def must_match(self, file, expect, mode = 'rb', match=None):
        """Matches the contents of the specified file (first argument)
        against the expected contents (second argument).  The expected
        contents are a list of lines or a string which will be split
        on newlines.
        """
        file_contents = self.read(file, mode)
        if not match:
            match = self.match
        try:
            self.fail_test(not match(file_contents, expect))
        except KeyboardInterrupt:
            raise
        except:
            print "Unexpected contents of `%s'" % file
            self.diff(expect, file_contents, 'contents ')
            raise

    def must_not_contain(self, file, banned, mode = 'rb', find = None):
        """Ensures that the specified file doesn't contain the banned text.
        """
        file_contents = self.read(file, mode)
        if find is None:
            def find(o, l):
                try:
                    return o.index(l)
                except ValueError:
                    return None
        contains = find(file_contents, banned)
        if contains:
            print "File `%s' contains banned string." % file
            print self.banner('Banned string ')
            print banned
            print self.banner('%s contents ' % file)
            print file_contents
            self.fail_test(contains)

    def must_not_contain_any_line(self, output, lines, title=None, find=None):
        """Ensures that the specified output string (first argument)
        does not contain any of the specified lines (second argument).

        An optional third argument can be used to describe the type
        of output being searched, and only shows up in failure output.

        An optional fourth argument can be used to supply a different
        function, of the form "find(line, output), to use when searching
        for lines in the output.
        """
        if find is None:
            def find(o, l):
                try:
                    return o.index(l)
                except ValueError:
                    return None
        unexpected = []
        for line in lines:
            if find(output, line) is not None:
                unexpected.append(line)

        if unexpected:
            if title is None:
                title = 'output'
            sys.stdout.write("Unexpected lines in %s:\n" % title)
            for line in unexpected:
                sys.stdout.write('    ' + repr(line) + '\n')
            sys.stdout.write(self.banner(title + ' ') + '\n')
            sys.stdout.write(output)
            self.fail_test()

    def must_not_contain_lines(self, lines, output, title=None, find=None):
        return self.must_not_contain_any_line(output, lines, title, find)

    def must_not_exist(self, *files):
        """Ensures that the specified file(s) must not exist.
        An individual file be specified as a list of directory names, in
        which case the pathname will be constructed by concatenating them.
        Exits FAILED if any of the files exists.
        """
        files = [is_List(x) and os.path.join(*x) or x for x in files]
        existing = [x for x in files if os.path.exists(x) or os.path.islink(x)]
        if existing:
            print "Unexpected files exist: `%s'" % "', `".join(existing)
            self.fail_test(existing)

    def must_not_exist_any_of(self, files):
        """Ensures that none of the specified file(s) exists.
        The filenames can be given as a list, where each entry may be
        a single path string, or a tuple of folder names and the final
        filename that get concatenated.
        Supports wildcard names like 'foo-1.2.3-*.rpm'.
        Exits FAILED if any of the files exists.
        """
        existing = []
        for x in files:
            if is_List(x) or is_Tuple(x):
                xpath = os.path.join(*x)
            else:
                xpath = is_Sequence(x) and os.path.join(x) or x
            if glob.glob(xpath):
                existing.append(xpath)
        if existing:
            print "Unexpected files exist: `%s'" % "', `".join(existing)
            self.fail_test(existing)

    def must_not_be_writable(self, *files):
        """Ensures that the specified file(s) exist and are not writable.
        An individual file can be specified as a list of directory names,
        in which case the pathname will be constructed by concatenating
        them.  Exits FAILED if any of the files does not exist or is
        writable.
        """
        files = [is_List(x) and os.path.join(*x) or x for x in files]
        existing, missing = separate_files(files)
        writable = list(filter(is_writable, existing))
        if missing:
            print "Missing files: `%s'" % "', `".join(missing)
        if writable:
            print "Writable files: `%s'" % "', `".join(writable)
        self.fail_test(missing + writable)

    def _complete(self, actual_stdout, expected_stdout,
                        actual_stderr, expected_stderr, status, match):
        """
        Post-processes running a subcommand, checking for failure
        status and displaying output appropriately.
        """
        if _failed(self, status):
            expect = ''
            if status != 0:
                expect = " (expected %s)" % str(status)
            print "%s returned %s%s" % (self.program, _status(self), expect)
            print self.banner('STDOUT ')
            print actual_stdout
            print self.banner('STDERR ')
            print actual_stderr
            self.fail_test()
        if (expected_stdout is not None
                and not match(actual_stdout, expected_stdout)):
            self.diff(expected_stdout, actual_stdout, 'STDOUT ')
            if actual_stderr:
                print self.banner('STDERR ')
                print actual_stderr
            self.fail_test()
        if (expected_stderr is not None
                and not match(actual_stderr, expected_stderr)):
            print self.banner('STDOUT ')
            print actual_stdout
            self.diff(expected_stderr, actual_stderr, 'STDERR ')
            self.fail_test()

    def start(self, program = None,
                    interpreter = None,
                    options = None,
                    arguments = None,
                    universal_newlines = None,
                    **kw):
        """
        Starts a program or script for the test environment, handling
        any exceptions.
        """
        arguments = self.options_arguments(options, arguments)
        try:
            return TestCmd.start(self, program, interpreter, arguments,
                                 universal_newlines, **kw)
        except KeyboardInterrupt:
            raise
        except Exception, e:
            print self.banner('STDOUT ')
            try:
                print self.stdout()
            except IndexError:
                pass
            print self.banner('STDERR ')
            try:
                print self.stderr()
            except IndexError:
                pass
            cmd_args = self.command_args(program, interpreter, arguments)
            sys.stderr.write('Exception trying to execute: %s\n' % cmd_args)
            raise e

    def finish(self, popen, stdout = None, stderr = '', status = 0, **kw):
        """
        Finishes and waits for the process being run under control of
        the specified popen argument.  Additional arguments are similar
        to those of the run() method:

                stdout  The expected standard output from
                        the command.  A value of None means
                        don't test standard output.

                stderr  The expected error output from
                        the command.  A value of None means
                        don't test error output.

                status  The expected exit status from the
                        command.  A value of None means don't
                        test exit status.
        """
        TestCmd.finish(self, popen, **kw)
        match = kw.get('match', self.match)
        self._complete(self.stdout(), stdout,
                       self.stderr(), stderr, status, match)

    def run(self, options = None, arguments = None,
                  stdout = None, stderr = '', status = 0, **kw):
        """Runs the program under test, checking that the test succeeded.

        The parameters are the same as the base TestCmd.run() method,
        with the addition of:

                options Extra options that get appended to the beginning
                        of the arguments.

                stdout  The expected standard output from
                        the command.  A value of None means
                        don't test standard output.

                stderr  The expected error output from
                        the command.  A value of None means
                        don't test error output.

                status  The expected exit status from the
                        command.  A value of None means don't
                        test exit status.

        By default, this expects a successful exit (status = 0), does
        not test standard output (stdout = None), and expects that error
        output is empty (stderr = "").
        """
        kw['arguments'] = self.options_arguments(options, arguments)
        try:
            match = kw['match']
            del kw['match']
        except KeyError:
            match = self.match
        TestCmd.run(self, **kw)
        self._complete(self.stdout(), stdout,
                       self.stderr(), stderr, status, match)

    def skip_test(self, message="Skipping test.\n"):
        """Skips a test.

        Proper test-skipping behavior is dependent on the external
        TESTCOMMON_PASS_SKIPS environment variable.  If set, we treat
        the skip as a PASS (exit 0), and otherwise treat it as NO RESULT.
        In either case, we print the specified message as an indication
        that the substance of the test was skipped.

        (This was originally added to support development under Aegis.
        Technically, skipping a test is a NO RESULT, but Aegis would
        treat that as a test failure and prevent the change from going to
        the next step.  Since we ddn't want to force anyone using Aegis
        to have to install absolutely every tool used by the tests, we
        would actually report to Aegis that a skipped test has PASSED
        so that the workflow isn't held up.)
        """
        if message:
            sys.stdout.write(message)
            sys.stdout.flush()
        pass_skips = os.environ.get('TESTCOMMON_PASS_SKIPS')
        if pass_skips in [None, 0, '0']:
            # skip=1 means skip this function when showing where this
            # result came from.  They only care about the line where the
            # script called test.skip_test(), not the line number where
            # we call test.no_result().
            self.no_result(skip=1)
        else:
            # We're under the development directory for this change,
            # so this is an Aegis invocation; pass the test (exit 0).
            self.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
