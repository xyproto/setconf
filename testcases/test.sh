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

P='/usr/bin/env python ../setconf.py'

start PKGBUILD
$P PKGBUILD pkgname=asdfasdf
$P PKGBUILD pkgrel+=1
complete PKGBUILD

start testcase2
$P testcase2 x+=2
$P testcase2 x-=3
$P testcase2 z+=1000
$P testcase2 d1-=.1
$P testcase2 d1+=0.3
$P testcase2 d2+=.02
$P testcase2 d2-=0.01
$P testcase2 s+=pie
$P testcase2 y-=0.31
complete testcase2

start nonewline
$P nonewline x=3
complete nonewline

start nonewline2
$P -a nonewline2 y=7
complete nonewline2

start aurutils
$P aurutils pkgrel+=1
complete aurutils

start printk
$P -d printk CONSOLE_LOGLEVEL_DEFAULT=4
complete printk

start kernel_config
$P -u kernel_config CONFIG_ULTRIX_PARTITION=y
complete kernel_config

start small
$P -u small f 42
complete small

start dropbear
$P -d dropbear SFTPSERVER_PATH='"/usr/bin/sftp-server"'
complete dropbear

start uncomment
$P -u uncomment Color
complete uncomment

echo -n 'Testing nonexisting...'
$P nonexisting x+=1 >/dev/null 2> error.log
grep Errno error.log \
  && (echo FAIL; cat error.log) \
  || (echo ok; rm -f error.log)

start multiline
$P multiline WARNFLAGS "-w" 's$'
complete multiline

start sh
$P sh name newvalue
complete sh
