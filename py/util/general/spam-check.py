#!/usr/bin/python
#spam checking script for exim mail server

import subprocess
import re
import collections


############## Functions #################

def queue_filter():

    proc = subprocess.Popen(['exim', '-bp'], stdout=subprocess.PIPE)
    word = proc.stdout.read()

    #regex patterns for mail account and user account

    #mail accounts example@example.com

    match = re.findall('([a-zA-Z0-9_.-]{2,}@[a-zA-Z0-9-]{2,}.[a-zA-Z0-9]{2,}.[a-zA-Z0-9]{2,})', word)

    #user accounts (username)

    match2 = re.findall('(\([a-zA-Z0-9_.-]{2,}\))', word)

    spam = []
    for row in match:
        counter = 0
        spam.insert(counter, row)
        counter += 1
    spam2 = []
    for row in match2:
        counter2 = 0
        spam2.insert(counter2, row)
        counter2 += 1

    global fst, scd
    global fst2, scd2
    count = collections.Counter(spam).most_common(5)
    count2 = collections.Counter(spam2).most_common(5)
    try:
        fst2, scd2 = str(count2[0]), str(count2[1])
    except IndexError:
        try:
            fst2 = str(count2[0])
        except IndexError:
            print("No spam scripts check mail accounts...")
    try:
        fst, scd = str(count[0]), str(count[1])
    except IndexError:
        try:
            fst = str(count[0])
        except IndexError:
            print("No mail queue or something is wrong...")


def vivaweb_check(user):
    regex = re.findall('@[a-zA-Z0-9-]{2,}.vivawebhost.com', user)
    if regex:
        account = user.split("@")[0]
        return account

def mail_strip(user):
    tmp = user.split(",")[0]
    tmp2 = tmp.split("'")[1]
    account = tmp2.split("'")[0]
    count = user.split(",")[1]
    count2 = count.split(")")[0]
    return account, count2

def acc_strip(user):
    tmp = user.split("'")[1]
    tmp2 = tmp.split("(")[1]
    account = tmp2.split(")")[0]
    count = user.split(",")[1]
    count2 = count.split(")")[0]
    return account, count2



###################### Script ####################

queue_filter()
ime, nomer = mail_strip(fst)
ime3, nomer3 = mail_strip(scd)
try:
    ime2, nomer2 = acc_strip(fst2)
    ime4, nomer4 = acc_strip(scd2)
    print ime2 + "   ====>  " + nomer2
    print ime4 + "   ====>  " + nomer4
    print ""
except NameError:
    print ""

test = vivaweb_check(ime)
test2 = vivaweb_check(ime3)
if test:
    print "Check the following account..   " + test
    print ""
    print "grep cwd /var/log/exim_mainlog|grep -v /var/spool|awk -F\"cwd=\" '{print $2}'|awk '{print $1}'|sort|uniq -c|sort -n | grep username"
if test2:
    print "Check the following account..   " + test2

print ""
print ""
print ime + "   ====>   " + nomer
print ime3 + "    ====>  " + nomer3
print ""

