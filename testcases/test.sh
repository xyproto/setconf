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
../setconf.py PKGBUILD pkgname=asdfasdf
../setconf.py PKGBUILD pkgrel+=1
complete PKGBUILD

start testcase2
../setconf.py testcase2 x+=2
../setconf.py testcase2 x-=3
../setconf.py testcase2 z+=1000
../setconf.py testcase2 d1-=.1
../setconf.py testcase2 d1+=0.3
../setconf.py testcase2 d2+=.02
../setconf.py testcase2 d2-=0.01
../setconf.py testcase2 s+=pie
../setconf.py testcase2 y-=0.31
complete testcase2

start nonewline
../setconf.py nonewline x=3
complete nonewline

start nonewline2
../setconf.py -a nonewline2 y=7
complete nonewline2

start aurutils
../setconf.py aurutils pkgrel+=1
complete aurutils

start printk
../setconf.py -d printk CONSOLE_LOGLEVEL_DEFAULT=4
complete printk

start kernel_config
../setconf.py -u kernel_config CONFIG_ULTRIX_PARTITION=y
complete kernel_config

start small
../setconf.py -u small f 42
complete small

start dropbear
../setconf.py -d dropbear SFTPSERVER_PATH='"/usr/bin/sftp-server"'
complete dropbear

start uncomment
../setconf.py -u uncomment Color
complete uncomment

echo -n 'Testing nonexisting...'
../setconf.py nonexisting x+=1 >/dev/null 2> error.log
grep Errno error.log \
  && (echo FAIL; cat error.log) \
  || (echo ok; rm -f error.log)

start multiline
../setconf.py WARNFLAGS "-w" 's\n'
complete multiline
