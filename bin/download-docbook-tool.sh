#! /bin/sh
#
# Copyright (c) 2013 by Pawel Tomulik
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

# download-docbook-tool.sh
#
# Download SCons docbook tool. 

set -e

echo '** Downloading SCons docbook tool **'

TOPDIR=$(readlink -f "$(dirname $0)/..")
TOOLDIR="$TOPDIR/site_scons/site_tools/docbook"
TMPDIR=$(mktemp -d)
URL='https://bitbucket.org/dirkbaechle/scons_docbook/get/default.tar.gz'

test -z "$TMPDIR" && { echo "Failed to create temp directory" >&2 ; exit 1; }
test -d "$TMPDIR" || { echo "'$TMPDIR' is not a directory" >&2 ; exit 1; }

test -x "$TOOLDIR" || mkdir -p "$TOOLDIR"

(cd $TMPDIR && curl "$URL" | tar -zxf - --wildcards --strip-components=1 && \
 cp "__init__.py" "$TOOLDIR" && cp -r "utils" "$TOOLDIR" && \
 cp -r docbook-xsl-*/ "$TOOLDIR" )

rm -rf "$TMPDIR"

# vim: set syntax=sh expandtab tabstop=4 shiftwidth=4 nospell:
