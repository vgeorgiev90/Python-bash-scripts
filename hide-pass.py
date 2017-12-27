#!/usr/bin/python

import string
import collections
import argparse
import getpass


###### Parser ##########

parser = argparse.ArgumentParser(description='Basic password encoding based on digit key')
parser.add_argument('--encode','-e',type=str,metavar=("PASSWORD"), help='Provide the string to be encoded')
parser.add_argument('--decode','-d',type=str,metavar=("ENC-PASSWORD"), help='Provide encoded string to decode')
parser.add_argument('--file','-f',type=str, help='File to search for password, you can set search pattern in the script')
parser.add_argument('--version','-v',action='version', version="%(prog)s 2.0\nCode may be up to 10 chars only digits..\nString must be without spaces...")
args = parser.parse_args()

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
    return code

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

def file_act(file,search,replace):
    search = "password:'%s'" % search
    new_parola = "password:'%s'" % replace
    with open(file,'r') as f:
        cont = f.read()
    cont = cont.replace(search,new_parola)
    with open(file,'w') as f:
        f.write(cont)



########### Script #############


if args.file and args.encode:
    path = args.file
    code = init()
    total = code_check(code)
    parola = args.encode
    enc_pas = encode(parola,total)
    file_act(path,parola,enc_pas)
    print "Password encoded: %s" % enc_pas
elif args.file and args.decode:
    path = args.file
    code = init()
    total = code_check(code)
    parola = args.decode
    dec_pas = decode(parola,total)
    file_act(path,parola,dec_pas)
    print "Password decoded ready to use.."
else:
    print "To use -f option you must specify either decode or encode.."
    print "hide.py --help for more info..."
