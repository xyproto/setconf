#!/usr/bin/python2
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
#

from sys import argv
from sys import exit as sysexit
from os import linesep as linesep_str
from os.path import exists
from tempfile import mkstemp
from subprocess import check_output
from decimal import Decimal
from base64 import b64decode
import chardet

# TODO: Use optparse or argparse if shedskin is no longer a target.

def bs(x):
    """Convert from string to UTF-8 encoded bytes, if needed"""
    if type(x) != type(b""):
        return x.encode("utf-8")
    return x

linesep = bs(linesep_str)

VERSION = "0.6.8"
ASSIGNMENTS = [bs('=='), bs('=>'), bs('+='), bs('-='), bs('?='), bs('='), bs(':='), bs('::'), bs(':')]


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


def test_changeline():
    passes = True
    passes = passes and changeline(" // ost = 2", "3") == bs(" // ost = 2")
    passes = passes and changeline("rabbits = DUMB", "cool") == bs("rabbits = cool")
    passes = passes and changeline(
        "for ever and ever : never",
        "and ever") == bs("for ever and ever : and ever")
    passes = passes and changeline(
        "     for  ever  and  Ever   :=    beaver",
        "TURTLE") == bs("     for  ever  and  Ever   := TURTLE")
    passes = passes and changeline("CC=g++", "baffled") == bs("CC=baffled")
    passes = passes and changeline("CC =\t\tg++", "baffled") == bs("CC =\tbaffled")
    passes = passes and changeline("cabal ==1.2.3", "1.2.4") == bs("cabal ==1.2.4")
    passes = passes and changeline(
        "TMPROOT=${TMPDIR:=/tmp}",
        "/nice/pants") == bs("TMPROOT=/nice/pants")
    passes = passes and changeline("    # ost = 2", "3") == bs("    # ost = 2")

    # The above passes, except for the first one

    passes = passes and changeline("  ost = 2", "3") == bs("  ost = 3")
    passes = passes and changeline("   /* ost = 2 */", "3") == bs("   /* ost = 2 */")
    passes = passes and changeline("æøå =>\t123", "256") == bs("æøå =>\t256")
    print("Changeline passes: %s" % (passes))
    return passes


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


def test_change():
    testcontent = bs("""LIGHTS =    ON
bananas= not present
tea := yes
    randombob    :ok

""")
    testcontent_changed = bs("""LIGHTS = off
bananas= not present
tea := yes
    randombob    :ok

""")
    passes = True
    splitted = testcontent.split(linesep)
    elements = change(splitted, "LIGHTS", "off")
    a = bytes.join(b"", elements)
    b = bytes.join(b"", testcontent_changed.split(linesep))
    passes = passes and a == b
    print("Change passes: %s" % (passes))
    return passes

def changefile(filename, key, value, dummyrun=False):
    """if dummyrun==True, don't write but return True if changes would have been made"""

    key = bs(key)
    value = bs(value)

    # Read the file
    try:
        file = open(filename, 'rb')
        data = file.read()
        lines = data.split(linesep)[:-1]
        file.close()
    except IOError:
        print("Can't read %s" % (filename))
        sysexit(2)
    final_nl = True
    if linesep not in data:
        lines = [data]
        final_nl = False
    elif not data.endswith(linesep):
        final_nl = False
    # Change and write the file
    changed_contents = linesep.join(change(lines, key, value))
    # Only add a final newline if the original contents had one at the end
    if final_nl:
        changed_contents += linesep
    if dummyrun:
        return data != changed_contents
    try:
        file = open(filename, 'wb')
    except IOError:
        print("No write permission: %s" % (filename))
        sysexit(2)
    file.write(changed_contents)
    file.close()

def addtofile(filename, line):
    """Tries to add a line to a file. UTF-8. No questions asked."""

    line = bs(line)

    # Read the file
    try:
        with open(filename, 'rb') as file:
            data = file.read()
            lines = data.split(linesep)[:-1]
    except IOError:
        print("Can't read %s" % (filename))
        sysexit(2)
    if data.strip() == bs(""):
        lines = []
    elif linesep not in data:
        lines = [data]
    # Change and write the file
    try:
        with open(filename, 'wb') as file:
            lines.append(line)
            added_data = linesep.join(lines) + linesep
            file.write(added_data)
    except IOError:
        print("No write permission: %s" % (filename))
        sysexit(2)

def test_changefile():
    # Test data
    testcontent = bs("keys := missing") + linesep + bs("døg = found") + linesep * 3 + bs("æøåÆØÅ") + linesep
    testcontent_changed = bs("keys := found") + linesep + \
        bs("døg = missing") + linesep * 3 + bs("æøåÆØÅ") + linesep
    filename = mkstemp()[1]
    # Write the testfile
    with open(filename, 'wb') as file:
        file.write(testcontent)
    # Change the file with changefile
    changefile(filename, "keys", "found")
    changefile(filename, "døg", "missing")
    # Read the file
    with open(filename, 'rb') as file:
        newcontent = file.read().split(linesep)[:-1]
    # Do the tests
    passes = True
    passes = passes and newcontent == testcontent_changed.split(linesep)[:-1]
    print("Changefile passes: %s" % (passes))
    return passes


def change_multiline(data, key, value, endstring=linesep, verbose=True, searchfrom=0):

    data = bs(data)
    key = bs(key)
    value = bs(value)
    endstring = bs(endstring)

    if key not in data:
        return data
    if (endstring != linesep) and (endstring not in data):
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

    linestartpos = data[:startpos].rfind(linesep) + 1
    line = data[linestartpos:endpos + 1]
    # If the first part of the line is not a key (could be because it's commented out)...
    if not firstpart(line):
        # Search again, from endpos this time
        return change_multiline(data, key, value, endstring, verbose, endpos)

    after = data[endpos + len(endstring):]
    newbetween = changeline(between, value)
    if between.endswith(linesep):
        newbetween += linesep
    result = before + newbetween + after
    return result


def test_change_multiline():
    passes = True
    # test 1
    testcontent = bs("keys := missing") + linesep + bs("dog = found") + linesep * 3
    testcontent_changed = bs("keys := found") + linesep + bs("dog = found") + linesep * 3
    a = change_multiline(testcontent, "keys", "found")
    b = testcontent_changed
    extracheck = testcontent.replace(bs("missing"), bs("found")) == testcontent_changed
    passes = passes and a == b and extracheck
    if not passes:
        print("FAIL1")
    # test 2
    testcontent = bs('blabla\nOST=(a\nb)\n\nblabla\nÆØÅ')
    testcontent_changed = bs('blabla\nOST=(c d)\n\nblabla\nÆØÅ')
    a = change_multiline(testcontent, "OST", "(c d)", ")")
    b = testcontent_changed
    passes = passes and a == b
    if not passes:
        print("FAIL2")
    # test 3
    testcontent = bs('bläblä=1')
    testcontent_changed = bs('bläblä=2')
    a = change_multiline(testcontent, "bläblä", "2")
    b = testcontent_changed
    passes = passes and a == b
    if not passes:
        print("FAIL3")
    # test 4
    testcontent = bs("\n")
    testcontent_changed = bs("\n")
    a = change_multiline(testcontent, "blablañ", "ost")
    b = testcontent_changed
    passes = passes and a == b
    if not passes:
        print("FAIL4")
    # test 5
    testcontent = bs("")
    testcontent_changed = bs("")
    a = change_multiline(testcontent, "blabla", "ost")
    b = testcontent_changed
    passes = passes and a == b
    if not passes:
        print("FAIL5")
    # test 6
    testcontent = bs("a=(1, 2, 3")
    testcontent_changed = bs("a=(1, 2, 3")
    a = change_multiline(testcontent, "a", "(4, 5, 6)", ")", verbose=False)
    b = testcontent_changed
    passes = passes and a == b
    if not passes:
        print("FAIL6")
    # test 7
    testcontent = bs("a=(1, 2, 3\nb=(7, 8, 9)")
    testcontent_changed = bs("a=(4, 5, 6)")
    a = change_multiline(testcontent, "a", "(4, 5, 6)", ")")
    b = testcontent_changed
    passes = passes and a == b
    if not passes:
        print("FAIL7")
    # test 8
    testcontent = bs("a=(0, 0, 0)\nb=(1\n2\n3\n)\nc=(7, 8, 9)")
    testcontent_changed = bs("a=(0, 0, 0)\nb=(4, 5, 6)\nc=(7, 8, 9)")
    a = change_multiline(testcontent, "b", "(4, 5, 6)", ")")
    b = testcontent_changed
    passes = passes and a == b
    if not passes:
        print("FAIL8")
    # test 9
    testcontent = bs("a=(0, 0, 0)\nb=(1\n2\n3\n)\nc=(7, 8, 9)\n\n")
    testcontent_changed = bs("a=(0, 0, 0)\nb=(1\n2\n3\n)\nc=(7, 8, 9)\n\n")
    a = change_multiline(testcontent, "b", "(4, 5, 6)", "]", verbose=False)
    b = testcontent_changed
    passes = passes and a == b
    if not passes:
        print("FAIL9")
    # test 10
    testcontent = bs("""
source=("http://prdownloads.sourceforge.net/maniadrive/ManiaDrive-$pkgver-linux-i386.tar.gz"
        "maniadrive.desktop"
        "ñlicense.txt"
        "https://admin.fedoraproject.org/pkgdb/appicon/show/Maniadrive")
md5sums=('5592eaf4b8c4012edcd4f0fc6e54c09c'
         '064639f1b48ec61e46c524ae31eec520'
         'afa5fac56d01430e904dd6716d84f4bf'
         '9b5fc9d981d460a7b0c9d78e75c5aeca')

build() {
  cd "$srcdir/ManiaDrive-$pkgver-linux-i386"
""")
    testcontent_changed = bs("""
source=("http://prdownloads.sourceforge.net/maniadrive/ManiaDrive-$pkgver-linux-i386.tar.gz"
        "maniadrive.desktop"
        "ñlicense.txt"
        "https://admin.fedoraproject.org/pkgdb/appicon/show/Maniadrive")
md5sums=('123abc' 'abc123')

build() {
  cd "$srcdir/ManiaDrive-$pkgver-linux-i386"
""")
    a = change_multiline(testcontent, "md5sums", "('123abc' 'abc123')", ")", verbose=False)
    b = testcontent_changed
    passes = passes and a == b
    if not passes:
        print("FAIL10")
    # test 11
    testcontent = bs("x=(0, 0, 0)\nCHEESE\nz=2\n")
    testcontent_changed = bs("x=(4, 5, 6)\nz=2\n")
    a = change_multiline(testcontent, "x", "(4, 5, 6)", "CHEESE", verbose=False)
    b = testcontent_changed
    passes = passes and a == b
    if not passes:
        print("FAIL11")
    # test 12
    testcontent = bs("# md5sum=('abc123')\nmd5sum=('def456')\nmd5sum=('ghi789')\n")
    testcontent_changed = bs("# md5sum=('abc123')\nmd5sum=('OST')\nmd5sum=('ghi789')\n")
    a = change_multiline(testcontent, "md5sum", "('OST')", "\n", verbose=False)
    b = testcontent_changed
    passes = passes and a == b
    if not passes:
        print("FAIL12")
    # result
    print("Change multiline passes: %s" % (passes))
    return passes


def changefile_multiline(filename, key, value, endstring=bs("\n")):

    key = bs(key)
    value = bs(value)

    # Read the file
    try:
        file = open(filename, 'rb')
        data = file.read()
        file.close()
    except IOError:
        print("Can't read %s" % (filename))
        sysexit(2)
    # Change and write the file
    new_contents = change_multiline(data, key, value, endstring)
    try:
        file = open(filename, 'wb')
        file.write(new_contents)
    except:  # UnicodeEncodeError: not supported by shedskin
        #print("codeEncodeError: Can't change value for %s" % (filename))
        print("Can't change value for %s" % (filename))
        sysexit(2)
    # finally is not supported by shedskin
    file.close()


def test_changefile_multiline():
    # Test data
    testcontent = bs("keys := missing") + linesep + bs("dog = found") + linesep * 3 + bs("æøåÆØÅ")
    testcontent_changed = bs("keys := found") + linesep + bs("dog = missing") + linesep * 3 + bs("æøåÆØÅ")
    filename = mkstemp()[1]
    # Write the testfile
    file = open(filename, 'wb')
    file.write(testcontent)
    file.close()
    # Change the file with changefile
    changefile_multiline(filename, "keys", "found")
    changefile_multiline(filename, "dog", "missing")
    # Read the file
    file = open(filename, 'rb')
    newcontent = file.read()
    file.close()
    # Do the tests
    passes = True
    passes = passes and newcontent == testcontent_changed
    print("Changefile multiline passes: %s" % (passes))
    return passes

# Note that this test function may cause sysexit to be called if it fails
# because it calls the main function directly


def test_addline():
    # --- TEST 1 ---
    testcontent = bs("# cache-ttl=65000") + linesep + bs("MOO=yes") + linesep
    testcontent_changed = bs("# cache-ttl=65000") + linesep + bs("MOO=no") + linesep + \
            bs("X=123") + linesep + bs("Y=345") + linesep + bs("Z:=567") + linesep + \
                          bs("FJORD => 999") + linesep + bs('vm.swappiness=1') + \
                          linesep + bs("cache-ttl=6") + linesep
    filename = mkstemp()[1]
    # Write the testfile
    with open(filename, 'wb') as file:
        file.write(testcontent)
    # Change the file by adding keys and values
    main(["-a", filename, "X", "123"])
    main(["--add", filename, "Y=345"])
    main(["-a", filename, "Z:=567"])
    main(["--add", filename, "FJORD => 999"])
    main(["--add", filename, "MOO", "no"])
    main(["-a", filename, "vm.swappiness=1"])
    main(["-a", filename, "vm.swappiness=1"])
    main(["-a", filename, "cache-ttl=6"])
    # Read the file
    with open(filename, 'rb') as file:
        newcontent = file.read()

    # --- TEST 2 ---
    testcontent_changed2 = bs("x=2") + linesep
    filename = mkstemp()[1]
    # Write an empty testfile
    open(filename, 'wb+').close()
    # Change the file by adding keys and values
    main(["-a", filename, "x=2"])
    # Read the file
    with open(filename, 'rb') as file2:
        newcontent2 = file2.read()

    # Do the tests
    passes = True
    passes = passes and (newcontent == testcontent_changed)
    passes = passes and (newcontent2 == testcontent_changed2)

    print("Addline passes: %s" % (passes))
    return passes


def test_latin1():
    # Test data
    testcontent = b64decode("SGVsbG8sIHRoaXMgaXMgYW4gSVNPLTg4NTktMSBlbmNvZGVkIHRleHQgZmlsZS4gQmzlYuZyIG9n\nIHL4ZHZpbi4KCkFsc28sCng9Nwo=")
    testcontent_changed = b64decode("SGVsbG8sIHRoaXMgaXMgYW4gSVNPLTg4NTktMSBlbmNvZGVkIHRleHQgZmlsZS4gQmzlYuZyIG9n\nIHL4ZHZpbi4KCkFsc28sCng9NDIK")

    filename = mkstemp()[1]
    # Write the testfile
    with open(filename, 'wb') as file:
        file.write(testcontent) # already bytes, no need to encode
    # Change the file with changefile
    changefile(filename, "x", "42")
    # Read the file
    with open(filename, 'rb') as file:
        newcontent = file.read().split(linesep)[:-1]
    # Do the tests
    passes = True
    passes = passes and newcontent == testcontent_changed.split(linesep)[:-1]
    print("ISO-8859-1 passes: %s" % (passes))
    return passes


def tests():
    # If one test fails, the rest will not be run
    passes = True
    passes = passes and test_changeline()
    passes = passes and test_change()
    passes = passes and test_changefile()
    passes = passes and test_change_multiline()
    passes = passes and test_changefile_multiline()
    passes = passes and test_addline()
    passes = passes and test_latin1()
    if passes:
        print("All tests pass!")
    else:
        print("Tests fail.")


def create_if_missing(filename):
    if not exists(filename):
        try:
            f = open(filename, 'wb')
        except IOError:
            print("No write permission: %s" % (filename))
            sysexit(2)
        f.close()


def has_key(data, key):
    """Check if the given key exists in the given data."""
    lines = data.split(linesep)[:-1]
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
    lines = data.split(linesep)[:-1]
    for line in lines:
        if not line.strip():
            # Skip blank lines
            continue
        first, second = parts(line, False)
        if key == first:
            return second
    return ""

def strip_trailing_zeros(s):
    return s.rstrip('0').rstrip('.') if '.' in s else s

def inc(startvalue, s):
    """Increase the number in the string with the given string, or return the same string."""
    try:
        result = str(Decimal(startvalue)+Decimal(s))
    except ArithmeticError:
        return s

    return strip_trailing_zeros(result)

def dec(startvalue, s):
    """Decrease the number in the string with the given string, or return the same string."""
    try:
        result = str(Decimal(startvalue)-Decimal(s))
    except ArithmeticError:
        return s

    return strip_trailing_zeros(result)

def main(args=argv[1:], exitok=True):
    if len(args) == 1:
        if args[0] in ["-t", "--test"]:
            tests()
        elif args[0] in ["-h", "--help"]:
            print("setconf " + VERSION)
            print("")
            print("Changes a key in a text file to a given value")
            print("")
            print("Syntax:")
            print("\tsetconf filename key value [end string for multiline value]")
            print("")
            print("Options:")
            print("\t-h or --help\t\tthis text")
            print("\t-t or --test\t\tinternal self test")
            print("\t-v or --version\t\tversion number")
            print("\t-a or --add\t\tadd the option if it doesn't exist")
            print("\t\t\t\tcreates the file if needed")
            #print("\t-r or --remove\t\tremove the option if it exist")
            print("")
            print("Examples:")
            print("\tsetconf Makefile.defaults NETSURF_USE_HARU_PDF NO")
            print("\tsetconf Makefile CC clang")
            print("\tsetconf my.conf x=42")
            print("\tsetconf PKGBUILD sha256sums \"('123abc' 'abc123')\" ')'")
            print("\tsetconf app.py NUMS \"[1, 2, 3]\" ']'")
            print("\tsetconf -a server.conf ABC 123")
            #print("\tsetconf -r server.conf ABC")
            print("")
        elif args[0] in ["-v", "--version"]:
            print(VERSION)
    elif len(args) == 2:
        # Single line replace: "x=123" or "x+=2"
        filename = args[0]
        keyvalue = bs(args[1])
        if bs("+=") in keyvalue:
            key, value = keyvalue.split(bs("+="), 1)
            try:
                f = open(filename, 'rb')
            except IOError:
                print("Can't read %s" % (filename))
                sysexit(2)
            data = f.read()
            f.close()
            datavalue = get_value(data, key)
            changefile(filename, key, inc(datavalue, value))
        elif bs("-=") in keyvalue:
            key, value = keyvalue.split(bs("-="), 1)
            try:
                f = open(filename, 'rb')
            except IOError:
                print("Can't read %s" % (filename))
                sysexit(2)
            data = f.read()
            f.close()
            datavalue = get_value(data, key)
            changefile(filename, key, dec(datavalue, value))
        elif "=" in keyvalue:
            key, value = keyvalue.split(bs("="), 1)
            changefile(filename, key, value)
        else:
            sysexit(2)
    elif len(args) == 3:
        if args[0] in ["-a", "--add"]:
            # Single line replace/add ("x 123")
            filename = args[1]
            keyvalue = bs(args[2])

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
                f = open(filename, 'rb')
                data = f.read()
                f.close()
                if not has_key(data, key):
                    addtofile(filename, keyvalue)
        else:
            # Single line replace ("x 123")
            filename = args[0]
            key = bs(args[1])
            value = bs(args[2])
            changefile(filename, key, value)
    elif len(args) == 4:
        if args[0] in ["-a", "--add"]:
            filename = args[1]
            key = bs(args[2])
            value = bs(args[3])

            create_if_missing(filename)

            # Change the file if possible, if not, add the key value
            if changefile(filename, key, value, dummyrun=True):
                changefile(filename, key, value)
            else:
                keyvalue = key + bs("=") + value
                f = open(filename, 'rb')
                data = f.read()
                f.close()
                if not has_key(data, key):
                    addtofile(filename, keyvalue)
        else:
            # Multiline replace
            filename = args[0]
            key = bs(args[1])
            value = bs(args[2])
            endstring = bs(args[3])
            changefile_multiline(filename, key, value, endstring)
    else:
        sysexit(1)

if __name__ == "__main__":
    main()

