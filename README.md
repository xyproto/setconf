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
* Rewrite in Go?
* New logo?
* Add support for changing values of "#define" and "(setq" as well?

Changes from 0.4 to 0.5 (released)
----------------------------------
* Add support for => as well
* Fixed a bug where comments were not ignored for multiline values

Changes from 0.3.2 to 0.4 (released)
------------------------------------
* Ignores configuration options that are commented out
