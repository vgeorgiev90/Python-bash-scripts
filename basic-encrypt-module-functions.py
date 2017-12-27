#!/usr/bin/python

import string
import collections
import getpass

##### Variables #########

chars = string.ascii_letters + string.digits + string.punctuation
temp = collections.OrderedDict()

###### Functions ########

def init():
    code = getpass.getpass('Enter code: ')
    count = 0
    for i in chars:
        temp[i] = count
        count = count + 1
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

def file_check(file,mode,code):
    if mode == 'encode':
        with open(file,'r') as f:
            cont = f.read()
        content = cont.replace(' ','---')
        content2 = content.replace('\n','___')
        content3 = encode(content2,code)
        with open(file,'w') as f:
            f.write(content3)
    elif mode == 'decode':
        with open(file,'r') as f:
            cont = f.read()
        content = decode(cont,code)
        content2 = content.replace('---',' ')
        content3 = content2.replace('___','\n')
        with open(file,'w') as f:
            f.write(content3)

