#!/usr/bin/python
#Simple and basic password encoding

import string
import collections
import sys
import getpass

##### Variables #########

chars = string.ascii_letters + string.digits + string.punctuation
temp = collections.OrderedDict()

####### Functions ########

def init():
    print "Code may be up to 10 chars only digits.."
    print "String must be without spaces..."
    code = getpass.getpass('Enter code: ')
    parola = getpass.getpass('Enter the pass: ')
    count = 0
    for i in chars:
        temp[i] = count
        count = count + 1
    return parola,code

def code_check(code):
    total = 0
    for i in code:
        total = total + int(i)
    return total


def encode(parola,code):
    enc = []
    positions = []
    for i in parola:
        positions.append(temp[i])
    for i in positions:
        i = i + code
        if i >= 94:
            i = i - 94
        for key,value in temp.iteritems():
            if value == i:
                enc.append(key)
    enc_pass = ''.join(enc)
    return enc_pass


def decode(enc_pass,code):
    enc = []
    positions = []
    for i in enc_pass:
        positions.append(temp[i])
    for i in positions:
        i = i - code
        if i < 0:
            i = i + 94
        for key,value in temp.iteritems():
            if value == i:
                enc.append(key)
    dec_pass = ''.join(enc)
    return dec_pass

####### Script ##########


try:
    arg = sys.argv[1]
    if arg == '--encode':
        parola,code = init()
        total = code_check(code)
        pos = encode(parola,total)
        print pos
    if arg == '--decode':
        parola,code = init()
        total = code_check(code)
        pas = decode(parola,total)
        print pas
except IndexError:
    print "Usage:\n===================\n./hide.py --encode\n./hide.py --decode\n"
