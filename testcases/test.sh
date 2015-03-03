#!/bin/sh

# TODO: Create one function for preparing and one for diffing+removing
#       temporary test files.

echo -n 'Testing PKGBUILD...'
rm -f PKGBUILD
cp PKGBUILD.orig PKGBUILD
../setconf.py PKGBUILD pkgname=asdfasdf
../setconf.py PKGBUILD pkgrel+=1
diff PKGBUILD PKGBUILD.correct && (echo 'ok'; rm -f PKGBUILD) || echo 'FAIL'

echo -n 'Testing testcase2...'
rm -f testcase2
cp testcase2.orig testcase2
../setconf.py testcase2 x+=2
../setconf.py testcase2 x-=3
../setconf.py testcase2 z+=1000
diff testcase2 testcase2.correct && (echo 'ok'; rm -f testcase2) || echo 'FAIL'

echo -n 'Testing nonewline...'
rm -f nonewline
cp nonewline.orig nonewline
../setconf.py nonewline x=3
diff nonewline nonewline.correct && (echo 'ok'; rm -f nonewline) || echo 'FAIL'

