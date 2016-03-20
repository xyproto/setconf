#!/bin/sh

start() {
  filename=$1
  echo -n "Testing $filename..."
  rm -f "$filename"
  cp "$filename.orig" "$filename"
}

complete() {
  filename=$1
  diff "$filename" "$filename.correct" \
    && (echo 'ok'; rm -f "$filename") \
    || echo 'FAIL'
}

start PKGBUILD
../setconf.exe PKGBUILD pkgname=asdfasdf
../setconf.exe PKGBUILD pkgrel+=1
complete PKGBUILD

start testcase2
../setconf.exe testcase2 x+=2
../setconf.exe testcase2 x-=3
../setconf.exe testcase2 z+=1000
../setconf.exe testcase2 d1-=.1
../setconf.exe testcase2 d1+=0.3
../setconf.exe testcase2 d2+=.02
../setconf.exe testcase2 d2-=0.01
../setconf.exe testcase2 s+=pie
../setconf.exe testcase2 y-=0.31
complete testcase2

start nonewline
../setconf.exe nonewline x=3
complete nonewline

start nonewline2
../setconf.exe -a nonewline2 y=7
complete nonewline2

start aurutils
../setconf.exe aurutils pkgrel+=1
complete aurutils

echo -n 'Testing nonexisting...'
../setconf.exe nonexisting x+=1 >/dev/null 2> error.log
grep Errno error.log \
  && (echo FAIL; cat error.log) \
  || (echo ok; rm -f error.log)
