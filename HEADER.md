# Header information

The header is the first 0xF8 bytes of the file and is unencrypted. Changes
between files are most easily viewed in a hex editor.

Listed below are some of the important locations in the header.
There are various other parameters that can be left as default values.
Nobody cares if the font for the colour names is Arial or Calibri.

Some of the options require validation in the DAK GUI. For example, the
colour Jacquard options cannot be selected if the pattern contains too
few colours.

## Miscellaneous
* "Magic number" - location 0x00. 24 bit value 0x633744 ('D7c')
* Random number - location 0x3D. 16 bit word. used in obfuscation but can be set to 0x0000 without consequences

## Dimensions
* Height - locations 0x03 0x07. 16 bit word
* Width - locations 0x05 0x09 0x15. 16 bit word

## Knitting options
* location 0x2C=0x00 machine Fair Isle,
		0x01 machine Intarsia,
		0x02 machine 2 colour Jacquard,
                0x03 machine 3 colour Jacquard,
		0x04 machine 4 colour Jacquard,
		0x05 machine 5 colour Jacquard,
                0x06 machine 6 colour Jacquard,
		0x0C hand knitting,
		0x0E machine RS texture,
		0x0F machine WS texture
* location 0xEA=0x00 flat knit,
		0x01 circular knit
* location 0xE9=0x00 row 1 starts RHS,
		0x01 row 1 starts LHS
* location 0xEC=0x00 row 1 starts RS, 
		0x01 row 1 starts WS

## Hand knitting options
* location 0xEB=0x00 stocking stitch,
		0x01 rev stocking stitch,
		0x02 K garter stitch,
		0x03 P garter stitch

## Machine knitting options
* location 0xEE=0x00 colour changer off,
		0x01 colour changer on
