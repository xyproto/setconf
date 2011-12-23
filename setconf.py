#!/usr/bin/python
# -*- coding: utf-8 -*-
# Alexander Rødseth <rodseth@gmail.com>
# May 2009
# Dec 2011
# GPL

from sys import argv
from sys import exit as sysexit
from os import linesep

VERSION = "0.3"

def firstpart(line, including_assignment=True):
    # Supports ==, :=, ::, = and :. They are matched in this order.
    assignments = ['==', ':=', '::', '=', ':']
    if not line.strip():
        return None
    for assignment in assignments:
        if assignment in line:
            if including_assignment:
                return line.split(assignment, 1)[0] + assignment
            else:
                return line.split(assignment, 1)[0]
    return None

def changeline(line, newvalue):
    first = firstpart(line)
    if first:
        if "= " in line or ": " in line:
            return first + " " + newvalue
        elif "=\t" in line or ":\t" in line:
            return first + "\t" + newvalue
        else:
            return first + newvalue
    else:
        return line

def test_changeline():
    passes = True
    passes = passes and changeline("rabbits = DUMB", "cool") == "rabbits = cool"
    passes = passes and changeline("for ever and ever : never", "and ever") == "for ever and ever : and ever"
    passes = passes and changeline("     for  ever  and  Ever   :=    beaver", "TURTLE") == "     for  ever  and  Ever   := TURTLE"
    passes = passes and changeline("CC=g++", "baffled") == "CC=baffled"
    passes = passes and changeline("CC =\t\tg++", "baffled") == "CC =\tbaffled"
    passes = passes and changeline("cabal ==1.2.3", "1.2.4") == "cabal ==1.2.4"
    print("Changeline passes: %s" % (passes))
    return passes

def change(lines, key, value):
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

def test_change():
    testcontent = """LIGHTS =    ON
bananas= not present
tea := yes
    crazyclown    :ok

"""
    testcontent_changed = """LIGHTS = off
bananas= not present
tea := yes
    crazyclown    :ok

"""
    passes = True
    a = "".join(change(testcontent.split(linesep), "LIGHTS", "off"))
    b = "".join(testcontent_changed.split(linesep))
    passes = passes and a == b
    print("Change passes: %s" % (passes))
    return passes

def changefile(filename, key, value):
    # Read the file
    try:
        file = open(filename)
        data = file.read()
        lines = data.split(linesep)[:-1]
        file.close()
    except IOError:
        print("Can't read %s" % (filename))
        sysexit(2)
    # Change and write the file
    file = open(filename, "w")
    file.write(linesep.join(change(lines, key, value)) + linesep)
    file.close()

def test_changefile(function=changefile):
    print("TEST CHANGEFILE")
    # Test data
    testcontent = "keys := missing" + linesep + "dog = found" + linesep * 3
    testcontent_changed = "keys := found" + linesep + "dog = missing" + linesep * 3
    filename = "/tmp/test_changefile.txt"
    # Write the testfile
    file = open(filename, "w")
    file.write(testcontent)
    file.close()
    # Change the file with changefile
    function(filename, "keys", "found")
    function(filename, "dog", "missing")
    # Read the file
    file = open(filename, "r")
    newcontent = file.read().split(linesep)[:-1]
    file.close()
    # Do the tests
    passes = True
    passes = passes and newcontent == testcontent_changed.split(linesep)[:-1]
    print("NEWCONTENT", newcontent)
    print("CHANGED", testcontent_changed.split(linesep)[:-1])
    print("Changefile passes: %s" % (passes))
    return passes

def change_multiline(data, key, value, endstring="\n"):
    startpos = data.find(key)
    if endstring in data:
        endpos = data.find(endstring, startpos+1)
    else:
        endpos = len(data) - 1
    before = data[:startpos]
    between = data[startpos:endpos+1]
    after = data[endpos+1:]
    newbetween = firstpart(between) + value
    print("BETWEEN:", between)
    print("NEWBETWEEN:", newbetween)
    return before + newbetween + after

def test_change_multiline():
    passes = True
    # test 1
    testcontent = 'blabla\nOST=(a\nb)\n\nblabla'
    testcontent_changed = 'blabla\nOST=(c d)\n\nblabla'
    a = change_multiline(testcontent, "OST", "(c d)", ")")
    b = testcontent_changed
    passes = passes and a == b
    print("TEST1", passes)
    # test 2
    testcontent = 'blabla=1'
    testcontent_changed = 'blabla=2'
    a = change_multiline(testcontent, "blabla", "2")
    b = testcontent_changed
    passes = passes and a == b
    print("TEST2", passes)
    # test 3
    testcontent = "keys := missing" + linesep + "dog = found" + linesep * 3
    testcontent_changed = "keys := found" + linesep + "dog = found" + linesep * 3
    a = change_multiline(testcontent, "keys", "found")
    b = testcontent_changed
    print("A", a)
    print("B", b)
    passes = passes and a == b
    print("TEST3", passes)
    # result
    print("Change multiline passes: %s" % (passes))
    return passes

def changefile_multiline(filename, key, value, endstring="\n"):
    # Read the file
    try:
        file = open(filename)
        data = file.read()
        file.close()
    except IOError:
        print("Can't read %s" % (filename))
        sysexit(2)
    # Change and write the file
    file = open(filename, "w")
    file.write(change_multiline(data, key, value, endstring))
    file.close()

def test_changefile_multiline():
    print("TEST_CHANGEFILE_MULTILINE")
    # Test data
    testcontent = "keys := missing" + linesep + "dog = found" + linesep * 3
    testcontent_changed = "keys := found" + linesep + "dog = missing" + linesep * 3
    filename = "/tmp/test_changefile.txt"
    # Write the testfile
    file = open(filename, "w")
    file.write(testcontent)
    file.close()
    # Change the file with changefile
    changefile_multiline(filename, "keys", "found")
    changefile_multiline(filename, "dog", "missing")
    # Read the file
    file = open(filename, "r")
    newcontent = file.read()
    file.close()
    # Do the tests
    passes = True
    passes = passes and newcontent == testcontent_changed
    print("NEWCONTENT:", newcontent)
    print("CHANGED:", testcontent_changed)
    print("A", passes)
    passes = passes and test_changefile(changefile_multiline)
    print("B", passes)
    print("Changefile multiline passes: %s" % (passes))
    return passes

def tests():
    # If one test fails, the rest will not be run
    passes = True
    passes = passes and test_changeline()
    passes = passes and test_change()
    passes = passes and test_changefile()
    passes = passes and test_change_multiline()
    passes = passes and test_changefile_multiline()
    if passes:
        print("All tests pass!")
    else:
        print("Tests fail.")

def main():
    args = argv[1:]
    if len(args) == 1:
        if args[0] in ["-t", "--test"]:
            tests()
        elif args[0] in ["-h", "--help"]:
            print("setconf changes a key in a textfile to a given value")
            print("")
            print("Options:")
            print("-h or --help\tgive this text")
            print("-t or --test\tinternal self test")
            print("-v or --version\tprint version number")
            print("")
            print("Arguments:")
            print("\ta filename, a key and a value")
            print("\tor: a filename, a key, a value and the end string for multiline values, like \")\"")
            print("")
            print("Examples:")
            print("\tsetconf Makefile.defaults NETSURF_USE_HARU_PDF NO")
            print("\tsetconf PKGBUILD sha256sums \"('fsdaffsda' 'sfdasfdasafd')\" \")\"")
        elif args[0] in ["-v", "--version"]:
            print(VERSION)
    elif len(args) == 3:
        # Single line replace
        filename = args[0]
        key = args[1]
        value = args[2]
        changefile(filename, key, value)
    elif len(args) == 4:
        # Multiline replace
        filename = args[0]
        key = args[1]
        value = args[2]
        endstring = args[3]
        changefile_multiline(filename, key, value, endstring)
    else:
        sysexit(1)

if __name__ == "__main__":
    main()
