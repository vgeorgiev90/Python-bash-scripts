#!/bin/bash
# Script to check IPs with most requests perdoamin for period of time
# 1. Suphp log check for 3 accounts with most file hits
# 2. Search domain for this accounts in httpd.conf
# 3. Search trough domain's access log for IP's with more than 10 connections for 20 seconds
# 4. Temporary block on found IP's


###### Vars ######
SUPHP=`tail -1000 /var/log/apache2/suphp_log |awk '{print $8}' |sort -n |uniq -c |sort -k1nr |head -3 | awk -F" " '{print $2}' | awk -F"\"" '{print $2}' | awk -F"\"" '{print $1}'`
LOG_DIR='/var/log/apache2/domlogs'


############ Functions ###########

domain_search() {
    DIR=${1}
    SEARCH=`echo $DIR | awk -F"/[A-Za-z1-9]{1,}.php" '{print $1}'`

# Search in httpd.conf for domain name with account found in suphp.log directory paths are trimmed if needed until match is found

    for i in `seq 1 8`;do
        if [ -z ${SEARCH} ];then
            break
        else
        DOMAIN_LINE_NUMBER=`cat /etc/apache2/conf/httpd.conf | grep -n $SEARCH | grep "DocumentRoot" | awk -F":" '{print $1}' | head -1`
        if [ -z ${DOMAIN_LINE_NUMBER} ];then
            PART=`echo $SEARCH | awk -F"/" '{print $NF}'`
            SEARCH=${SEARCH%/$PART}
        else
            LINE=$(($DOMAIN_LINE_NUMBER - 2))
            DOMAIN=`head -$LINE /etc/apache2/conf/httpd.conf | tail -1 | awk -F" " '{print $2}'`
            break
        fi
        fi
    done
    echo $DOMAIN >> domains.txt
}


ip_to_block () {
    LOG=${LOG_DIR}/${1}
    IPS=`tail -1000 $LOG | awk -F" " '{print $1}'`
# Check is made for only 1000 lines in the domain access log
    for ip in `echo $IPS`;do
        DATE=`tail -1000 $LOG | grep $ip | awk -F" " '{print $4}' | awk -F"[" '{print $2}' | awk -F":" '{print $2":"$3":"$4}' | awk -F":" '{print ($1 * 3600) + ($2 * 60) + $3}'`

        CHECK=$ip" "$DATE

# sec = 20 - connections per 20 seconds can be changed if needed, all access times found for the IPs are turned in seconds for better calculation
        echo $CHECK | awk '{sec = 20;cnt = 0;check = ($2 + sec);for (i=2;i<=NF;i++)  if ($i <= check) cnt = cnt + 1}END{if (cnt >= 10) print $1}' >> block-ip.txt
# cnt - number of connections for the IP within the time period
    done
}

# The function is for csf firewall it can be changed for other firewall applications or iptables directly
firewall_block () {
    for i in `cat block-ip.txt | sort | uniq`;do
        csf -td $i
    done
}

clean () {
   rm -rf domains.txt
   rm -rf block-ip.txt
}

########### Script ###########
clean 2>/dev/null

if [ -z ${1} ];then
    for dir in `echo $SUPHP`;do
        domain_search $dir
    done
    for dom in `cat domains.txt`;do
        ip_to_block $dom
    done
    firewall_block
# Option to provide domain manually
else
    dom=${1}
    ip_to_block $dom
    firewall_block
fi
