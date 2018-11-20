#!/bin/bash

db="${1}"

pass=`cat /mnt/${db}.php | grep DB_PASSWORD | awk -F"'" '{print $4}'`

mysql -e "grant all on ${db}.* to '${db}'@'%' identified by '${pass}'"

mysql ${db} < /mnt/${db}.sql

if [ $? == 0 ];then
    rm /mnt/${db}.php -rf && rm /mnt/${db}.sql
fi
