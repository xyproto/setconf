setconf
=========

Setconf is a small utility for changing settings in configuration textfiles.

Patches are welcome.


Requirements
------------
* Python 2
* It can be compiled to native with <a href="http://nuitka.net/">nuitka</a>. Try these parameters: `--exe --lto --python-version=2.7`


TODO
----
* A way to change only the n'th occurence of a configuration option
* Add support for changing values of "#define" and "(setq" as well?
* Rewrite in Go?
* An option for removing the configuration value instead of using ''.
* Optimize the code that is used for adding options with -a.
* An option for removing both the key and the value.
* Test and fix the combination of -a and multiline markers.
* Make it behave like in Python 2 when running with Python 3 and changing an ISO-8859-1 file
* Refactor


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
