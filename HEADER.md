# Header information

The header is the first 0xF8 bytes of the file and is unencrypted. Changes
between files are most easily viewed in a hex editor.

Listed below are some of the important locations in the header.

Byte 0x20 and bytes 0x35 and up are used in obfuscation. Changing any of
these values will screw up the file.

Some of the options require validation in the DAK GUI. For example, the
colour Jacquard options cannot be selected if the pattern contains too
few colours.

## Dimensions
* Height - locations 0x03 0x07, 16 bit word
* Width - locations 0x05 0x09, 16 bit word

## Repeats
* Horizontal repeats - location 0x0B, 16 bit word
* Vertical repeats - location 0x0D, 16 bit word

## Knitting options
* location 0x2C=0x00 machine Fair Isle,
		0x01 machine Intarsia,
		0x02 machine 2 colour Jacquard,
                0x03 machine 3 colour Jacquard,
		0x04 machine 4 colour Jacquard,
		0x05 machine 5 colour Jacquard,
                0x06 machine 6 colour Jacquard,
		0x0C hand knitting,
		0x0E machine RS texture
		0x0F machine WS texture

* location 0xEA=0x00 flat knit,
		0x01 circular knit
* location 0xE9=0x00 row 1 starts RHS,
		0x01 row 1 starts LHS
* location 0xEC=0x00 row 1 starts RS, 
		0x01 row 1 starts WS

## Hand knitting options
* location 0xEB=0x00 stocking stitch,
		0x01 reverse stocking stitch,
		0x02 garter stitch (K),
		0x03 garter stitch (P)

## Machine knitting options
* location 0xEE=0x00 colour changer off,
		0x01 colour changer on

## Font
* location 0xB1=0x6C61697241 ('Arial')

## Miscellaneous
* "Magic number" - location 0x00=0x633744 ('D7c'),
* Version info (?) - 0x39=0x0000007B, 0xD8=0x12. Older files may have different values, e.g. 0x000003E7, 0x00.
* Random number - location 0x3D, 16 bit word