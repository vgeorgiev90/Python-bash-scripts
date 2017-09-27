#!/bin/bash
# script to set up mysql master master configuration
# for single database


########## Functions ###################

mysql-install () {
  yum update -y
  yum install mariadb-server mariadb -y
[root@test ~]# vi mysql-replication.sh
[root@test ~]# clear
[root@test ~]# cat mysql-replication.sh
#!/bin/bash
# script to set up mysql master master replication
# for single database


########## Functions ###################

mysql-install () {
  yum update -y
  yum install mariadb-server mariadb -y
  systemctl start mariadb
  systemctl enable mariadb
  /usr/bin/mysqladmin -u root password 'viktor123'
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
  INS=`grep -n "socket=/var/lib/mysql/mysql.sock" /etc/my.cnf | awk -F":" '{print $1}'`
  LINE=$(expr $INS + 1)
  sed -i '$LINEi server-id  = $ID' /etc/my.cnf
  sed -i '$LINEi log_bin = /var/log/mariadb/mariadb-bin.log' /etc/my.cnf
  sed -i "$LINEi binlog_do_db = $DB" /etc/my.cnf
  systemctl restart mariadb
  echo "create user 'replica'@'%' identified by 'parolata';" | mysql
  echo "grant replication slave on *.* to 'replica'@'%';"
  echo "These are master log file and log position needed to set up the slave part"
  echo "=========================================================================="
  echo "show master status;" | mysql | awk -F" " '{print $1}' | tail -1`
  echo "show master status;" | mysql | awk -F" " '{print $2}' | tail -1`
}

mysql-slave-part () {
  echo "Provide the remote address of the other host: "
  read HOST
  echo "master log file on the remote server: "
  read FILE
  echo "Master log position on the remote server: "
  read POS
  echo "slave stop;" | mysql
  echo "change master to master_host = '${HOST}', master_user = 'replica', master_password = 'parolata', master_log_file = '${FILE}', master_log_pos = ${POS};" | mysql
  echo "slave start;" | mysql
}

start () {
echo "========================== Usage =============================="
echo "mysql.sh --install     -  to install mariadb server"
echo "mysql.sh --master-set  -  to set up master part for both servers"
echo "mysql.sh --slave-set   -  to set up slave part for both servers"
}

########### Script ################

if [ $? -eq 0 ] || [ $? -gt 1 ]; then
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
  echo "Set it for the remote server too to complete master master replication"
fi
