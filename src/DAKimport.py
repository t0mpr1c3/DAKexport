#!/usr/bin/python3

import sys
import numpy as np
from collections import Counter
from PIL import Image
# import png


def signExt_b2d(x):
    return (((x & 0xFF) ^ 0x80) - 0x80) & 0xFFFFFFFF

def getByteAt(data, i):
    return data[i] & 0xFF

def getWordAt(data, i):
    return getByteAt(data, i) + (getByteAt(data, i + 1) << 8)

def getDWordAt(data, i):
    return getWordAt(data, i) + (getWordAt(data, i + 2) << 16)

## Pascal-style string
def getStringAt(data, i):
    size = getByteAt(data, i)
    return data[i + 1:i + size + 1].decode()


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

## end of STPBlock class definition


class DAKPatternConverter:

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
        # self.max_row_colors = 0
        # self.col1 = 0
        # self.col2 = 0x3C ## '<'
        # self.status = 0
        self.debug = False

    def __read_data(self, filename):
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

    def __find_col1(buffer, start):
        pos = start
        for i in range(0x47):
            if buffer[pos] & 0x50 == 0x50:
                return i
            else:
                pos += 0x19
        return 0x20 ## default value for col1

    ## block of color data after pattern block = 1775 bytes = 0x47 * 0x19
    def __read_colors(self, buf, start):
        pos = start
        for i in range(0x47):
            b = buf[pos:pos + 0x1A]
            # if b[0] & 0x10 and b[1] > 0: ## works for .pat file
            if b[0] & 0x10: ## works for .stp file
                new_color = DAKColor(binary = b)
                # self.colors[b[1]] = new_color ## works for .pat file
                self.colors[i] = new_color ## works for .stp file
                if self.debug:
                    print("new_color '{}' {}".format(chr(i), new_color.string()))
            pos += 0x19

    ## block of stitch data after pattern block = 96 bytes = 0x30 * 2
    def __read_stitches(self, buf, start):
        pos = start
        for i in range(0x30):
            k = buf[pos + 1]
            if k != 0:
                j = buf[pos]
                x = (buf[4 * j + 3] & 0xF) | ((k & 5) << 4)
                new_stitch = DAKStitch(i + 1, j, k, buf[4 * j], buf[4 * j + 1], buf[4 * j + 2], buf[4 * j + 3], x)
                self.stitches[i + 1] = new_stitch
                if self.debug:
                    print(f"new_stitch {new_stitch.string()}")
            pos += 2

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
        # self.status = return_code
        # sys.exit(self.status)
        sys.exit(return_code)

    # read DAK .pat file and return a PIL.Image object
    def pat2im(self, filename):
        ## constants
        dst_pos = 0x10
        pattern_start = 0x165
        #
        ## read data
        input_data = self.__read_data(filename)
        input_size = len(input_data)
        #
        ## check data
        self.__check_header(input_data[0:3], (b'D4C', b'D6C'))
        self.__check_dims(input_data, 0x13A, 0x13C, 500, 800)
        # self.status = 0
        #
        ## decode run length encoding of color pattern
        ## count colors
        self.color_pattern = np.zeros((self.height, self.width,), np.uint8)
        pos = pattern_start
        # all_colors = set()
        for row in range(self.height):
            row_colors = set()
            column = 0
            while column < self.width:
                run = 1
                color = getByteAt(input_data, pos)
                pos += 1
                if color & 0x80:
                    run = color & 0x7F
                    color = getByteAt(input_data, pos)
                    pos += 1
                # all_colors.add(color)
                # row_colors.add(color)
                if run > 0:
                    for i in range(run):
                        self.color_pattern[row, column] = color
                        column += 1
            # self.max_row_colors = max(self.max_row_colors, len(row_colors))
        #
        ## no stitch data
        self.stitch_pattern = np.zeros((self.height, self.width), np.uint8)
        #
        ## get base color
        # b151 = getByteAt(input_data, 0x151)
        # if b151:
        #     self.col1 = np.int8(b151) + 0x100
        # else:
        #     self.col1 = 0
        # self.col2 = getByteAt(input_data, 0x152)
        #
        ## calculate return code
        # b15A = getByteAt(input_data, 0x15A)
        # if b15A == 0x0E or b15A == 0x0F:
        #     self.status = 0
        # else:
        #     self.status = b15A
        # if self.status == 0 or \
        # self.status < self.max_row_colors or \
        # self.max_row_colors > 2:
        #     self.status = self.max_row_colors
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
        ## block of color data after pattern block = 1775 bytes = 0x47 * 0x19
        if pos < input_size:
            # if self.col1 == 0:
                # self.col1 = find_col1(input_data, pos)
            self.__read_colors(input_data, pos)
            #
            ## get additional information, 6 bytes per row
            ## I don't know what these data represent
            pos += 1775
            if pos < input_size - 6 and \
            bytes(input_data[pos:pos + 6]) != b'Arial' and \
            input_data[pos:pos + 6] != bytearray(6):
                extension = 6 * self.height
                self.extension = input_data[pos:pos + extension]
        #
        ## color information before pattern block
        if pos == input_size or len(self.colors) == 0:
            # if self.col1 == 0:
                # self.col1 = Counter(color_array).most_common(1)[0][0]
            color = 0
            for i in range(0x80):
                a = getByteAt(input_data, i + 3)
                if a != 0xFF:
                    color += 1
                    pos = 3 * (a & 0xF)
                    # b = 3 * (self.getByteAt(i + 0x84) & 0xF)
                    new_color = DAKColor(
                        0x10 + 0x40 * ((self.col1 & 0xFF) == i),
                        color,
                        chr(i),
                        "",
                        getByteAt(input_data, 0x107 + pos),
                        getByteAt(input_data, 0x106 + pos),
                        getByteAt(input_data, 0x105 + pos))
                    self.colors[i] = new_color
                    if self.debug:
                        print("new_color {}".format(new_color.string()))
        # if self.debug:
            # print(f"col1 {hex(self.col1)}")
        #
        ## no information on stitch types
        ## done
        # return self.status
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

    # read DAK .stp file and return de-obfuscated data
    def stp2dat(self, filename):
        self.__decode_stp(filename)
        return self.output_data

    # read DAK .stp file and return a PIL.Image object
    def stp2im(self, filename):
        self.__decode_stp(filename)
        return self.__output_im()

    # deobfuscate DAK .stp file
    def __decode_stp(self, filename):

        def __decrypt_blocks(pos):
            blocks = []
            while True:
                block = STPBlock(input_data, pos, xorkey)
                blocks.append(block)
                pos += block.size + 4
                if block.height == self.height:
                    return blocks, pos

        # decode run length encoding of color and stitch patterns
        def __decode_runs(data, blocks, offset):
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
                    # if offset:
                        # symbol = getByteAt(data, offset + symbol * 2 - 2)
                    if run > 0:
                        for i in range(run):
                            output[row, column] = symbol
                            column += 1
            return output

        ## constants
        color_blocks_start = 0xF8
        color_data_size = 1775 ## 71 colors * 25 bytes
        #
        ## read data
        input_data = self.__read_data(filename)
        #
        ## check data
        self.__check_magic(input_data[0:3], (b'D7c',))
        self.__check_dims(input_data, 3, 5, 500, 3000)
        # self.status = 0
        #
        ## calculate key for decryption
        xorkey = self.__calc_key(input_data)
        #
        ## decrypt data blocks
        color_blocks, stitch_blocks_start = __decrypt_blocks(color_blocks_start)
        stitch_blocks, color_data_start = __decrypt_blocks(stitch_blocks_start)
        stitch_data_start = color_data_start + color_data_size
        if self.debug:
            print("start of color data {}".format(hex(color_data_start)))
            print("start of stitch data {}".format(hex(stitch_data_start)))
        #
        ## get pattern, color, and stitch data
        self.color_pattern = __decode_runs(input_data, color_blocks, 0)
        self.stitch_pattern = __decode_runs(input_data, stitch_blocks, color_data_size)
        self.__read_colors(input_data, color_data_start)
        self.__read_stitches(input_data, stitch_data_start)
        # if self.debug:
            # print(input_data[stitch_data_start:stitch_data_start+0x100])
            # print(self.colors)
        #
        ## output data
        self.output_data = input_data[0:0xF8] + bytearray(self.color_pattern) + bytearray(self.stitch_pattern) + input_data[
            color_data_start:stitch_data_start] + input_data[stitch_data_start:stitch_data_start + 96]
        #
        # return self.status

    # accepts de-obfuscated data and returns DAK .stp file
    def dat2stp(self, input_data):

    # def __init__(self, buffer, start, xorkey = None):
    #     self.height = getWordAt(buffer, start)
    #     self.size = getWordAt(buffer, start + 2)
    #     if xorkey != None:
    #         self.data = bytearray(self.size)
    #         for i in range(self.size):
    #             self.data[i] = buffer[start + 4 + i] ^ xorkey[i]
    #     else:
    #         self.data = buffer[start + 4:start + 4 + self.size]

        def __encrypt_blocks(pos):
            blocks = []
            while True:
                block = STPBlock(input_data, pos, xorkey)
                blocks.append(block)
                pos += block.size + 4
                if block.height == self.height:
                    return blocks, pos

            # perform run length encoding of color and stitch patterns
            def __encode_runs(data, blocks, offset):
                length = 0
                for row in range(self.height):
                    length += blocks[row].size + 4
                output = np.zeros(length, np.uint8)
                pos = 0
                for row in range(self.height):
                    s = block[row].size
                    putWordAt(output, pos, block[row].height)
                    putWordAt(output, pos, s)
                    for i in range(s):
                        output[pos + 4 + i] = block[row].data[i]
                    pos += s
                return output

        ## constants
        color_blocks_start = 0xF8
        color_data_size = 1775 ## 71 colors * 25 bytes
        #
        ## check data
        self.__check_magic(input_data[0:3], (b'D7c',))
        self.__check_dims(input_data, 3, 5, 500, 3000)
        # self.status = 0
        #
        ## calculate key for decryption
        xorkey = self.__calc_key(input_data)
        #
        ## encrypt data blocks
        color_blocks, stitch_blocks_start = __encrypt_blocks(color_blocks_start)
        stitch_blocks, color_data_start = __encrypt_blocks(stitch_blocks_start)
        stitch_data_start = color_data_start + color_data_size
        if self.debug:
            print("start of color data {}".format(hex(color_data_start)))
            print("start of stitch data {}".format(hex(stitch_data_start)))
        #
        ## get pattern, color, and stitch data
        self.color_pattern = __encode_runs(input_data, color_blocks, 0)
        self.stitch_pattern = __encode_runs(input_data, stitch_blocks, color_data_size)
        # if self.debug:
            # print(input_data[stitch_data_start:stitch_data_start+0x60])
            # print(self.colors)
        #
        ## output data
        self_output_data = input_data[0:0xF8] + bytearray(self.color_pattern) + bytearray(self.stitch_pattern) + input_data[
            color_data_start:stitch_data_start] + input_data[stitch_data_start:stitch_data_start + 96]
        #
        # return self.status
        self.__decode_stp(filename)
        return self.output_data

# end of DAKPatternConverter class definition
