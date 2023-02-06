# DAKexport
Export DAK9 .stp files

Collaboration with [Agnes Cameron](https://github.com/agnescameron)

## Outline

The goal is to output knitting patterns as .stp files compatible with recent
versions of [Designaknit](https://softbyte.co.uk/).

## Input

For this to be useful it needs to be able to work with various different input
formats. I don't have firm suggestions how best to go about this. There are
various open source projects that have attempted to design open source pattern
formats. The most useful are Knitspeak and Knitout (see for example
[https://github.com/mhofmann-uw/599-Knitting-Complete], because there are
already people developing applications for them (see for example
https://github.com/mhofmann-uw/599-Knitting-Complete).

I have come up with a format called [Knitscheme](https://github.com/t0mpr1c3/knitscheme)
which is essentially a generalisation of Knitspeak to multiple yarns. It is
currently possible to input multicolour .png files. I am planning to write a parser
for Knitspeak in the neat future.

My suggestion is to use Knitscheme an intermediary format, at least initially, 
so that we can test pipelines from .png files and Knitspeak to Designaknit. This
would take advantage of existing pattern collections
(e.g. https://github.com/AllYarnsAreBeautiful/ayab-patterns, https://stitch-maps.com/patterns/).
