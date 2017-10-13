#!/usr/bin/env python

import collections
import subprocess
import sys

command = subprocess.Popen(["netstat", "-tanp"], stdout=subprocess.PIPE)

output = command.stdout.read()

resultsrc = []
resultdst = []

######### Main Function ##########

def main( int ):
    try:
        for row in output.split('\n'):
            if int in row and not "0.0.0.0" in row:
                counter = 0
                red = row.split()[4]
                red2 = row.split()[3]
                IP = red.split(":")[0]
                IP2 = red2.split(":")[0]
                resultsrc.insert(counter, IP)
                resultdst.insert(counter, IP2)
                counter += 1
                count = collections.Counter(resultsrc)
                count2 = collections.Counter(resultdst)

        print("IP's connecting from: ")
        print("=======================")
        c1 = 0
        for i in count:
            string = str(count)
            SRC = string.split(",")[c1]
            ipsrc = SRC.split("'")[1]
            cosrc = SRC.split(":")[1]
            print(cosrc.split("}")[0] + "   ---   " + ipsrc)
            print("")
            c1 += 1

        print("IP connecting to: ")
        print("=================")

        c2 = 0
        for y in count2:
            string2 = str(count2)
            DST = string2.split(",")[c2]
            ipdst = DST.split("'")[1]
            codst = DST.split(":")[1]
            print(codst.split("}")[0] + "   ---   " + ipdst)
            print("")
            c2 += 1

    except NameError:
        print("Sorry there are now connections at the moment to port 80 or 443")

######### Script ###########

try:
    arg = sys.argv[1]
    port = arg.split("p")[1]
    main(port)

except IndexError:
    print("This script check number of connections to port 80 or 443")
    print("=========================================================")
    print("Usage: ")
    print("connections.py -p80 or -p443")
