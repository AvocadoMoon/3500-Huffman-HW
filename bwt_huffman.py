import os
import sys
import marshal
import itertools
import argparse
import math
from operator import itemgetter
from functools import partial
from collections import Counter

try:
    import cPickle as pickle
except:
    import pickle

class node:
    def __init__(self, freq, symbol, left=None, right=None):
        self.freq = freq

        self.symbol = symbol

        self.left = left

        self.right = right

        self.huff = ""
    
    def findHuff(self, cha):
        st = ""
        if(self.symbol != cha):
            if ((self.left != None) & (self.right != None)):

                #if not none, go to left and right
                l = self.left.findHuff(cha)
                r = self.right.findHuff(cha)
                if (l != None):
                    st += str(l)
                    st += str(self.huff)
                    return st
                elif(r != None):
                    st += str(r)
                    st += str(self.huff)
                    return st
            
            #if right is not none
            elif (self.right != None):
                st += str(self.right.findHuff(cha))
                st += str(self.huff)
                return st
            
            #if left is not none
            elif (self.left != None):
                st += str(self.left.findHuff(cha))
                st += str(self.huff)
                return st

            #else return none
            else:
                return self.left
        else:
            return self.huff
        
    
    def findSymbol(self, c):
        i = 0
        substring = c[i]
        currentNode = self

        while(1):
            if (substring[i] == "0"):
                currentNode = currentNode.left
                if (currentNode.symbol != None):
                    return substring, currentNode.symbol
                i += 1
                substring += c[i]
            else:
                currentNode = currentNode.right
                if (currentNode.symbol != None):
                    return substring, currentNode.symbol
                i += 1
                substring += c[i]
            

        # if(self.right != None):
        #     if(str(self.right.huff) == substring):
        #         huff = str(self.right.huff)
        #         return huff, self.right.symbol
        
        # huff = str(self.left.huff)
        
        # while (1):
        #     if((substring == huff) & (currentNode.left.symbol != None)):
        #         return huff, currentNode.left.symbol
        #     if (currentNode.right != None):
        #         r = huff[:-1]
        #         r += "1"
        #     if (substring == r):
        #         return r, currentNode.right.symbol
        #     else:
        #         currentNode = currentNode.left
        #         huff += str(currentNode.huff)
        #         i += 1
        #         substring += c[i]
#Order is
#BWT, MTF, Huff, Compress

termchar = 17 # you can assume the byte 17 does not appear in the input file

# This takes a sequence of bytes over which you can iterate, msg, 
# and returns a tuple (enc,\ ring) in which enc is the ASCII representation of the 
# Huffman-encoded message (e.g. "1001011") and ring is your ``decoder ring'' needed 
# to decompress that message.
def encode(msg):
    #find probability of each letter in msg
    #make huffman tree out of probability
    #then encode message in binary using huffman tree


    nodes = []
    for c in range(256):
        
        n = msg.count(c)
        if (n != 0):
            print("n: {}, c: {}".format(n, c))
            nodes.append(node(n, c))
    
    while len(nodes) > 1:
        nodes = sorted(nodes, key= lambda x: x.freq)

        right = nodes[0]
        left = nodes[1]

        left.huff = 0
        right.huff = 1

        newNode = node(left.freq+right.freq, None, left, right)

        nodes.remove(left)
        nodes.remove(right)

        nodes.append(newNode)
    
    S = bytearray()
    byte_size = 8
    current = ""
    for c in msg:
        j = nodes[0].findHuff(c)
        j = j[::-1]
        while(len(j) != 0):
            while(len(current) != byte_size and len(j) != 0):
                current += j[0]
                j = j[1:]
            if (len(current) == byte_size):
                S.append(int(current, 2))
                current = ""
    n = len(current) % 8
    n = abs(8 - n)
    print(n)
    current += ("0" * n)
    if (len(current) != 0):
        S.append(int(current, 2))
    n = ord(str(n))
    S.append(n)
    
    
    #S = bytearray(S.encode())
    return S, nodes[0]

# This takes a string, cmsg, which must contain only 0s and 1s, and your 
# representation of the ``decoder ring'' ring, and returns a bytearray msg which 
# is the decompressed message. 
def decode(cmsg, decoderRing):
    # Creates an array with the appropriate type so that the message can be decoded.

    #keeps on looking in tree for code that works with current string, if none add length of search string by 1 and traverse down
    #huffman tree by 1. Once found remove serach string section from begining of string and start over
    byteMsg = bytearray()

    while len(cmsg) != 0:
        
        substring, byte = decoderRing.findSymbol(cmsg)

        byteMsg.append(byte)
        cmsg = cmsg[len(substring): ]

    
    return byteMsg

# This takes a sequence of bytes over which you can iterate, msg, and returns a tuple (compressed, ring) 
# in which compressed is a bytearray (containing the Huffman-coded message in binary, 
# and ring is again the ``decoder ring'' needed to decompress the message.
def compress(msg, useBWT):
    #take the binary msg and convert it into a byte array

    if useBWT:
        msg = bwt(msg)
        msg = mtf(msg)

    # Initializes an array to hold the compressed message.
    enc, huff = encode(msg)    
    return enc, huff

# This takes a sequence of bytes over which you can iterate containing the Huffman-coded message, and the 
# decoder ring needed to decompress it.  It returns the bytearray which is the decompressed message. 
def decompress(msg, decoderRing, useBWT):
    # Creates an array with the appropriate type so that the message can be decoded.
    S = "".join(format(x, '08b') for x in msg)
    n = S[-8:]
    n = int(n, 2)
    n = chr(n)
    n = int(n)
    print(n)
    S = S[: len(S) -8 -n]
    decompressedMsg = decode(S, decoderRing)

    print("done")
    
    # before you return, you must invert the move-to-front and BWT if applicable
    # here, decompressed message should be the return value from decode()
    if useBWT:
        decompressedMsg = imtf(decompressedMsg)
        decompressedMsg = ibwt(decompressedMsg)

    return decompressedMsg

# # memory efficient iBWT
def ibwt(msg):
    # I would work with a bytearray to store the IBWT output
    i = msg.index(termchar)
    msg = msg.decode()

    rotations = ['' for c in msg]
    for j in range(len(msg)):
        #insert the BWT as the first column
        rotations = sorted([c+rotations[i] for i, c in enumerate(msg)])
        print(j)
    #return the row ending in ‘$’
    s = termchar.to_bytes(1, byteorder='big').decode()
    msg = rotations[msg.index(s)]
    msg = msg[:-1]
    msg = bytearray(msg.encode())
    return msg

# Burrows-Wheeler Transform fncs
def radix_sort(values, key, step=0):
    sortedvals = []
    radix_stack = []
    radix_stack.append((values, key, step))

    while len(radix_stack) > 0:
        values, key, step = radix_stack.pop()
        if len(values) < 2:
            for value in values:
                sortedvals.append(value)
            continue

        bins = {}
        for value in values:
            bins.setdefault(key(value, step), []).append(value)

        for k in sorted(bins.keys()):
            radix_stack.append((bins[k], key, step + 1))
    return sortedvals
            
# memory efficient BWT
def bwt(msg):
    def bw_key(text, value, step):
        return text[(value + step) % len(text)]

    msg = msg + termchar.to_bytes(1, byteorder='big')

    bwtM = bytearray()

    rs = radix_sort(range(len(msg)), partial(bw_key, msg))
    for i in rs:
        bwtM.append(msg[i - 1])

    return bwtM[::-1]

# move-to-front encoding fncs
def mtf(msg):
    # Initialise the list of characters (i.e. the dictionary)
    dictionary = bytearray(range(256))
    
    # Transformation
    compressed_text = bytearray()
    rank = 0

    # read in each character
    for c in msg:
        rank = dictionary.index(c) # find the rank of the character in the dictionary
        compressed_text.append(rank) # update the encoded text
        
        # update the dictionary
        dictionary.pop(rank)
        dictionary.insert(0, c)

    #dictionary.sort() # sort dictionary
    return compressed_text # Return the encoded text as well as the dictionary

# inverse move-to-front
def imtf(compressed_msg):
    compressed_text = compressed_msg
    dictionary = bytearray(range(256))

    decompressed_img = bytearray()

    # read in each character of the encoded text
    for i in compressed_text:
        # read the rank of the character from dictionary
        decompressed_img.append(dictionary[i])
        
        # update dictionary
        e = dictionary.pop(i)
        dictionary.insert(0, e)
        
    return decompressed_img # Return original string

if __name__=='__main__':
    s = "hello"
    f = bytearray(s.encode())
    t = bwt(f)
    q = mtf(t)
    e, ring = compress(f, True)
    i = imtf(mtf(f))
    d = decompress(e, ring, True)



    # argparse is an excellent library for parsing arguments to a python program
    parser = argparse.ArgumentParser(description='<Insert a cool name for your compression algorithm> compresses '
                                                 'binary and plain text files using the Burrows-Wheeler transform, '
                                                 'move-to-front coding, and Huffman coding.')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-c', action='store_true', help='Compresses a stream of bytes (e.g. file) into a bytes.')
    group.add_argument('-d', action='store_true', help='Decompresses a compressed file back into the original input')
    group.add_argument('-v', action='store_true', help='Encodes a stream of bytes (e.g. file) into a binary string'
                                                       ' using Huffman encoding.')
    group.add_argument('-w', action='store_true', help='Decodes a Huffman encoded binary string into bytes.')
    parser.add_argument('-i', '--input', help='Input file path', required=True)
    parser.add_argument('-o', '--output', help='Output file path', required=True)
    parser.add_argument('-b', '--binary', help='Use this option if the file is binary and therefore '
                                               'do not want to use the BWT.', action='store_true')

    args = parser.parse_args()

    compressing = args.c
    decompressing = args.d
    encoding = args.v
    decoding = args.w


    infile = args.input
    outfile = args.output
    useBWT = not args.binary

    assert os.path.exists(infile)

    if compressing or encoding:
        fp = open(infile, 'rb')
        sinput = fp.read()
        fp.close()
        if compressing:
            msg, tree = compress(sinput,useBWT)
            fcompressed = open(outfile, 'wb')
            marshal.dump((pickle.dumps(tree), msg), fcompressed)
            fcompressed.close()
        else:
            msg, tree = encode(sinput)
            print(msg)
            fcompressed = open(outfile, 'wb')
            marshal.dump((pickle.dumps(tree), msg), fcompressed)
            fcompressed.close()
    else:
        fp = open(infile, 'rb')
        pck, msg = marshal.load(fp)
        tree = pickle.loads(pck)
        fp.close()
        if decompressing:
            sinput = decompress(msg, tree, useBWT)
        else:
            sinput = decode(msg, tree)
            print(sinput)
        fp = open(outfile, 'wb')
        fp.write(sinput)
        fp.close()