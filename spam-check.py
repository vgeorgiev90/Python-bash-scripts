#!/usr/bin/python
#spam checking script for exim mail server

import subprocess
import re
import collections


############## Functions #################

def queue_filter():

    proc = subprocess.Popen(['exima', '-bp'], stdout=subprocess.PIPE)
    word = proc.stdout.read()

    #regex patterns for mail account and user account

    match = re.findall('([a-zA-Z0-9_.-]{2,}@[a-zA-Z0-9-]{2,}.[a-zA-Z0-9]{2,}.[a-zA-Z0-9]{2,})', word)
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

    count = collections.Counter(spam).most_common(5)
    count2 = collections.Counter(spam2).most_common(5)
    print("Possible account sources...")
    print("===========================")
    fst2, scd2, trd2, frd2 = str(count2[0]), str(count2[1]), str(count2[2]), str(count2[3])
    print(fst2.split(",")[0] + "    =====>    " + fst2.split(",")[1])
    print(scd2.split(",")[0] + "    =====>    " + scd2.split(",")[1])
    print(trd2.split(",")[0] + "    =====>    " + trd2.split(",")[1])
    print(frd2.split(",")[0] + "    =====>    " + frd2.split(",")[1])
    print("")
    print("Possible mail sources...")
    print("===========================")
    fst, scd, trd, frd = str(count[0]), str(count[1]), str(count[2]), str(count[3])
    print(fst.split(",")[0] + "    =====>    " + fst.split(",")[1])
    print(scd.split(",")[0] + "    =====>    " + scd.split(",")[1])
    print(trd.split(",")[0] + "    =====>    " + trd.split(",")[1])
    print(frd.split(",")[0] + "    =====>    " + frd.split(",")[1])
    print("")


###################### Script ####################

queue_filter()
