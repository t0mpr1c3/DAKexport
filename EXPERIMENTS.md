A series of experiments will be required to reverse engineer the file format.

An experiment might proceed something like this:

* Create a small test pattern in DAK and record all the steps taken to make it
so that it can be recreated exactly.

* Make a small change to the pattern by varying one option or altering one stitch.

* Deobfuscate the `.stp` file and examine to see how the contents have changed.

* Repeat until we have learned how these stitches are encoded under different pattern options.  


Experiments can also be performed in the reverse direction. For example, the header
can be edited directly to verify the meaning of header codes in the resulting file.
