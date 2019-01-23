Wrapper around cfssl and first go program

All generated files will be placed in directory /root/certificates so run with sudo or change
Flag -hostnames is optional

Usage:

generate CA
ssl -cmd ca -cname myCA -anames myOtherCAname 

generate Certificate with newly generated CA
ssl -cmd cert -cname myCert -anames OtherName -hostnames 127.0.0.1,10.0.11.120 -ca-type local

generate Certificate with existing CA
ssl -cmd cert -cname myCert -anames OtherNames -hostnames 127.0.0.1,10.0.0.0/24 -ca-type remote -ca /path/to/my/ca.crt -ca-key /path/to/my/ca.key
