setconf
=========

Setconf is a small utility for changing settings in configuration textfiles.

Patches are welcome.

TODO
----
* A way to change the n'th occurence of a configuration option
* A way to change all occurences of a configuration option
* A way to insert a configuration option at the end of a file if
  the configuration option is missing
* Add support for changing values of "#define" and "(setq" as well?
* Manipulate bytes, not strings or lines
* Rewrite in Go

Changes from 0.5.1 to 0.5.2 (released)
------------------------------------
* Fixed a problem with ascii/utf-8 encoding

Changes from 0.5 to 0.5.1 (released)
------------------------------------
* Fixed a problem with => assignments
* Changed the way files are opened with open()
* Added more tests relating to ascii/utf-8

Changes from 0.4 to 0.5 (released)
----------------------------------
* Add support for => as well
* Fixed a bug where comments were not ignored for multiline values
* New logo

Changes from 0.3.2 to 0.4 (released)
------------------------------------
* Ignores configuration options that are commented out
