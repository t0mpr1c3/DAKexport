# DAKexport

A collaboration between [Agnes Cameron](https://github.com/agnescameron)
and [Tom Price](https://github.com/t0mpr1c3/).

## Aim

The goal is to encode knitting patterns as `.stp` files compatible with
recent versions of [Designaknit](https://softbyte.co.uk/) (DAK) so that
patterns written by other means can be used by people who have access
to that software.

The priority is making patterns usable for people with domestic-market
knitting machines from brands like Brother and Silver Reed.

## Status

Progress has already been made on decoding the proprietary format 
(see [DAKimport](https://github.com/t0mpr1c3/DAKimport)). There is an
initial header of 0xF8 bytes whose important content is known. Following
that are blocks of run-length encoded colour data whose contents reference 
a panel of colour data. This is followed by blocks of stitch data, encoded
in a similar way. The raw data are obfuscated to produce a compact binary file.

Tom has written a Python module that can perform and reverse the obfuscation.
Also, the stitch codes have been largely documented with the exception of
cable stitches.

One thing that has not been investigated yet is how memo information is encoded.

## Input

For this to be useful it needs to be able to work with various different
input formats. I don't have firm suggestions how best to go about this.
The absence of a clear alternative is one reason why `.stp` files are a
useful format for publication and exchange.

There are various projects that have attempted to design open source pattern
formats. The most useful are Knitspeak and Knitout because there are already
people developing applications for them (see for example
https://github.com/mhofmann-uw/599-Knitting-Complete).

I have come up with a format called [Knitscheme](https://github.com/t0mpr1c3/knitscheme)
which is essentially a generalisation of Knitspeak to multiple yarns. It is
currently possible to input multicolour `.png` files. I am planning to write
a parser for Knitspeak in the near future.

My tentative suggestion is to use Knitscheme as an intermediate format, at least
initially, so that we can test pipelines from `.png` files and Knitspeak to
DAK. This would take advantage of existing pattern collections
(e.g. https://github.com/AllYarnsAreBeautiful/ayab-patterns, https://stitch-maps.com/patterns/).
