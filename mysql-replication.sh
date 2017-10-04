#!/bin/bash
# script to set up mysql master master configuration
# for CentOS7 and MariaDB

########## Functions ###################

mysql-install () {
  yum update -y
  yum install mariadb-server mariadb -y
  systemctl start mariadb
  systemctl enable mariadb
  /usr/bin/mysqladmin -u root password 'viktor123'
  
  if [ ! -f "/etc/my.cnf" ]; then
    
cat > /etc/my.cnf << EOF
[mysqld]
datadir=/var/lib/mysql
socket=/var/lib/mysql/mysql.sock


# Disabling symbolic-links is recommended to prevent assorted security risks
symbolic-links=0
# Settings user and group are ignored when systemd is used.
# If you need to run mysqld under a different user or group,
# customize your systemd unit file for mariadb according to the

innodb_buffer_pool_size=32000000

[mysqld_safe]
log-error=/var/log/mariadb/mariadb.log
pid-file=/var/run/mariadb/mariadb.pid

#
# include all files from the config directory
#
!includedir /etc/my.cnf.d
EOF

fi

}

mysql-master-part () {

cat > .my.cnf << EOF
[client]
user=root
password=viktor123
EOF

  echo "Which database you want to replicate: "
  read DB
  echo "Provide id number of the server (1,2): "
  read ID
  echo "Provide the address of the other host: "
  read HOST
  INS=`grep -n "socket=/var/lib/mysql/mysql.sock" /etc/my.cnf | awk -F":" '{print $1}'`
  LINE=$(expr $INS + 1)
  sed -i "${LINE}i server-id  = ${ID}" /etc/my.cnf
  sed -i "${LINE}i log_bin = /var/log/mariadb/mariadb-bin.log" /etc/my.cnf
  sed -i "${LINE}i binlog_do_db = ${DB}" /etc/my.cnf
  systemctl restart mariadb
  echo "create user 'replica'@'${HOST}' identified by 'GHR234d';" | mysql
  echo "grant replication slave on *.* to 'replica'@'${HOST}' identified by 'GHR234d';" | mysql
  echo "These are master log file and log position needed to set up the slave part"
  echo "=========================================================================="
  echo "show master status;" | mysql | awk -F" " '{print $1}' | tail -1
  echo "show master status;" | mysql | awk -F" " '{print $2}' | tail -1
}

mysql-slave-part () {
  echo "Provide the address of the other host: "
  read HOST
  echo "Master log file on the remote server: "
  read FILE
  echo "Master log position on the remote server: "
  read POS
  echo "slave stop;" | mysql
  echo "change master to master_host = '${HOST}', master_user = 'replica', master_password = 'GHR234d', master_log_file = '${FILE}', master_log_pos = ${POS};" | mysql
  echo "slave start;" | mysql
}

start () {
echo "Script for Mysql master-master replication on CentOS 7"
echo "   1. Run master setup on both servers."
echo "   2. Run slave setup on both servers."
echo ""
echo "========================== Usage =============================="
echo "mysql.sh --install     -  to install mariadb server"
echo "mysql.sh --master-set  -  to set up master part"
echo "mysql.sh --slave-set   -  to set up slave part"
}

############## Script ################

if [ $# -eq 0 ] || [ $# -gt 1 ]; then
  clear
  start
elif [ $1 == '--install' ]; then
  mysql-install
elif [ $1 == '--master-set' ]; then
  mysql-master-part
  echo "Replication is now set for database $DB"
elif [ $1 == '--slave-set' ]; then
  mysql-slave-part
  echo "Slave part is now set for the server"
  echo "Run slave part on the remote server too to complete master-master replication"
else
  echo "Please provide valid options"
  sleep 2
  clear
  start
fi
