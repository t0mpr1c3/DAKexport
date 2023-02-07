A series of experiments will be required to reverse engineer the file format.

An experiment might proceed something like this:

* Create a small test pattern in DAK and record all the steps taken to make it
so that it can be recreated exactly.

* Make a small change to the pattern by varying one option or altering one stitch.

* Deobfuscate the `.stp` file and examine to see how the contents have changed.

* Repeat until we have learned how these stitches are encoded under different pattern options.  


Experiments can also be performed in the reverse direction. For example, the header
can be edited directly to verify the effect of header codes in the resulting file.

## Experiment 1: same size, different colour

I created two test files, both 48x60, one blue and one orange, and disassembled the hex. A diff shows that there are three main differences between the 2 files, all in the first part of the file. To experiment with changing the properties of the file, I tried changing one line/block at a time -- I took the blue file and substituted line 2, line 3, both lines 2 and 3, and lines 9-17, all separately.

All of these were read as invalid by DAK, indicating that there is probably some kind of hash/checksum functionality between lines 2 and 3 and the block.

<img width="1046" alt="Screenshot 2023-02-07 at 12 39 07" src="https://user-images.githubusercontent.com/16444898/217248666-673f905b-26e3-4501-89f0-40c1c973efee.png">

I don't think there's much of a pattern to be gleaned from the large block, other than its location, and beginning with `3c00780085` and ending in `100000300000b6ff7b`. In files of different sizes, this beginning is different and the block is of a different length (but the end remains the same) -- in a striped file of the same size the prefix is also the case, and the block is the same size.
