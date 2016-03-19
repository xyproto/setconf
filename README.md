setconf
=========

[![Build Status](https://travis-ci.org/xyproto/setconf.svg?branch=master)](https://travis-ci.org/xyproto/setconf)

Setconf is a small utility for changing settings in configuration textfiles.

Patches are welcome.


Compile time features
---------------------
* It can be compiled to native with <a href="http://nuitka.net/">nuitka</a>. Try these parameters: `--exe --lto --python-version=2.7`


TODO
----
* -u option for uncommenting a key while setting the value (removing "# "). Should uncomment by default?
* -c option for commenting out a key (adding "# ") or changing a key while keeping it as commented out.
* A way to change only the n'th occurence of a configuration option
* Add support for changing values of "#define" and "(setq" as well?
* Rewrite in Go?
* An option for removing the configuration value instead of using ''.
* Optimize the code that is used for adding options with -a.
* A way to add an option with -a after a given string occurs.
* An option for removing both the key and the value.
* Test and fix the combination of -a and multiline markers.
* Fix the behavior when " is the multiline marker and ":" the delimiter. (the yml format)
* Refactor

Changes from 0.7 to 0.7.1
-------------------------
* Removed a dependency on chardet

Changes from 0.6.8 to 0.7
-------------------------
* Fix issue #6, a failing testcase for `+=`.

Changes from 0.6.7 to 0.6.8
---------------------------
* Deal mainly with bytes instead of strings.
* Handle ISO-8859-1 (Latin1) better, for Python 3.

Changes from 0.6.6 to 0.6.7
---------------------------
* Can use floating point numbers together with `+=` and `-=`

Changes from 0.6.5 to 0.6.6
---------------------------
* Fixed a problem with files without newline endings

Changes from 0.6.4 to 0.6.5
---------------------------
* Can now use += or -= for increasing or decreasing integer values

Changes from 0.6.3 to 0.6.4
---------------------------
* Better error messages when write permissions are denied

Changes from 0.6.2 to 0.6.3
---------------------------
* Fixed a problem with -a that occurred when a key existed but was commented out
* Added regression test

Changes from 0.6.1 to 0.6.2
---------------------------
* Now runs on Python 2 and Python 3 (tested with 2.4, 2.5, 2.6, 2.7 and 3.3)

Changes from 0.6 to 0.6.1
-------------------------
* Fixed a problem with the -a option
* Creates the file when -a or --add is given, if needed

Changes from 0.5.3 to 0.6
-------------------------
* Made -a add options only when not already present

Changes from 0.5.2 to 0.5.3
---------------------------
* Made it compile with the latest version of shedskin
* Added an option -a for adding keys/values to a file

Changes from 0.5.1 to 0.5.2
---------------------------
* Fixed a problem with ascii/utf-8 encoding

Changes from 0.5 to 0.5.1
-------------------------
* Fixed a problem with => assignments
* Changed the way files are opened with open()
* Added more tests relating to ascii/utf-8

Changes from 0.4 to 0.5
-----------------------
* Add support for => as well
* Fixed a bug where comments were not ignored for multiline values
* New logo

Changes from 0.3.2 to 0.4 (released)
------------------------------------
* Ignored configuration options that are commented out


General information
-------------------

* License: GPL2
* Author: Alexander F Rødseth

