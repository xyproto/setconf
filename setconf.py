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
# Oct 2017
#

from sys import argv
from sys import exit as sysexit
from os import linesep as linesep_str
from os.path import exists
from tempfile import mkstemp
from decimal import Decimal
from base64 import b64decode

VERSION = "0.7.5"

# TODO: Use optparse or argparse if shedskin is no longer a target.


def bs(x):
    """Convert from string to UTF-8 encoded bytes, if needed"""
    if type(x) != type(b""):
        return x.encode("utf-8")
    return x


NL = bs(linesep_str)
ASSIGNMENTS = [b'==', b'=>', b'+=', b'-=', b'?=',
               b'=', b':=', b'::', b':', b'is']
SINGLE_LINE_COMMENTS = [b"#", b"//", b"--"]
MULTI_LINE_COMMENTS = [b"/*"]


def parts(line, including_assignment=True):
    """Return the key and value parts of a line, if there is an assignment there.
    May include the assignment as part of the key."""
    stripline = line.strip()
    if not stripline:
        return None, None
    # Skip lines that start with #, // or /*
    for commentsymbol in SINGLE_LINE_COMMENTS + MULTI_LINE_COMMENTS:
        if stripline.startswith(commentsymbol):
            # Skip this line
            return None, None
    # These assignments are supported, in this order
    assignment = b""
    found = []
    for ass in ASSIGNMENTS:
        # Skip the += and -= operators when finding keys and values
        if ass in [b'+=', b'-=']:
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
        firstassignment = b""
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


def changeline(line, newvalue):
    line = bs(line)
    newvalue = bs(newvalue)

    first = firstpart(line)
    if first:
        if b"= " in line or b": " in line or b"> " in line:
            return first + b" " + newvalue
        elif b"=\t" in line or b":\t" in line or b">\t" in line:
            return first + b"\t" + newvalue
        else:
            # Special case for Linux kernel configuration files
            if first.endswith(b" is"):
                # Use "=" instead of "is" when setting a config value to "=y" for instance
                first = first[:-3] + b"="
            return first + newvalue
    else:
        return line


def test_changeline():
    passes = True
    passes = passes and changeline(" // ost = 2", "3") == b" // ost = 2"
    passes = passes and changeline("rabbits = DUMB", "cool") == b"rabbits = cool"
    passes = passes and changeline(
        "for ever and ever : never",
        "and ever") == b"for ever and ever : and ever"
    passes = passes and changeline(
        "     for  ever  and  Ever   :=    beaver",
        "TURTLE") == b"     for  ever  and  Ever   := TURTLE"
    passes = passes and changeline("CC=g++", "baffled") == b"CC=baffled"
    passes = passes and changeline("CC =\t\tg++", "baffled") == b"CC =\tbaffled"
    passes = passes and changeline("cabal ==1.2.3", "1.2.4") == b"cabal ==1.2.4"
    passes = passes and changeline(
        "TMPROOT=${TMPDIR:=/tmp}",
        "/nice/pants") == b"TMPROOT=/nice/pants"
    passes = passes and changeline("    # ost = 2", "3") == b"    # ost = 2"

    # The above passes, except for the first one

    passes = passes and changeline("  ost = 2", "3") == b"  ost = 3"
    passes = passes and changeline("   /* ost = 2 */", "3") == b"   /* ost = 2 */"
    passes = passes and changeline("æøå =>\t123", "256") == bs("æøå =>\t256")
    print("Changeline passes: %s" % (passes))
    return passes


def uncomment(lines, key):
    """Given a list of lines and a key, uncomment lines starting with a single line comment."""
    key = bs(key)

    newlines = []
    for line in lines:
        if not line.strip():
            newlines.append(line)
            continue
        else:
            stripped = line.strip()
            comment_markers = SINGLE_LINE_COMMENTS
            # Strip away comment marker + space if possible, if not, just strip away the comment marker
            for comment_marker in [x + b" " for x in comment_markers] + comment_markers:
                if stripped.startswith(comment_marker):
                    # Use the line, with the comment stripped away
                    commentpos = line.find(comment_marker)
                    after_comment_marker = line[commentpos + len(comment_marker):]
                    stripped_contents = after_comment_marker.strip()
                    if stripped_contents.startswith(key):
                        newlines.append(line[:commentpos] + after_comment_marker)
                        break
            else:
                # No uncommenting, the regular case
                newlines.append(line)
    return newlines


def test_uncomment():
    testcontent = b"""y = 1
// x = 42
  #CONFIG_EVERYTHING=y
z := 9
"""
    testcontent_changed = b"""y = 1
// x = 42
  CONFIG_EVERYTHING="ABSOLUTELY NOT"
z := 9
"""
    passes = True
    splitted = testcontent.split(NL)
    splitted = uncomment(splitted, "CONFIG_EVERYTHING")
    elements = change(splitted, "CONFIG_EVERYTHING", "\"ABSOLUTELY NOT\"")
    a = bytes.join(b"", elements)
    b = bytes.join(b"", testcontent_changed.split(NL))
    passes = passes and a == b
    print("Uncomment passes: %s" % (passes))
    return passes


def change(lines, key, value, define=False):
    key = bs(key)
    value = bs(value)

    newlines = []
    for line in lines:
        if not line.strip():
            newlines.append(line)
            continue
        if define:
            if line.strip().startswith(b"#define") and line.count(b" ") >= 2:
                firstp = line.split()[1].strip()
                oldvalue = line.split()[2].strip()
                if firstp == key:
                    newlines.append(line.replace(oldvalue, value))
                    continue
            newlines.append(line)
            continue
        else:
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
    testcontent = b"""LIGHTS =    ON
bananas= not present
tea := yes
    randombob    :ok

"""
    testcontent_changed = b"""LIGHTS = off
bananas= not present
tea := yes
    randombob    :ok

"""
    passes = True
    splitted = testcontent.split(NL)
    elements = change(splitted, "LIGHTS", "off")
    a = bytes.join(b"", elements)
    b = bytes.join(b"", testcontent_changed.split(NL))
    passes = passes and a == b
    print("Change passes: %s" % (passes))
    return passes


def test_change_define():
    passes = True

    testcontent = b"#define X 12"
    testcontent_changed = b"#define X 42"
    output = change([testcontent], "X", "42", define=True)[0]
    passes = passes and output == testcontent_changed

    testcontent = b"   #define   X    12"
    testcontent_changed = b"   #define   X    42"
    output = change([testcontent], "X", "42", define=True)[0]
    passes = passes and output == testcontent_changed

    print("Change define passes: %s" % (passes))
    return passes


def changefile(filename, key, value, dummyrun=False, define=False, uncomment_first=False):
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
    if uncomment_first:
        changed_contents = NL.join(change(uncomment(lines, key), key, value, define=define))
    else:
        changed_contents = NL.join(change(lines, key, value, define=define))
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
    if data.strip() == b"":
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


def test_changefile():
    # Test data
    testcontent = b"keys := missing" + NL + bs("døg = found") + NL * 3 + bs("æøåÆØÅ") + NL
    testcontent_changed = b"keys := found" + NL + \
        bs("døg = missing") + NL * 3 + bs("æøåÆØÅ") + NL
    filename = mkstemp()[1]
    # Write the testfile
    with open(filename, 'wb') as f:
        f.write(testcontent)
    # Change the file with changefile
    changefile(filename, "keys", "found")
    changefile(filename, "døg", "missing")
    # Read the file
    with open(filename, 'rb') as f:
        newcontent = f.read().split(NL)[:-1]
    # Do the tests
    passes = True
    passes = passes and newcontent == testcontent_changed.split(NL)[:-1]
    print("Changefile passes: %s" % (passes))
    return passes


def test_changefile_uncomment():
    # Test data
    testcontent = b"""#   y = 1
// x = 42
  #DESTROY_EVERYTHING=y
# z  :=  123
"""
    testcontent_changed = b"""  y = 2
x = 9000
  #DESTROY_EVERYTHING=y
z  := 7
"""
    filename = mkstemp()[1]
    # Write the testfile
    with open(filename, 'wb') as f:
        f.write(testcontent)
    # Change the file with changefile
    changefile(filename, "x", "9000", uncomment_first=True)
    changefile(filename, "DESTROY_EVERYTHING", "!IGNORED!", uncomment_first=False)
    changefile(filename, "z", "7", uncomment_first=True)
    changefile(filename, "y", "2", uncomment_first=True)
    # Read the file
    with open(filename, 'rb') as f:
        newcontent = f.read().split(NL)[:-1]
    # Do the tests
    passes = True
    passes = passes and newcontent == testcontent_changed.split(NL)[:-1]
    print("Changefile and uncomment passes: %s" % (passes))
    return passes


def test_changefile_uncomment_kernel():
    # Test data
    testcontent = b"""# CONFIG_KERNEL_XZ is not set
"""
    testcontent_changed = b"""CONFIG_KERNEL_XZ=y
"""
    filename = mkstemp()[1]
    # Write the testfile
    with open(filename, 'wb') as f:
        f.write(testcontent)
    # Change the file with changefile
    changefile(filename, "CONFIG_KERNEL_XZ", "y", uncomment_first=True)
    # Read the file
    with open(filename, 'rb') as f:
        newcontent = f.read().split(NL)[:-1]
    # Do the tests
    passes = True
    passes = passes and newcontent == testcontent_changed.split(NL)[:-1]
    print("Changefile kernel config passes: %s" % (passes))
    return passes


def change_multiline(data, key, value, endstring=NL, verbose=True, searchfrom=0, define=False):

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
        return change_multiline(data, key, value, endstring, verbose, endpos, define=define)

    after = data[endpos + len(endstring):]
    newbetween = changeline(between, value)
    if between.endswith(NL):
        newbetween += NL
    result = before + newbetween + after
    return result


def test_change_multiline():
    passes = True
    # test 1
    testcontent = b"keys := missing" + NL + b"dog = found" + NL * 3
    testcontent_changed = b"keys := found" + NL + b"dog = found" + NL * 3
    a = change_multiline(testcontent, "keys", "found")
    b = testcontent_changed
    extracheck = testcontent.replace(b"missing", b"found") == testcontent_changed
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
    testcontent = b"\n"
    testcontent_changed = b"\n"
    a = change_multiline(testcontent, "blablañ", "ost")
    b = testcontent_changed
    passes = passes and a == b
    if not passes:
        print("FAIL4")
    # test 5
    testcontent = b""
    testcontent_changed = b""
    a = change_multiline(testcontent, "blabla", "ost")
    b = testcontent_changed
    passes = passes and a == b
    if not passes:
        print("FAIL5")
    # test 6
    testcontent = b"a=(1, 2, 3"
    testcontent_changed = b"a=(1, 2, 3"
    a = change_multiline(testcontent, "a", "(4, 5, 6)", ")", verbose=False)
    b = testcontent_changed
    passes = passes and a == b
    if not passes:
        print("FAIL6")
    # test 7
    testcontent = b"a=(1, 2, 3\nb=(7, 8, 9)"
    testcontent_changed = b"a=(4, 5, 6)"
    a = change_multiline(testcontent, "a", "(4, 5, 6)", ")")
    b = testcontent_changed
    passes = passes and a == b
    if not passes:
        print("FAIL7")
    # test 8
    testcontent = b"a=(0, 0, 0)\nb=(1\n2\n3\n)\nc=(7, 8, 9)"
    testcontent_changed = b"a=(0, 0, 0)\nb=(4, 5, 6)\nc=(7, 8, 9)"
    a = change_multiline(testcontent, "b", "(4, 5, 6)", ")")
    b = testcontent_changed
    passes = passes and a == b
    if not passes:
        print("FAIL8")
    # test 9
    testcontent = b"a=(0, 0, 0)\nb=(1\n2\n3\n)\nc=(7, 8, 9)\n\n"
    testcontent_changed = b"a=(0, 0, 0)\nb=(1\n2\n3\n)\nc=(7, 8, 9)\n\n"
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
    testcontent = b"x=(0, 0, 0)\nCHEESE\nz=2\n"
    testcontent_changed = b"x=(4, 5, 6)\nz=2\n"
    a = change_multiline(testcontent, "x", "(4, 5, 6)", "CHEESE", verbose=False)
    b = testcontent_changed
    passes = passes and a == b
    if not passes:
        print("FAIL11")
    # test 12
    testcontent = b"# md5sum=('abc123')\nmd5sum=('def456')\nmd5sum=('ghi789')\n"
    testcontent_changed = b"# md5sum=('abc123')\nmd5sum=('OST')\nmd5sum=('ghi789')\n"
    a = change_multiline(testcontent, "md5sum", "('OST')", "\n", verbose=False)
    b = testcontent_changed
    passes = passes and a == b
    if not passes:
        print("FAIL12")
    # result
    print("Change multiline passes: %s" % (passes))
    return passes


def changefile_multiline(filename, key, value, endstring=b"\n"):

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


def test_changefile_multiline():
    # Test data
    testcontent = b"keys := missing" + NL + b"dog = found" + NL * 3 + bs("æøåÆØÅ")
    testcontent_changed = b"keys := found" + NL + b"dog = missing" + NL * 3 + bs("æøåÆØÅ")
    filename = mkstemp()[1]
    # Write the testfile
    with open(filename, 'wb') as f:
        f.write(testcontent)
    # Change the file with changefile
    changefile_multiline(filename, "keys", "found")
    changefile_multiline(filename, "dog", "missing")
    # Read the file
    with open(filename, 'rb') as f:
        newcontent = f.read()
    # Do the tests
    passes = True
    passes = passes and newcontent == testcontent_changed
    print("Changefile multiline passes: %s" % (passes))
    return passes

# Note that this test function may cause sysexit to be called if it fails
# because it calls the main function directly


def test_addline():
    # --- TEST 1 ---
    testcontent = b"# cache-ttl=65000" + NL + b"MOO=yes" + NL
    testcontent_changed = b"# cache-ttl=65000" + NL + b"MOO=no" + NL + \
        b"X=123" + NL + b"Y=345" + NL + b"Z:=567" + NL + \
        b"FJORD => 999" + NL + b'vm.swappiness=1' + \
        NL + b"cache-ttl=6" + NL
    filename = mkstemp()[1]
    # Write the testfile
    with open(filename, 'wb') as f:
        f.write(testcontent)
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
    with open(filename, 'rb') as f:
        newcontent = f.read()

    # --- TEST 2 ---
    testcontent_changed2 = b"x=2" + NL
    filename = mkstemp()[1]
    # Write an empty testfile
    open(filename, 'wb+').close()
    # Change the file by adding keys and values
    main(["-a", filename, "x=2"])
    # Read the file
    with open(filename, 'rb') as f:
        newcontent2 = f.read()

    # Do the tests
    passes = True
    passes = passes and (newcontent == testcontent_changed)
    passes = passes and (newcontent2 == testcontent_changed2)

    print("Addline passes: %s" % (passes))
    return passes


def test_latin1():
    # Test data
    testcontent = b64decode(
        b"SGVsbG8sIHRoaXMgaXMgYW4gSVNPLTg4NTktMSBlbmNvZGVkIHRleHQgZmlsZS4gQmzlYuZyIG9n\nIHL4ZHZpbi4KCkFsc28sCng9Nwo=")
    testcontent_changed = b64decode(
        b"SGVsbG8sIHRoaXMgaXMgYW4gSVNPLTg4NTktMSBlbmNvZGVkIHRleHQgZmlsZS4gQmzlYuZyIG9n\nIHL4ZHZpbi4KCkFsc28sCng9NDIK")

    filename = mkstemp()[1]
    # Write the testfile
    with open(filename, 'wb') as f:
        f.write(testcontent)  # already bytes, no need to encode
    # Change the file with changefile
    changefile(filename, "x", "42")
    # Read the file
    with open(filename, 'rb') as f:
        newcontent = f.read().split(NL)[:-1]
    # Do the tests
    passes = True
    passes = passes and newcontent == testcontent_changed.split(NL)[:-1]
    print("ISO-8859-1 passes: %s" % (passes))
    return passes


def tests():
    # If one test fails, the rest will not be run
    passes = True
    passes = passes and test_changeline()
    passes = passes and test_change()
    passes = passes and test_change_define()
    passes = passes and test_changefile()
    passes = passes and test_change_multiline()
    passes = passes and test_changefile_multiline()
    passes = passes and test_addline()
    passes = passes and test_latin1()
    passes = passes and test_uncomment()
    passes = passes and test_changefile_uncomment()
    passes = passes and test_changefile_uncomment_kernel()
    if passes:
        print("All tests pass!")
    else:
        print("Tests fail.")


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
    return b""


def strip_trailing_zeros(s):
    return s.rstrip(b'0').rstrip(b'.') if b'.' in s else s


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


def main(args=argv[1:]):
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
            print("\t-d or --define\t\tset a #define")
            print("\t-u or --uncomment\t\tuncomment the line first")
            print("")
            print("Examples:")
            print("\tsetconf Makefile.defaults NETSURF_USE_HARU_PDF NO")
            print("\tsetconf Makefile CC clang")
            print("\tsetconf my.conf x=42")
            print("\tsetconf PKGBUILD sha256sums \"('123abc' 'abc123')\" ')'")
            print("\tsetconf app.py NUMS \"[1, 2, 3]\" ']'")
            print("\tsetconf -a server.conf ABC 123")
            print("\tsetconf -d linux/printk.h CONSOLE_LOGLEVEL_DEFAULT=4")
            print("\tsetconf -u kernel_config CONFIG_MAGIC_SYSRQ=y")
            print("")
        elif args[0] in ["-v", "--version"]:
            print(VERSION)
    elif len(args) == 2:
        # Single line replace: "x=123" or "x+=2"
        filename = args[0]
        keyvalue = bs(args[1])
        if b"+=" in keyvalue:
            key, value = keyvalue.split(b"+=", 1)
            try:
                with open(filename, 'rb') as f:
                    data = f.read()
            except IOError:
                print("Can't read %s" % (filename))
                sysexit(2)
            datavalue = get_value(data, key)
            changefile(filename, key, inc(datavalue, value))
        elif b"-=" in keyvalue:
            key, value = keyvalue.split(b"-=", 1)
            try:
                with open(filename, 'rb') as f:
                    data = f.read()
            except IOError:
                print("Can't read %s" % (filename))
                sysexit(2)
            datavalue = get_value(data, key)
            changefile(filename, key, dec(datavalue, value))
        elif b"=" in keyvalue:
            key, value = keyvalue.split(b"=", 1)
            changefile(filename, key, value)
        else:
            sysexit(2)
    elif len(args) == 3:
        if args[0] in ["-a", "--add"]:
            # Single line replace/add ("x 123")
            filename = args[1]
            keyvalue = bs(args[2])

            create_if_missing(filename)

            assignment = None
            for ass in ASSIGNMENTS:
                if ass in keyvalue:
                    assignment = ass
                    break
            if not assignment:
                sysexit(2)
            _, value = keyvalue.split(assignment, 1)
            key = firstpart(keyvalue, False)

            # Change the file if possible, if not, add the key value
            if changefile(filename, key, value, dummyrun=True):
                changefile(filename, key, value)
            else:
                with open(filename, 'rb') as f:
                    data = f.read()
                if not has_key(data, key):
                    addtofile(filename, keyvalue)
        elif args[0] in ["-d", "--define"]:
            filename = args[1]
            keyvalue = bs(args[2])

            assignment = None
            for ass in ASSIGNMENTS:
                if ass in keyvalue:
                    assignment = ass
                    break
            if not assignment:
                sysexit(2)
            _, value = keyvalue.split(assignment, 1)
            key = firstpart(keyvalue, False)

            # Change the #define value in the file
            changefile(filename, key, value, define=True)
        elif args[0] in ["-u", "--uncomment"]:
            filename = args[1]
            keyvalue = bs(args[2])

            assignment = None
            for ass in ASSIGNMENTS:
                if ass in keyvalue:
                    assignment = ass
                    break
            if not assignment:
                sysexit(2)
            _, value = keyvalue.split(assignment, 1)
            key = firstpart(keyvalue, False)

            # Uncomment the key in the file, then try to set the value
            changefile(filename, key, value, uncomment_first=True)
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
                keyvalue = key + b"=" + value
                with open(filename, 'rb') as f:
                    data = f.read()
                if not has_key(data, key):
                    addtofile(filename, keyvalue)
        elif args[0] in ["-u", "--uncomment"]:
            filename = args[1]
            key = bs(args[2])
            value = bs(args[3])

            # Uncomment the key in the file, then try to set the value
            changefile(filename, key, value, uncomment_first=True)
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
