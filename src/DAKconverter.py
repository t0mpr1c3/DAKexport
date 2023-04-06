#!/usr/bin/python env

import sys
import numpy as np
from collections import Counter
from PIL import Image


def signExt_b2d(x):
    return (((x & 0xFF) ^ 0x80) - 0x80) & 0xFFFFFFFF

def getByteAt(data, i):
    return data[i] & 0xFF

def getWordAt(data, i):
    return getByteAt(data, i) + (getByteAt(data, i + 1) << 8)

def getDWordAt(data, i):
    return getWordAt(data, i) + (getWordAt(data, i + 2) << 16)

def putWordAt(data : bytearray, i, x):
    data[i] = x & 0xFF
    data[i + 1] = x >> 8

## Pascal-style string
def getStringAt(data, i):
    size = getByteAt(data, i)
    return data[i + 1:i + size + 1].decode()

# run length encoding of color and stitch patterns
def rle(input : bytes, offset = 0):
    n = len(input)
    output = bytearray(n)
    value = input[0] + offset
    run = 0x81
    i = 1 # index of input data
    j = 0 # index of output data
    while i < n:
        next_value = input[i] + offset
        if value == next_value:
            run += 1
            i += 1
            if run == 0xFF:
                output[j] = run
                output[j + 1] = value
                if i == n:
                    return output[:j + 2]
                j += 2
                i += 1
                run = 0x81
        else:
            if run == 0x81:
                output[j] = value
                j += 1
            else:
                output[j] = run
                output[j + 1] = value
                j += 2
                i += 1
                run = 0x81
                value = next_value
    if run == 0x81:
        output[j] = value
        return output[:j + 1]
    output[j] = run
    output[j + 1] = value
    return output[:j + 2]


class DAKColor:

    def __init__(self, code = 0x10, n = None, symbol = "", name = "",
        r = np.uint8(), g = np.uint8(), b = np.uint8(), binary = None):
        if binary != None:
            self.code = getByteAt(binary, 0)
            self.n = getByteAt(binary, 3)
            self.symbol = getByteAt(binary, 1)
            self.name = getStringAt(binary, 9)
            self.rgb = bytearray([getByteAt(binary, 6), getByteAt(binary, 7), getByteAt(binary, 8)])
        else:
            self.code = code
            self.n = n
            self.symbol = symbol
            self.name = name
            self.rgb = bytearray([r, g, b])

    def string(self):
        return ("{0}, {1}, '{2}', '{3}', {4}") \
        .format(hex(self.code), str(self.n), chr(self.symbol), self.name,
            hex(int.from_bytes(self.rgb, 'big')))

## end of DAKColor class definition


class DAKStitch:

    def __init__(self, i, j, k, a, b, c, d, e):
        self.i = i
        self.j = j
        self.k = k
        self.a = a
        self.b = b
        self.c = c
        self.d = d
        self.e = e

    def string(self):
        return ("{0}: {1} {2}, {3} {4} {5} {6}, {7}") \
        .format(hex(self.i), hex(self.j), hex(self.k), hex(self.a), hex(self.b),
            hex(self.c), hex(self.d), hex(self.e))

## end of DAKStitch class definition


class STPBlock:

    def __init__(self, buffer, start, xorkey = None):
        self.height = getWordAt(buffer, start)
        self.size = getWordAt(buffer, start + 2)
        if xorkey != None:
            self.data = bytearray(self.size)
            for i in range(self.size):
                self.data[i] = buffer[start + 4 + i] ^ xorkey[i]
        else:
            self.data = buffer[start + 4:start + 4 + self.size]

    def raw(self):
        return bytearray([
            self.height & 0xFF, 
            self.height >> 8, 
            self.size & 0xFF, 
            self.size >> 8]) + self.data

## end of STPBlock class definition


class DAKPatternConverter:

    # constants
    pat_max_x = 500
    pat_max_y = 800
    stp_max_x = 2000
    stp_max_y = 3000
    header_size = 0xF8
    max_colors = 71
    color_size = 25
    color_data_size = max_colors * color_size ## 1775
    color_gap = 13 ## color numbers below 13 don't work
    max_stitches = 48
    stitch_size = 2
    stp_magic = b'D7c'
    symbol_offset = 0x20

    def __init__(self, debug = True):
        self.filename = None
        self.height = None
        self.width = None
        self.color_pattern = bytearray()
        self.stitch_pattern = bytearray()
        self.extension = bytearray()
        self.output_data = bytearray()
        self.colors = {}
        self.stitches = {}
        self.debug = False

    def __read_file(self, filename):
        self.__init__()
        self.filename = filename
        if self.debug:
            print("filename {}".format(self.filename))
        file = open(self.filename, "rb")
        if file is None:
            self.__exit("file not found", -3)
        data = file.read()
        file.close()
        size = len(data)
        if self.debug:
            print("input size {} bytes".format(hex(size)))
        return data

    def __check_magic(self, header, magic_numbers):
        if self.debug:
            print("header {}".format(header))
        if header not in magic_numbers:
            self.__exit("file header not recognized", -4)

    def __check_dims(self, data, w_pos, h_pos, w_max, h_max):
        self.width = getWordAt(data, w_pos)
        self.height = getWordAt(data, h_pos)
        if self.debug:
            print("width {}".format(self.width))
            print("height {}".format(self.height))
        if self.width > w_max or self.height > h_max:
            self.__exit("dimensions are too big", -2)

    ## block of color data after pattern block = 1775 bytes = 71 colors * 25 bytes
    def __read_colors(self, buf, start):
        pos = start
        for i in range(self.max_colors):
            b = buf[pos:pos + 0x1A]
            # if b[0] & 0x10 and b[1] > 0: ## works for .pat file
            if b[0] & 0x10: ## works for .stp file
                new_color = DAKColor(binary = b)
                # self.colors[b[1]] = new_color ## works for .pat file
                self.colors[i] = new_color ## works for .stp file
                if self.debug:
                    print("new_color '{}' {}".format(chr(i), new_color.string()))
            pos += self.color_size

    ## block of stitch data after pattern block = 96 bytes = 48 stitches * 2 bytes
    def __read_stitches(self, buf, start):
        pos = start
        for i in range(self.max_stitches):
            k = buf[pos + 1]
            if k != 0:
                j = buf[pos]
                x = (buf[4 * j + 3] & 0xF) | ((k & 5) << 4)
                new_stitch = DAKStitch(i + 1, j, k, buf[4 * j], buf[4 * j + 1], buf[4 * j + 2], buf[4 * j + 3], x)
                self.stitches[i + 1] = new_stitch
                if self.debug:
                    print(f"new_stitch {new_stitch.string()}")
            pos += self.stitch_size

    def __output_png(self):
        rgb = [[num for element in [self.colors[self.color_pattern[self.height - row - 1, column]].rgb \
        for column in range(self.width)] for num in element] for row in range(self.height)]
        return png.from_array(rgb, mode = 'RGB')

    def __output_im(self):
        rgb = np.array([[self.colors[self.color_pattern[self.height - row - 1, column]].rgb \
        for column in range(self.width)] for row in range(self.height)],
        np.uint8)
        if self.debug:
            print(rgb, file=sys.stderr)
        return Image.fromarray(rgb, mode = 'RGB')

    def __exit(self, msg, return_code):
        print(msg)
        sys.exit(return_code)

    # read DAK .pat file and return a PIL.Image object
    def pat2im(self, filename):
        ## constants
        dst_pos = 0x10
        pattern_start = 0x165
        #
        ## read data
        input_data = self.__read_file(filename)
        input_size = len(input_data)
        #
        ## check data
        self.__check_header(input_data[0:3], (b'D4C', b'D6C'))
        self.__check_dims(input_data, 0x13A, 0x13C, self.pat_max_x, self.pat_max_y)
        #
        ## decode run length encoding of color pattern
        self.color_pattern = np.zeros((self.height, self.width,), np.uint8)
        pos = pattern_start
        for row in range(self.height):
            column = 0
            while column < self.width:
                run = 1
                color = getByteAt(input_data, pos)
                pos += 1
                if color & 0x80:
                    run = color & 0x7F
                    color = getByteAt(input_data, pos)
                    pos += 1
                if run > 0:
                    for i in range(run):
                        output[row, column] = color
                        column += 1
        #
        ## ignore stitch data
        self.stitch_pattern = np.zeros((self.height, self.width), np.uint8)
        #
        ## go to end of pattern block
        pos += 1
        while pos < input_size:
            pos += 1
            if getByteAt(input_data, pos - 1) == 0xFE:
                break
            pos += getByteAt(input_data, pos) + 1
            pos += getByteAt(input_data, pos) + 3
        if self.debug:
            print("pos {}".format(hex(pos)))
        #
        ## get color information
        if pos < input_size:
            self.__read_colors(input_data, pos)
            #
            ## get additional information, 6 bytes per row
            ## I don't know what these data represent
            pos += self.color_data_size
            if pos < input_size - 6 and \
            bytes(input_data[pos:pos + 6]) != b'Arial' and \
            input_data[pos:pos + 6] != bytearray(6):
                extension = 6 * self.height
                self.extension = input_data[pos:pos + extension]
        #
        ## color information before pattern block
        if pos == input_size or len(self.colors) == 0:
            color = 0
            for i in range(0x80):
                a = getByteAt(input_data, i + 3)
                if a != 0xFF:
                    color += 1
                    pos = 3 * (a & 0xF)
                    new_color = DAKColor(
                        0x10,
                        color,
                        chr(i),
                        "",
                        getByteAt(input_data, 0x107 + pos),
                        getByteAt(input_data, 0x106 + pos),
                        getByteAt(input_data, 0x105 + pos))
                    self.colors[i] = new_color
                    if self.debug:
                        print("new_color {}".format(new_color.string()))
        #
        ## done
        return self.__output_im()

    def __calc_key(self, data):

        def __appendKeystring(next_string, max_size):
            return (keystring + next_string)[0:max_size]

        max_xor_len = 21000
        key1 = (getDWordAt(data, 0x35) >> 1)
        key1 += (getWordAt(data, 0x3F) << 2)
        key1 += getDWordAt(data, 0x39) 
        key1 += getWordAt(data, 0x3D)
        key1 += getByteAt(data, 0x20);
        if self.debug:
            print("first key number {}".format(key1))
        salt1 = getWordAt(data, 0x39);
        salt2 = int((getDWordAt(data, 0x35) & 0xFFFF) > 0)
        keystring = getStringAt(data, 0x60)
        keystring = __appendKeystring(getStringAt(data, 0x41),    0x6E)
        keystring = __appendKeystring(str(getWordAt(data, 0x3D)), 0x7D) 
        keystring = __appendKeystring(str(getByteAt(data, 0x20)), 0x8C) 
        keystring = __appendKeystring(getStringAt(data, 0x41),    0xAA) 
        keystring = __appendKeystring(str(getByteAt(data, 0x20)), 0xB9) 
        keystring = __appendKeystring(str(getWordAt(data, 0x3D)), 0xC8)
        if self.debug:
            print("first key string '{}'".format(keystring))
        key2 = key1 
        for i in range(len(keystring)):
            b = ord(keystring[i]) // 2
            switch = (i + 1) % 3
            if switch == 0:
                temp = (salt2 + b) // 7
                key2 += (i + 1) * b + temp
            elif switch == 1:
                temp = b // 5 * getWordAt(data, 0x3F);
                key2 += (i + 1) * salt2;
                key2 += b * 6;
                key2 += temp;
            else: ## switch == 2
                key2 += (i + 1) * salt1;
                key2 += b * 4;
        if self.debug:
            print("second key number {}".format(key2))
        keystring = str(key2 * 3)
        keystring = __appendKeystring(str(key2),     0x1E)
        keystring = __appendKeystring(str(key2 * 4), 0x2D)
        keystring = __appendKeystring(str(key2 * 2), 0x3C)
        keystring = __appendKeystring(str(key2 * 5), 0x4B)
        keystring = __appendKeystring(str(key2 * 6), 0x5A)
        keystring = __appendKeystring(str(key2 * 8), 0x69)
        keystring = __appendKeystring(str(key2 * 7), 0x78)
        if self.debug:
            print("second key string '{}'".format(keystring))
        xorkey = bytearray(max_xor_len)
        for i in range(max_xor_len):
            index = (i + 1) % len(keystring)
            temp1 = ord(keystring[index]) & 0xFF
            temp2 = key2 % (i + 1) & 0xFF
            xorkey[i] = temp1 ^ temp2
        return xorkey

    # read DAK .stp file and return deobfuscated data
    def stp2dat(self, filename):
        self.deobfuscate(filename)
        return self.output_data

    # read DAK .stp file and return a PIL.Image object
    def stp2im(self, filename):
        self.deobfuscate(filename)
        return self.__output_im()

    # deobfuscate DAK .stp file
    def deobfuscate(self, filename):

        def __decrypt_blocks(pos):
            blocks = []
            while True:
                block = STPBlock(input_data, pos, xorkey)
                blocks.append(block)
                pos += block.size + 4
                if block.height == self.height:
                    return blocks, pos

        # decode run length encoding of color and stitch patterns
        def __decode_blocks(blocks):
            output = np.zeros((self.height, self.width), np.uint8)
            block_num = 0
            block_data = blocks[0].data
            pos = 0
            for row in range(self.height):
                if row == blocks[block_num].height:
                    block_num += 1
                    block_data = blocks[block_num].data
                    pos = 0
                column = 0
                while column < self.width:
                    run = 1
                    symbol = getByteAt(block_data, pos)
                    pos += 1
                    if symbol & 0x80:
                        run = symbol & 0x7F
                        symbol = getByteAt(block_data, pos)
                        pos += 1
                    if run > 0:
                        for i in range(run):
                            output[row, column] = symbol
                            column += 1

        ## read data
        input_data = self.__read_file(filename)
        #
        ## check data
        self.__check_magic(input_data[0:3], (self.stp_magic,))
        self.__check_dims(input_data, 3, 5, self.stp_max_x, self.stp_max_y)
        #
        ## calculate key for decryption
        xorkey = self.__calc_key(input_data)
        #
        ## decrypt data blocks
        color_blocks, stitch_blocks_start = __decrypt_blocks(self.header_size)
        stitch_blocks, color_data_start = __decrypt_blocks(stitch_blocks_start)
        stitch_data_start = color_data_start + self.color_data_size
        if self.debug:
            print("start of color data {}".format(hex(color_data_start)))
            print("start of stitch data {}".format(hex(stitch_data_start)))
        #
        ## get pattern, color, and stitch data
        self.color_pattern = __decode_blocks(color_blocks)
        self.stitch_pattern = __decode_blocks(stitch_blocks)
        self.__read_colors(input_data, color_data_start)
        self.__read_stitches(input_data, stitch_data_start)
        #
        ## output data
        data = bytearray(input_data[0:self.header_size]) ## header
        for i in range(len(color_blocks)):
            data += color_blocks[i].raw()
        for i in range(len(color_blocks)):
            data += stitch_blocks[i].raw()
        data += input_data[color_data_start:]   
        self.output_data = bytes(data)
        #
        # return self.status

    # accepts deobfuscated data and returns data in DAK .stp format
    def obfuscate(self, input_data):

        def __encode_blocks(data, blocks):
            length = 0
            for b in range(len(blocks)):
                length += blocks[b].size + 4
            output = np.zeros(length, np.uint8)
            pos = 0
            for b in range(len(blocks)):
                s = blocks[b].size
                putWordAt(output, pos, blocks[b].height)
                putWordAt(output, pos + 2, s)
                pos += 4
                output[pos:pos + s] = blocks[b].data
                pos += s
            return output

        def __encrypt_blocks(pos):
            blocks = []
            while True:
                block = STPBlock(input_data, pos, xorkey)
                blocks.append(block)
                pos += block.size + 4
                if block.height == self.height:
                    return blocks, pos

        ## check data
        self.__check_magic(input_data[0:3], (self.stp_magic,))
        self.__check_dims(input_data, 3, 5, self.stp_max_x, self.stp_max_y)
        #
        ## calculate key for decryption
        xorkey = self.__calc_key(input_data)
        #
        ## encrypt data blocks
        color_blocks, stitch_blocks_start = __encrypt_blocks(self.header_size)
        stitch_blocks, color_data_start = __encrypt_blocks(stitch_blocks_start)
        stitch_data_start = color_data_start + self.color_data_size
        if self.debug:
            print("start of color data {}".format(hex(color_data_start)))
            print("start of stitch data {}".format(hex(stitch_data_start)))
        #
        ## get pattern, color, and stitch data
        self.color_pattern = __encode_blocks(input_data, color_blocks)
        self.stitch_pattern = __encode_blocks(input_data, stitch_blocks)
        #
        ## output data
        self.output_data = input_data[0:self.header_size] + bytearray(self.color_pattern) + bytearray(self.stitch_pattern) + input_data[color_data_start:]
        #
        # return self.status
        return self.output_data

    ## return data in run-length-encoded blocks
    def __encode_data(self, data : bytes, offset=0):
        pos = 0
        buffer = bytearray(self.width * self.height)
        buffer_pos = 0
        row_start = 0
        for row in range(self.height):
            putWordAt(buffer, buffer_pos, row + 1)
            row_data = data[row_start:row_start + self.width]
            runs = rle(row_data, offset)
            runs_length = len(runs)
            putWordAt(buffer, buffer_pos + 2, runs_length)
            buffer_pos += 4
            buffer[buffer_pos:buffer_pos + runs_length] = runs
            buffer_pos += runs_length
            row_start += self.width
        return buffer[:buffer_pos]

    # input PIL.Image object and return data in DAK .stp format 
    def im2stp(self, im : Image, x_repeats = 1, y_repeats = 1):

        ## return color data in 25-byte blocks
        def __encode_palette(palette, num_colors):
            buffer = bytearray(self.color_data_size)
            buffer_pos = self.color_gap * self.color_size
            palette_pos = 0
            for color in range(num_colors):
                buffer[buffer_pos] = 0x10 ## code
                ##buffer[buffer_pos + 1] = color + self.symbol_offset ## symbol
                buffer[buffer_pos + 3] = color + self.color_gap ## number
                buffer[buffer_pos + 6:buffer_pos + 9] = palette[palette_pos:palette_pos + 3]
                palette_pos += 3
                buffer_pos += self.color_size
            return buffer

        header = bytearray(self.header_size)
        header[0:3] = self.stp_magic
        self.height = im.height
        self.width = im.width
        putWordAt(header, 0x03, self.width)
        putWordAt(header, 0x05, self.height)
        putWordAt(header, 0x07, self.width)
        putWordAt(header, 0x09 , self.height)
        putWordAt(header, 0x0B, x_repeats)
        putWordAt(header, 0x0D, y_repeats)
        header[0x2C] = 0x00 ## machine Fair Isle (max 2 colors per row)
        header[0x39] = 0x7B ## version
        header[0xD8] = 0x12 ## version
        header[0xE9] = 0x00 ## row 1 starts RHS
        header[0xEA] = 0x00 ## flat knit
        header[0xEE] = 0x02 ## colour changer off
        header[0xB1:0xB6] = b'Arial' # font
        im = im.quantize(colors=self.max_colors - self.color_gap).transpose(Image.ROTATE_180)
        image_data = list(im.getdata())
        num_colors = max(image_data) + 1
        #
        ## encode color and stitch data
        color_blocks = self.__encode_data(image_data, self.color_gap)
        stitch_blocks = self.__encode_data(im.width * im.height * b'\0', 1)
        #
        ## encode color palette
        color_data = __encode_palette(im.getpalette(), num_colors)
        #
        ## encode stitches
        stitch_data = bytearray(self.max_stitches * self.stitch_size)
        stitch_data[0] = 0x20 ## knit
        stitch_data[2] = 0x2E ## purl
        #
        ## pad end of file with zeros
        ## it doesn't matter how many zeros as long as there are enough
        ## increase padding if DAK returns 'range error' when the file is opened
        padding = bytes(1024)
        #
        ## output
        return self.obfuscate(header + color_blocks + stitch_blocks + color_data + stitch_data + padding)

# end of DAKPatternConverter class definition
