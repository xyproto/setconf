# -*- coding: utf-8 -*-

import os
from base64 import b64decode
import subprocess
from tempfile import mkstemp

from setconf import NL
from setconf import bs
from setconf import change
from setconf import changeline
from setconf import changefile
from setconf import change_multiline
from setconf import changefile_multiline
from setconf import main

def test_changeline():
    assert changeline(" // ost = 2", "3") == bs(" // ost = 2")
    assert changeline("rabbits = DUMB", "cool") == bs("rabbits = cool")
    assert changeline(
        "for ever and ever : never",
        "and ever") == bs("for ever and ever : and ever")
    assert changeline(
        "     for  ever  and  Ever   :=    beaver",
        "TURTLE") == bs("     for  ever  and  Ever   := TURTLE")
    assert changeline("CC=g++", "baffled") == bs("CC=baffled")
    assert changeline("CC =\t\tg++", "baffled") == bs("CC =\tbaffled")
    assert changeline("cabal ==1.2.3", "1.2.4") == bs("cabal ==1.2.4")
    assert changeline(
        "TMPROOT=${TMPDIR:=/tmp}",
        "/nice/pants") == bs("TMPROOT=/nice/pants")
    assert changeline("    # ost = 2", "3") == bs("    # ost = 2")

    assert changeline("  ost = 2", "3") == bs("  ost = 3")
    assert changeline("   /* ost = 2 */", "3") == bs("   /* ost = 2 */")
    assert changeline("æøå =>\t123", "256") == bs("æøå =>\t256")

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
    splitted = testcontent.split(NL)
    elements = change(splitted, "LIGHTS", "off")
    a = bytes.join(b"", elements)
    b = bytes.join(b"", testcontent_changed.split(NL))
    assert a == b

def test_changefile():
    # Test data
    testcontent = bs("keys := missing") + NL + bs("døg = found") + NL * 3 + bs("æøåÆØÅ") + NL
    testcontent_changed = bs("keys := found") + NL + \
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
    assert newcontent == testcontent_changed.split(NL)[:-1]

def test_change_multiline():
    # test 1
    testcontent = bs("keys := missing") + NL + bs("dog = found") + NL * 3
    testcontent_changed = bs("keys := found") + NL + bs("dog = found") + NL * 3
    a = change_multiline(testcontent, "keys", "found")
    b = testcontent_changed
    extracheck = testcontent.replace(bs("missing"), bs("found")) == testcontent_changed
    assert a == b
    assert extracheck

    # test 2
    testcontent = bs('blabla\nOST=(a\nb)\n\nblabla\nÆØÅ')
    testcontent_changed = bs('blabla\nOST=(c d)\n\nblabla\nÆØÅ')
    a = change_multiline(testcontent, "OST", "(c d)", ")")
    b = testcontent_changed
    assert a == b

    # test 3
    testcontent = bs('bläblä=1')
    testcontent_changed = bs('bläblä=2')
    a = change_multiline(testcontent, "bläblä", "2")
    b = testcontent_changed
    assert a == b

    # test 4
    testcontent = bs("\n")
    testcontent_changed = bs("\n")
    a = change_multiline(testcontent, "blablañ", "ost")
    b = testcontent_changed
    assert a == b

    # test 5
    testcontent = bs("")
    testcontent_changed = bs("")
    a = change_multiline(testcontent, "blabla", "ost")
    b = testcontent_changed
    assert a == b

    # test 6
    testcontent = bs("a=(1, 2, 3")
    testcontent_changed = bs("a=(1, 2, 3")
    a = change_multiline(testcontent, "a", "(4, 5, 6)", ")", verbose=False)
    b = testcontent_changed
    assert a == b

    # test 7
    testcontent = bs("a=(1, 2, 3\nb=(7, 8, 9)")
    testcontent_changed = bs("a=(4, 5, 6)")
    a = change_multiline(testcontent, "a", "(4, 5, 6)", ")")
    b = testcontent_changed
    assert a == b

    # test 8
    testcontent = bs("a=(0, 0, 0)\nb=(1\n2\n3\n)\nc=(7, 8, 9)")
    testcontent_changed = bs("a=(0, 0, 0)\nb=(4, 5, 6)\nc=(7, 8, 9)")
    a = change_multiline(testcontent, "b", "(4, 5, 6)", ")")
    b = testcontent_changed
    assert a == b

    # test 9
    testcontent = bs("a=(0, 0, 0)\nb=(1\n2\n3\n)\nc=(7, 8, 9)\n\n")
    testcontent_changed = bs("a=(0, 0, 0)\nb=(1\n2\n3\n)\nc=(7, 8, 9)\n\n")
    a = change_multiline(testcontent, "b", "(4, 5, 6)", "]", verbose=False)
    b = testcontent_changed
    assert a == b

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
    assert a == b

    # test 11
    testcontent = bs("x=(0, 0, 0)\nCHEESE\nz=2\n")
    testcontent_changed = bs("x=(4, 5, 6)\nz=2\n")
    a = change_multiline(testcontent, "x", "(4, 5, 6)", "CHEESE", verbose=False)
    b = testcontent_changed
    assert a == b

    # test 12
    testcontent = bs("# md5sum=('abc123')\nmd5sum=('def456')\nmd5sum=('ghi789')\n")
    testcontent_changed = bs("# md5sum=('abc123')\nmd5sum=('OST')\nmd5sum=('ghi789')\n")
    a = change_multiline(testcontent, "md5sum", "('OST')", "\n", verbose=False)
    b = testcontent_changed
    assert a == b

def test_changefile_multiline():
    # Test data
    testcontent = bs("keys := missing") + NL + bs("dog = found") + NL * 3 + bs("æøåÆØÅ")
    testcontent_changed = bs("keys := found") + NL + bs("dog = missing") + NL * 3 + bs("æøåÆØÅ")
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
    assert newcontent == testcontent_changed

# Note that this test function may cause sysexit to be called if it fails
# because it calls the main function directly


def test_addline():
    # --- TEST 1 ---
    testcontent = bs("# cache-ttl=65000") + NL + bs("MOO=yes") + NL
    testcontent_changed = bs("# cache-ttl=65000") + NL + bs("MOO=no") + NL + \
        bs("X=123") + NL + bs("Y=345") + NL + bs("Z:=567") + NL + \
        bs("FJORD => 999") + NL + bs('vm.swappiness=1') + \
        NL + bs("cache-ttl=6") + NL
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
    testcontent_changed2 = bs("x=2") + NL
    filename = mkstemp()[1]
    # Write an empty testfile
    open(filename, 'wb+').close()
    # Change the file by adding keys and values
    main(["-a", filename, "x=2"])
    # Read the file
    with open(filename, 'rb') as f:
        newcontent2 = f.read()

    # Do the tests
    assert newcontent == testcontent_changed
    assert newcontent2 == testcontent_changed2

def test_latin1():
    # Test data
    testcontent = b64decode(
        bs("SGVsbG8sIHRoaXMgaXMgYW4gSVNPLTg4NTktMSBlbmNvZGVkIHRleHQgZmlsZS4gQmzlYuZyIG9n\nIHL4ZHZpbi4KCkFsc28sCng9Nwo="))
    testcontent_changed = b64decode(
        bs("SGVsbG8sIHRoaXMgaXMgYW4gSVNPLTg4NTktMSBlbmNvZGVkIHRleHQgZmlsZS4gQmzlYuZyIG9n\nIHL4ZHZpbi4KCkFsc28sCng9NDIK"))

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
    assert newcontent == testcontent_changed.split(NL)[:-1]

def test_integration():
    """ Run the tests in the testcases subfolder """
    here = os.path.abspath(os.path.dirname(__file__))
    testcases = os.path.join(here, "testcases")
    test_sh = os.path.join(testcases, "test.sh")
    process = subprocess.Popen([test_sh], cwd=testcases,
                               stdout=subprocess.PIPE)
    out, _ = process.communicate()
    assert process.returncode == 0
    assert not bs("FAILED") in out
