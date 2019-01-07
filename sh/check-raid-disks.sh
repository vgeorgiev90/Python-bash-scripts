#!/bin/bash


raid_type=$(lspci | grep -i raid | awk '{print $5}')

### Check the raid controller used

case $raid_type in

'LSI')
disks=$(megacli -AdpAllInfo -aALL | grep -C 9 -i "device present")
check=$(megacli -AdpAllInfo -aALL | grep -C 9 -i "device present" | grep -i failed | awk '{print $4}')
if [ ${check} -ne 0 ];then
/usr/sbin/sendmail mail@some.tld << EOF
Subject: Possible failed Disk on Raid status check
${disks}
EOF
fi
;;

'3ware')
disks=$(tw-cli /c0 show)
tw-cli /c0 show | grep -P "u\d" | grep -i degraded >/dev/null
if [ $? -eq 0 ];then
/usr/sbin/sendmail mail@some.tld << EOF
Subject: Possible failed Disk on Raid status check
${disks}
EOF
fi
;;

'Hewlett-Packard')
disks=$(ssacli ctrl all show config)
ssacli ctrl all show config | grep -i failed >/dev/null
if [ $? -eq 0 ];then
/usr/sbin/sendmail mail@some.tld << EOF
Subject: Possible failed Disk on Raid status check
${disks}
EOF
fi
;;

*)
        echo "No raid controller found"
;;

esac
