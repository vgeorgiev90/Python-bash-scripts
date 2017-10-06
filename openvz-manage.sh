#!/bin/bash
#open vz container managment and monitoring script


####### Functions ##########



####### Container Managment #######

trafic-control () {

  in-trafic () {

  DEV=venet0
  tc qdisc del dev $DEV root
  tc qdisc add dev $DEV root handle 1: cbq avpkt 1000 bandwidth 100mbit
  tc class add dev $DEV parent 1: classid 1:1 cbq rate 256kbit allot 1500 prio 5 bounded isolated
  tc qdisc add dev $DEV parent 1:1 sfq perturb 10

}

out-trafic () {

  DEV2=eth0
  tc qdisc del dev $DEV2 root
  tc qdisc add dev $DEV2 root handle 1: cbq avpkt 1000 bandwidth 100mbit
  tc class add dev $DEV2 parent 1: classid 1:1 cbq rate 256kbit allot 1500 prio 5 bounded isolated
  tc qdisc add dev $DEV2 parent 1:1 sfq perturb 10

}

ddos-limit () {
  DEV=eth0
  iptables -I FORWARD 1 -o $DEV -s $1 -m limit --limit 200/sec -j ACCEPT
  iptables -I FORWARD 2 -o $DEV -s $1 -j DROP
}


if [ $1 == "--ddos" ]; then
  ddos-limit $2
else
  in-trafic
  out-trafic
fi

IP=$1

if [ ! -z $IP ]; then
  tc filter add dev venet0 parent 1: protocol ip prio 16 u32 match ip dst "$IP" flowid 1:1
  tc filter add dev eth0 parent 1: protocol ip prio 16 u32 match ip src "$IP" flowid 1:1
  echo "Bandwith filters are now applied.."
fi


}

cont-create () {
  clear
  PASS=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 12 | head -n 1)
  # Generate random 12 char alpna numeric string for root password

  echo "Hostname: "
  read HOST
  echo "IP address: "
  read IP
  echo "OS available templates $(ls -la /vz/template/cache/)"
  ID=$(expr `echo $IP | awk -F"." '{print $1 + $2 + $3 + $4}'` + 1000)
  echo "Disk space soft/hard limits in format (6G:8G): "
  read DISK
  SYSMEM=`free -h | head -2 | tail -1 | awk -F" " '{print $2}'`
  echo "RAM in megabytes (256M): "
  echo "The system is with total memory: $SYSMEM"
  echo "Please keep in mind when assigning"
  read RAM
  SW=`echo $RAM | grep -o '[0-9]\+'`
  SW2=`echo $RAM | grep -o '[a-zA-Z]\+'`
  SWAP=$(($SW * 2))
  PRP=$(($SW-($SW/4)))
  PRPs=$(($SW/2))

  vzctl create $ID --ostemplate centos-7 --config basic
  vzctl set $ID --hostname $HOST --save
  vzctl set $ID --ipadd $IP --save
  vzctl set $ID --nameserver 8.8.8.8 --save
  vzctl set $ID --onboot yes --save
  vzctl set $ID --iolimit 10 --save
  vzctl set $ID --vmguarpages $PRPs${SW2} --save
  vzctl set $ID --oomguarpages $PRPs${SW2} --save
  vzctl set $ID --privvmpages $PRPs${SW2}:$PRP${SW2} --save
  vzctl set $ID --userpasswd root:${PASS}
  vzctl set $ID --ram $RAM --swap $SWAP${SW2} --save
  vzctl set $ID --diskspace $DISK --save
  vzctl start $ID
  clear
  echo "Container is now created and running.."
  vzlist $ID
  echo "============================"
  echo "Root Password : $PASS "
  echo ""
}


cont-delete () {
 echo "Conatiner ID to delete: "
 read CONT

 vzctl stop $CONT
 if [ $? != '0' ]; then
   echo "Please double check the container ID"
 fi
 vzctl destroy $CONT > /dev/null
 echo "$CONT is now deleted"
 vzctl status $CONT

}

cont-suspend () {
 clear
 echo "Please make sure vzctp and vzrst modules are loaded"
 echo "modprobe vzcpt; modprobe vzrst"
 echo "==========================="
 echo "1 to Suspend container.. "
 echo "2 to Restore container.. "
 read CHOICE
case $CHOICE in
1)
 echo "Container ID to suspend"
 read CONTID
 vzctl chkpnt $CONTID > /dev/null
 echo "$CONTID is now suspended"
 ;;
2)
 echo "Container ID to restore"
 read CONTID
 vzctl restore $CONTID > /dev/null
 echo "$CONTID is now up and running"
 vzlist $CONTID
 ;;
*) echo "Only 1 or 2.."
 ;;
esac
}

############ Container Monitoring ############

load-check () {

  for CT in $(vzlist -H -o ctid); do
    VAR=`vzctl exec $CT uptime | awk -F" " '{print $10, $11, $12}'`
    VAR2=`echo $VAR | awk -F" " '{print $1}' | awk -F"." '{print $1}'`
    if [ $VAR2 -gt 5 ]; then
      tput setaf 1; echo "$CT $(vzlist -H $CT | awk -F" " '{print $5}')";echo $VAR ; tput sgr0
      echo "========================="
      echp ""
    else
      echo "$CT $(vzlist -H $CT | awk -F" " '{print $5}')"
      echo $VAR
      echo "========================="
      echo ""
    fi
  done
}


disk-check () {

  for CT in $(vzlist -H -o ctid); do
    VAR=`vzctl exec $CT df -h | head -2 | tail -1 | awk -F" " '{print $5}' | grep -o '[0-9]\+'`
    if [ $VAR -gt 90 ]; then
      tput setaf 1; echo "$CT $(vzlist -H $CT | awk -F" " '{print $5}')"; vzctl exec $CT df -h | head -2 | tail -1; tput sgr0
      echo "=========================="
      echo ""
    else
      echo "$CT $(vzlist -H $CT | awk -F" " '{print $5}')"
      vzctl exec $CT df -h | head -2 | tail -1
      echo "=========================="
      echo ""
    fi
  done
}

memory-check () {

  for CT in $(vzlist -H -o ctid); do
    USAGE=`vzctl exec $CT free -m | head -2 | tail -1 | awk -F" " '{print $3}'`
    FREE=`vzctl exec $CT free -m | head -2 | tail -1 | awk -F" " '{print $2}'`
    PERC=$(($USAGE*100/$FREE))
    if [ $PERC -gt 90 ]; then
      tput setaf 1; echo "$CT $(vzlist -H $CT | awk -F" " '{print $5}')"; vzctl exec $CT free -h | head -2; tput sgr0
      echo "=========================="
      echo ""
    else
      echo "$CT $(vzlist -H $CT | awk -F" " '{print $5}')"
      vzctl exec $CT free -h | head -2
      echo "=========================="
      echo ""
    fi
done
}

trafic-check () {

  for CT in $(vzlist -H -o ctid); do
    echo ""
    echo "==========================="
    echo "$CT $(vzlist -H $CT | awk -F" " '{print $5}')"
    TRIN=`vzctl exec $CT cat /proc/net/dev | grep venet0: | awk -F" " '{print $2}'`
    TROUT=`vzctl exec $CT cat /proc/net/dev | grep venet0: | awk -F" " '{print $10}'`
    echo "Traffic (send/receive): "
    echo "IN: $((($TRIN/1000)/1000)) MB"
    echo "OUT: $((($TROUT/1000)/1000)) MB"
  done
}


start () {
  clear
  echo "  OpenVZ control script usage:  "
  echo "================================"
  echo "--create - Create container"
  echo "--delete - Delete container"
  echo "--monitor - Monitor cont usage  "
  echo "--suspend - Suspend/restore cont"
  echo "--traffic-ctl - to set bd limits"
  echo "================================"

}

########### Script start #############


if [ $# -eq 0 ] || [ $# -gt 1 ]; then
  start
elif [ $1 == "--create" ]; then
  cont-create
elif [ $1 == "--delete" ]; then
  cont-delete
elif [ $1 == "--suspend" ]; then
  cont-suspend
elif [ $1 == "--traffic-ctl" ]; then
  echo "Trafic control script"
  echo "1) to limit packet per second for containers (to avoid ddos from cont) "
  echo "2) to set the filters per IP"
  read CH
  case $CH in
  1) echo "IP of the container: "
     read ADDRESS
     trafic-control --ddos $ADDRESS
     ;;
  2) echo "IP of the container: "
     read ADDRESS
     trafic-control $ADDRESS
     ;;
  *) echo "Only valid options please..." ;;
  esac
elif [ $1 == "--monitor" ]; then
  clear
  echo "What do you want to check"
  echo "1) load average"
  echo "2) disk usage  "
  echo "3) bandwith usage"
  echo "4) memory usage  "
  read CHOICE2

  case $CHOICE2 in
  1) load-check ;;
  2) disk-check ;;
  3) trafic-check ;;
  4) memory-check ;;
  *) echo "Please choose valid option" ;;
  esac
else
  echo "Please choose valid option"
  sleep 2; clear
  start
fi
