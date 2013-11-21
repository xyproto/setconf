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
* Rewrite in Go?
* An option for removing the configuration value instead of using ''
* Refactor the code that is used for adding options with -a
* An option for removing both the key and the value

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
