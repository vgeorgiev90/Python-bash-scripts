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

    global fst, scd, trd, frd
    global fst2, scd2, trd2
    count = collections.Counter(spam).most_common(5)
    count2 = collections.Counter(spam2).most_common(5)
    try:
        print("Possible account sources...")
        print("===========================")
        fst2, scd2, trd2 = str(count2[0]), str(count2[1]), str(count2[2])
        print(fst2.split(",")[0] + "    =====>    " + fst2.split(",")[1])
        print(scd2.split(",")[0] + "    =====>    " + scd2.split(",")[1])
        print(trd2.split(",")[0] + "    =====>    " + trd2.split(",")[1])
        print("")
    except IndexError:
	try:
	    print("Only one possible account...")
	    fst2 = str(count2[0])
	    print(fst2.split(",")[0] + "    =====>    " + fst2.split(",")[1])
	    print("")
	except IndexError:
	    print("No spam scripts check mail accounts...")
    try:
        print("Possible mail sources...")
        print("===========================")
        fst, scd, trd, frd = str(count[0]), str(count[1]), str(count[2]), str(count[3])
        print(fst.split(",")[0] + "    =====>    " + fst.split(",")[1])
        print(scd.split(",")[0] + "    =====>    " + scd.split(",")[1])
        print(trd.split(",")[0] + "    =====>    " + trd.split(",")[1])
        print(frd.split(",")[0] + "    =====>    " + frd.split(",")[1])
        print("")
    except IndexError:
	try:
	    print("Only one possible account...")
            fst = str(count[0])
            print(fst.split(",")[0] + "    =====>    " + fst.split(",")[1])
            print("")
	except IndexError:
	    print("No mail queue or something is wrong...")


def vivaweb_check():
    user1 = re.findall('@[a-zA-Z0-9-]{2,}.vivawebhost.com', fst)
    user2 = re.findall('@[a-zA-Z0-9-]{2,}.vivawebhost.com', scd)
    global acc1, acc2
    temp1 = fst.split("@")[0]
    temp2 = scd.split("@")[0]
    acc1 = temp1.split("'")[1]
    acc2 = temp2.split("'")[1]

    if user1 or user2:
	print("Check the following accounts.. ")
	print(acc1 + ",     " + acc2)
    elif user1:
	print(acc1)
    elif user2:
	print(acc2)


###################### Script ####################

queue_filter()
vivaweb_check()
