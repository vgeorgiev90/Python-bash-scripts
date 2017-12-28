#!/usr/bin/python

import string
import collections
import getpass

##### Variables #########

chars = string.ascii_letters + string.digits + string.punctuation
temp = collections.OrderedDict()

###### Functions ########

def code_calculation(code):
    int_list = [int(i) for i in str(code)]
    first_op = [(i**2 + 2*i + i) for i in int_list]
    total = 0
    for i in first_op:
        total = total + i
    if total > 94:
        while total > 94:
            total = total - 94
    return total


def init():
    code = getpass.getpass('Enter code: ')
    count = 0
    for i in chars:
        temp[i] = count
        count = count + 1
    total = code_calculation(code)
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

def file_code(file,mode,code):                     ## Code can be either 'encode' or 'decode'
    if mode == 'encode':
        with open(file,'r') as f:
            cont = f.read()
        content = cont.replace(' ','---')
        content2 = content.replace('\n','___')
        content3 = content2.replace('\t','===')
        new_data = content3
        for i in range(1,10):                      ## For stronger encoding use more iterations
            old_data = encode(new_data,code)
            new_data = old_data
        with open(file,'w') as f:
            f.write(new_data)
    elif mode == 'decode':
        with open(file,'r') as f:
            cont = f.read()
        new_data = cont
        for i in range(1,10):                      ## Also change them for decoding the file
            old_data = decode(new_data,code)
            new_data = old_data
        content2 = new_data.replace('---',' ')
        content3 = content2.replace('___','\n')
        content4 = content3.replace('===','\t')
        with open(file,'w') as f:
            f.write(content4)
    else:
        print "The functions takes only encode or decode as argument"
