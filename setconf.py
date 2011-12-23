#!/usr/bin/python
# -*- coding: utf-8 -*-
# vim: set enc=utf-8:
# Alexander Rødseth <rodseth@gmail.com>
# May 2009
# GPL

from sys import argv
from sys import exit
from os import linesep

VERSION = "0.2"

def firstpart(line, including_assignment=True):
    # Supports ==, :=, = and :. They are matched in this order.
    assignments = ['==', ':=', '=', ':']
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
        exit(2)
    # Change and write the file
    file = open(filename, "w")
    file.write(linesep.join(change(lines, key, value)) + linesep)
    file.close()

def test_changefile():
    # Test data
    testcontent = "keys := missing" + linesep + "dog = found" + linesep * 3
    testcontent_changed = "keys := found" + linesep + "dog = missing" + linesep * 3
    filename = "/tmp/test_changefile.txt"
    # Write the testfile
    file = open(filename, "w")
    file.write(testcontent)
    file.close()
    # Change the file with changefile
    changefile(filename, "keys", "found")
    changefile(filename, "dog", "missing")
    # Read the file
    file = open(filename, "r")
    newcontent = file.read().split(linesep)[:-1]
    file.close()
    # Do the tests
    passes = True
    passes = passes and newcontent == testcontent_changed.split(linesep)[:-1]
    print("Changefile passes: %s" % (passes))
    return passes

def tests():
    passes = True
    passes = passes and test_changeline()
    passes = passes and test_change()
    passes = passes and test_changefile()
    if passes:
        print("All tests pass!")
    else:
        print("Tests fail.")

def main():
    args = argv[1:]
    if len(args) == 1:
        if args[0] == "test":
            tests()
        elif args[0] == "--help":
            print("setconf changes a key in a textfile to a given value")
            print("")
            print("Arguments:")
            print("\ta filename, a key and a value")
            print("Example:")
            print("\tsetconf Makefile.defaults NETSURF_USE_HARU_PDF NO")
        elif args[0] == "--version":
            print(VERSION)
    elif len(args) == 3:
        filename = args[0]
        key = args[1]
        value = args[2]
        changefile(filename, key, value)
    else:
        exit(1)

if __name__ == "__main__":
    main()
