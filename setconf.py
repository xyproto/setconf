#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# setconf
# Utility for setting options in configuration files.
#
# Alexander F Rødseth <xyproto@archlinux.org>
#
# GPL2
#
# May 2009
# Dec 2011
# Jan 2012
# Mar 2012
# Jun 2012
# Jul 2012
# Mar 2013
# Jul 2013
# Nov 2013
# Aug 2014
# Oct 2014
# Dec 2014
# Mar 2015
# Jun 2015
# Mar 2016
#

from sys import argv
from sys import exit as sysexit
from os import linesep as linesep_str
from os.path import exists
from tempfile import mkstemp
from decimal import Decimal
import argparse

VERSION = "0.7.1"


def bs(x):
    """Convert from string to UTF-8 encoded bytes, if needed"""
    if type(x) != type(b""):
        return x.encode("utf-8")
    return x

NL = bs(linesep_str)
ASSIGNMENTS = [bs('=='), bs('=>'), bs('+='), bs('-='), bs('?='),
               bs('='), bs(':='), bs('::'), bs(':')]


def parts(line, including_assignment=True):
    """Return the key and value parts of a line, if there is an assignment there.
    May include the assignment as part of the key."""
    stripline = line.strip()
    if not stripline:
        return None, None
    # Skip lines that start with #, // or /*
    for commentsymbol in [bs("#"), bs("//"), bs("/*")]:
        if stripline.startswith(commentsymbol):
            # Skip this line
            return None, None
    # These assignments are supported, in this order
    assignment = bs("")
    found = []
    for ass in ASSIGNMENTS:
        # Skip the += and -= operators when finding keys and values
        if ass in [bs('+='), bs('-=')]:
            continue
        # Collect the rest
        if ass in line:
            found.append(ass)
    if len(found) == 1:
        # Only one assignment were found
        assignment = found[0]
    elif found:  # > 1
        # If several assignments are found, use the first one
        firstpos = len(line)
        firstassignment = bs("")
        for ass in found:
            pos = line.index(ass)
            if pos < firstpos:
                firstpos = pos
                firstassignment = ass
        assignment = firstassignment
    # Return the "key" part of the line
    if assignment:
        fields = line.split(assignment, 1)
        if including_assignment:
            return fields[0] + assignment, fields[1]
        else:
            return fields[0], fields[1]
    # No assignments were found
    return None, None


def firstpart(line, including_assignment=True):
    return parts(line, including_assignment)[0]


def secondpart(line, including_assignment=True):
    return parts(line, including_assignment)[1]


def changeline(line, newvalue):
    line = bs(line)
    newvalue = bs(newvalue)

    first = firstpart(line)
    if first:
        if bs("= ") in line or bs(": ") in line or bs("> ") in line:
            return first + bs(" ") + newvalue
        elif bs("=\t") in line or bs(":\t") in line or bs(">\t") in line:
            return first + bs("\t") + newvalue
        else:
            return first + newvalue
    else:
        return line


def change(lines, key, value):
    key = bs(key)
    value = bs(value)

    newlines = []
    for line in lines:
        if not line.strip():
            newlines.append(line)
            continue
        firstp = firstpart(line, False)
        if not firstp:
            newlines.append(line)
            continue
        elif firstp.strip() == key:
            newlines.append(changeline(line, value))
        else:
            newlines.append(line)
    return newlines


def changefile(filename, key, value, dummyrun=False):
    """if dummyrun==True, don't write but return True if changes would have been made"""

    key = bs(key)
    value = bs(value)

    # Read the file
    try:
        with open(filename, 'rb') as f:
            data = f.read()
            lines = data.split(NL)[:-1]
    except IOError:
        print("Can't read %s" % (filename))
        sysexit(2)
    final_nl = True
    if NL not in data:
        lines = [data]
        final_nl = False
    elif not data.endswith(NL):
        final_nl = False
    # Change and write the file
    changed_contents = NL.join(change(lines, key, value))
    # Only add a final newline if the original contents had one at the end
    if final_nl:
        changed_contents += NL
    if dummyrun:
        return data != changed_contents
    try:
        with open(filename, 'wb') as f:
            f.write(changed_contents)
    except IOError:
        print("No write permission: %s" % (filename))
        sysexit(2)


def addtofile(filename, line):
    """Tries to add a line to a file. UTF-8. No questions asked."""

    line = bs(line)

    # Read the file
    try:
        with open(filename, 'rb') as f:
            data = f.read()
            lines = data.split(NL)[:-1]
    except IOError:
        print("Can't read %s" % (filename))
        sysexit(2)
    if data.strip() == bs(""):
        lines = []
    elif NL not in data:
        lines = [data]
    # Change and write the file
    try:
        with open(filename, 'wb') as f:
            lines.append(line)
            added_data = NL.join(lines) + NL
            f.write(added_data)
    except IOError:
        print("No write permission: %s" % (filename))
        sysexit(2)


def change_multiline(data, key, value, endstring=NL, verbose=True, searchfrom=0):

    data = bs(data)
    key = bs(key)
    value = bs(value)
    endstring = bs(endstring)

    if key not in data:
        return data
    if (endstring != NL) and (endstring not in data):
        if verbose:
            print("Multiline end marker not found: " + endstring)
        return data
    startpos = data.find(key, searchfrom)
    if endstring in data:
        endpos = data.find(endstring, startpos + 1)
    else:
        endpos = len(data) - 1
    before = data[:startpos]
    between = data[startpos:endpos + 1]

    linestartpos = data[:startpos].rfind(NL) + 1
    line = data[linestartpos:endpos + 1]
    # If the first part of the line is not a key (could be because it's commented out)...
    if not firstpart(line):
        # Search again, from endpos this time
        return change_multiline(data, key, value, endstring, verbose, endpos)

    after = data[endpos + len(endstring):]
    newbetween = changeline(between, value)
    if between.endswith(NL):
        newbetween += NL
    result = before + newbetween + after
    return result


def changefile_multiline(filename, key, value, endstring=bs("\n")):

    key = bs(key)
    value = bs(value)

    # Read the file
    try:
        with open(filename, 'rb') as f:
            data = f.read()
    except IOError:
        print("Can't read %s" % (filename))
        sysexit(2)
    # Change and write the file
    new_contents = change_multiline(data, key, value, endstring)
    try:
        with open(filename, 'wb') as f:
            f.write(new_contents)
    except:  # UnicodeEncodeError: not supported by shedskin
        #print("codeEncodeError: Can't change value for %s" % (filename))
        print("Can't change value for %s" % (filename))
        sysexit(2)


def create_if_missing(filename):
    if not exists(filename):
        try:
            open(filename, 'wb').close()
        except IOError:
            print("No write permission: %s" % (filename))
            sysexit(2)


def has_key(data, key):
    """Check if the given key exists in the given data."""
    lines = data.split(NL)[:-1]
    for line in lines:
        if not line.strip():
            # Skip blank lines
            continue
        first = firstpart(line, False)
        if key == first:
            return True
    return False


def get_value(data, key):
    """Return the first value for a given key."""
    lines = data.split(NL)[:-1]
    for line in lines:
        if not line.strip():
            # Skip blank lines
            continue
        first, second = parts(line, False)
        if first:
            first = first.strip()
        if second:
            second = second.strip()
        if key == first:
            return second
    return bs("")


def strip_trailing_zeros(s):
    return s.rstrip(bs('0')).rstrip(bs('.')) if bs('.') in s else s


def byte2decimal(b):
    return Decimal(b.decode("utf-8", "ignore"))


def inc(startvalue, s):
    """Increase the number in the byte string with the given byte string,
    or return the same string."""
    try:
        result = bs(str(byte2decimal(startvalue) + byte2decimal(s)))
    except ArithmeticError:
        return s

    return strip_trailing_zeros(result)


def dec(startvalue, s):
    """Decrease the number in the string with the given string,
    or return the same string."""
    try:
        result = bs(str(byte2decimal(startvalue) - byte2decimal(s)))
    except ArithmeticError:
        return s

    return strip_trailing_zeros(result)


def main(args=None):
    description = """\
setconf {version}

Changes a key in a text file to a given value

Syntax:
    setconf filename key value [end string for multiline value]
""".format(version=VERSION)

    epilog="""
Examples:

    setconf Makefile.defaults NETSURF_USE_HARU_PDF NO
    setconf Makefile CC clang
    setconf my.conf x=42
    setconf PKGBUILD sha256sums "('123abc' 'abc123')" ')'
    setconf app.py NUMS "[1, 2, 3]" ']'
    setconf -a server.conf ABC 123"
"""
    parser = argparse.ArgumentParser(prog="setconf",
                description=description,
                epilog=epilog,
                formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("--version", action="version", version=VERSION)
    parser.add_argument("-t", "--test", action="store_true",
                        help="internal self test")
    parser.add_argument("-a", "--add", action="store_true",
                        help="add the option if it doesn't exist\n"
                             "creates the file if needed")
    parser.add_argument("filename", nargs="?")
    parser.add_argument("key", nargs="?") # for setconf x=42
    parser.add_argument("value", nargs="?") # for setconf key val
    parser.add_argument("endstring", nargs="?") # for multiline
    args = parser.parse_args(args=args)
    if args.test:
        import pytest
        rc = pytest.main(args=[])
        sysexit(rc)
    filename = args.filename
    if not filename:
        parser.print_help()
        sysexit(1)
    if not args.value and not args.add:
        # Single line replace: "x=123" or "x+=2"
        keyvalue = bs(args.key)
        if bs("+=") in keyvalue:
            key, value = keyvalue.split(bs("+="), 1)
            try:
                with open(filename, 'rb') as f:
                    data = f.read()
            except IOError:
                print("Can't read %s" % (filename))
                sysexit(2)
            datavalue = get_value(data, key)
            changefile(filename, key, inc(datavalue, value))
        elif bs("-=") in keyvalue:
            key, value = keyvalue.split(bs("-="), 1)
            try:
                with open(filename, 'rb') as f:
                    data = f.read()
            except IOError:
                print("Can't read %s" % (filename))
                sysexit(2)
            datavalue = get_value(data, key)
            changefile(filename, key, dec(datavalue, value))
        elif bs("=") in keyvalue:
            key, value = keyvalue.split(bs("="), 1)
            changefile(filename, key, value)
        else:
            sysexit(2)
        return
    if args.add:
        if not args.value:
            # Single line add with no value
            keyvalue = bs(args.key)

            create_if_missing(filename)

            # Change the file if possible, if not, add the key value
            assignment = None
            special = None
            for ass in ASSIGNMENTS:
                if ass in keyvalue:
                    assignment = ass
                    break
            if not assignment:
                sysexit(2)
            _, value = keyvalue.split(assignment, 1)
            key = firstpart(keyvalue, False)

            if changefile(filename, key, value, dummyrun=True):
                changefile(filename, key, value)
            else:
                with open(filename, 'rb') as f:
                    data = f.read()
                if not has_key(data, key):
                    addtofile(filename, keyvalue)
        else:
            # Single line add with value
            key = bs(args.key)
            value = bs(args.value)

            create_if_missing(filename)

            # Change the file if possible, if not, add the key value
            if changefile(filename, key, value, dummyrun=True):
                changefile(filename, key, value)
            else:
                keyvalue = key + bs("=") + value
                with open(filename, 'rb') as f:
                    data = f.read()
                if not has_key(data, key):
                    addtofile(filename, keyvalue)
    else:
        if args.endstring:
            key = bs(args.key)
            value = bs(args.value)
            endstring = bs(args.endstring)
            changefile_multiline(filename, key, value, endstring)
        else:
            value = bs(args.value)
            changefile(filename, key, value)


if __name__ == "__main__":
    main()
