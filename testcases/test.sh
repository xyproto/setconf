#!/bin/sh

echo -n 'Testing PKGBUILD...'
rm -f PKGBUILD
cp PKGBUILD.orig PKGBUILD
../setconf.py PKGBUILD pkgname=asdfasdf
../setconf.py PKGBUILD pkgrel+=1
diff PKGBUILD PKGBUILD.correct && echo 'ok' || echo 'FAIL'
rm -f PKGBUILD

echo -n 'Testing testcase2...'
rm -f testcase2
cp testcase2.orig testcase2
../setconf.py testcase2 x+=2
../setconf.py testcase2 x-=3
../setconf.py testcase2 z+=1000
diff testcase2 testcase2.correct && echo 'ok' || echo 'FAIL'
rm -f testcase2
