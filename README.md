# DAKexport
Export DAK9 `.stp` files

A collaboration between [Agnes Cameron](https://github.com/agnescameron)
and [Tom Price](https://github.com/t0mpr1c3/).

## Aim

The goal is to write knitting patterns as `.stp` files compatible with
recent versions of [Designaknit](https://softbyte.co.uk/), so that
patterns written by other means can be used by people who have access
to that software.

## Tasks

Progress has already been made on decoding the proprietary format 
(see https://github.com/t0mpr1c3/DAKimport). There is an initial header
of 0xF8 bytes whose content is mostly unknown. Following that is a block
of colour data, one byte per stitch, whose content is mostly known. A
second block of stitch data, again one byte per stitch, is unknown. The
data are then obfuscated to produce a compact binary file.

A series of experiments will be necessary to discover the header format
and stitch codes.

I will make a start on Python module to perform the obfuscation, which
is the reverse of the de-obfuscation done by `DAKimport`.

## Input

For this to be useful it needs to be able to work with various different
input formats. I don't have firm suggestions how best to go about this.
There are various projects that have attempted to design open source pattern
formats. The most useful are Knitspeak and Knitout because there are already
people developing applications for them (see for example
https://github.com/mhofmann-uw/599-Knitting-Complete).

I have come up with a format called [Knitscheme](https://github.com/t0mpr1c3/knitscheme)
which is essentially a generalisation of Knitspeak to multiple yarns. It is
currently possible to input multicolour `.png` files. I am planning to write
a parser for Knitspeak in the near future.

My tentative suggestion is to use Knitscheme an intermediary format, at least
initially, so that we can test pipelines from `.png` files and Knitspeak to
Designaknit. This would take advantage of existing pattern collections
(e.g. https://github.com/AllYarnsAreBeautiful/ayab-patterns, https://stitch-maps.com/patterns/).
