#!/bin/bash
#install suphp and set up vhosts also install different php versions


##########functions start#############

install () {

yum install httpd-devel -y
yum groupinstall 'Development Tools' -y
yum update -y
yum install epel-release -y
yum install -y bzip2-devel curl-devel libjpeg-devel libpng-devel freetype-devel libc-client-devel libmcrypt-devel openssl openssl-devel libxml2 libxml2-devel sqlite-devel libc-client

}


suphp_check () {
  if [ ! -f "/etc/suphp.conf" ] ; then
    mkdir /tmp/suphp && cd /tmp/suphp
    wget http://suphp.org/download/suphp-0.7.2.tar.gz
    tar -xzvf suphp-0.7.2.tar.gz
    wget -O suphp.patch https://lists.marsching.com/pipermail/suphp/attachments/20130520/74f3ac02/attachment.patch
    patch -Np1 -d suphp-0.7.2 < suphp.patch
    cd suphp-0.7.2
    autoreconf -if
    sleep 5
    
    ./configure --prefix=/usr/ --sysconfdir=/etc/ --with-apr=/usr/bin/apr-1-config --with-apache-user=apache --with-setid-mode=paranoid --with-logfile=/var/log/httpd/suphp_log --with-apxs=/usr/bin/apxs

    make && make install
    cp /etc/httpd/conf/httpd.conf /etc/httpd/conf/httpd.conf.back
    echo "LoadModule suphp_module modules/mod_suphp.so" >> /etc/httpd/conf/httpd.conf 
    
cat > /etc/suphp.conf << EOF
[global]
;Path to logfile
logfile=/var/log/httpd/suphp.log
;Loglevel
loglevel=info
;User Apache is running as
webserver_user=apache
;Path all scripts have to be in
docroot=/
;Path to chroot() to before executing script
;chroot=/mychroot
; Security options
allow_file_group_writeable=false
allow_file_others_writeable=false
allow_directory_group_writeable=false
allow_directory_others_writeable=false
;Check wheter script is within DOCUMENT_ROOT
check_vhost_docroot=true
;Send minor error messages to browser
errors_to_browser=false
;PATH environment variable
env_path=/bin:/usr/bin
;Umask to set, specify in octal notation
umask=0022
; Minimum UID
min_uid=100
; Minimum GID
min_gid=100

[handlers]
;Handler for php-scripts

;Handler for CGI-scripts
x-suphp-cgi="execute:!self"
EOF
    
    mkdir /etc/httpd/conf.d/virthost
    echo "IncludeOptional conf.d/virthost/*.conf" >> /etc/httpd/conf/httpd.conf
    
    echo "SuPHP is now installed"
  else
    echo "SuPHP is already installed on this system proceeding..."
  fi
}

virtual_host_add () {
  IP=`ifconfig | grep inet | tail -1 | awk -F" " '{print $2}'`
  if ! grep $1 /etc/passwd ; then
    echo "$1 account is not created please add it first"
  else
    chmod 711 /home/$1
	mkdir -p /home/$1/public_html && chmod 755 /home/$1/public_html
    chown -R ${1}: /home/$1/

cat > /etc/httpd/conf.d/virthost/$2.conf << EOF
<VirtualHost 1.1.1.1:80>
 DocumentRoot /home/www/public_html
 ServerName example.com
 ServerAdmin webmaster@example.com
 
 <FilesMatch ".+\.ph(p[345]?|t|tml)$">
 SetHandler None
 </FilesMatch>
 
 <IfModule mod_suphp.c>
 suPHP_Engine on

 suPHP_AddHandler application/x-httpd-suphp
 suPHP_UserGroup test test
 </IfModule>
</VirtualHost>
EOF
   sed -i "s/ServerName example.com/ServerName $2/g" /etc/httpd/conf.d/virthost/$2.conf
   sed -i "s/1.1.1.1:80/${IP}:80/g" /etc/httpd/conf.d/virthost/$2.conf
   sed -i "s/\/home\/www\/public_html/\/home\/$1\/public_html/g" /etc/httpd/conf.d/virthost/$2.conf
   sed -i "s/suPHP_UserGroup test test/suPHP_UserGroup $1 $1/g" /etc/httpd/conf.d/virthost/$2.conf

   
   echo "Please choose php version to use with :"
   echo 'to change betwen php versions please use :AddHandler application/x-httpd-php$VER .php .php3 .php4 .php5 .php7 in your .htaccess file'
   echo "Virtual Host $2 is now created.."
  fi
}

php_install () {
    echo "Which version of php to install: 5.5 , 5.6 , 7.0"
    read VER
    NATIVE=`php -v | head -1 | awk -F" " {'print $2'} | cut -d. -f 1,2`
    if [ $VER == $NATIVE ]; then
      echo "$VER is already installed"
    else
      mkdir /tmp/php
      cd /tmp/php

      wget --user viktor --password  http://78.142.63.159/files/php-$VER.tar.bz2
      wget --user viktor --password  http://78.142.63.159/files/phpconf.txt
      
      sed -i "s/--prefix=\/usr\/local\/php/--prefix=\/usr\/local\/php${VER}\//g" /tmp/php/phpconf.txt
      sed -i "s/--exec-prefix=\/usr\/local\/php/--exec-prefix=\/usr\/local\/php${VER}\//g" /tmp/php/phpconf.txt
    
    tar -xjf php-$VER.*
    cd php-$VER.*
    ./configure `cat /tmp/php/phpconf.txt` && make && make install
    fi
    if [ ! -d "/usr/local/php$VER" ]; then
       echo "The installation of php$VER failed please check.."
    else
       echo "PHP$VER is now installed.."
    fi
    
    rm -rf /tmp/php/
}

suphp_conf () {

  LINE=`grep -n ";Handler for php-scripts" /etc/suphp.conf | awk -F: '{print $1}'`
  ADD=$(expr $LINE + 1)
  if ! grep -w "application/x-httpd-php$VER" /etc/suphp.conf ; then
    sed -i "${ADD}i application/x-httpd-php${VER}=\"php:/usr/local/php${VER}/bin/php-cgi\"" /etc/suphp.conf
  else
    echo "All must be configured with suphp.conf"
  fi
  echo "<Directory />" >> /etc/httpd/conf.d/php$VER.conf
  echo "    suPHP_AddHandler application/x-httpd-php${VER}" >> /etc/httpd/conf.d/php$VER.conf
  echo "</Directory>" >> /etc/httpd/conf.d/php$VER.conf

}

start () {
  clear
  echo "This script installs suPHP and PHP versions 5.5, 5.6, 7.0"
  echo "======================================================================="
  echo "Usage: "
  echo "--suphp-install  -  Install suPHP apache module"
  echo "--virt-host-add  -  Add new virtual host entry provide user and domain"
  echo "--php-install    -  Install one of the supported php versions"
  echo "--install-deps   -  Install all of the dependancies          "
  echo "======================================================================="
}


####### Script Start ##########

if [ "$#" -eq '0' ]; then
  start
elif [ "$1" == "--suphp-install" ]; then
  suphp_check
  systemctl restart httpd
  echo 'Ready suPHP installed..'
elif [ "$1" == "--virt-host-add" ]; then
  if [ "$#" -eq '1' ] && [ "$#" -eq '2' ] && [ "$#" -gt '3' ]; then
    echo 'Please use  --virtual-host-add username domain.com'
  else
    virtual_host_add $2 $3
	echo "$3.conf is now created in /etc/httpd/conf.d/"
	systemctl restart httpd
  fi
elif [ "$1" == "--php-install" ]; then
  suphp_check
  php_install
  suphp_conf
  systemctl restart httpd
elif [ "$1" == "--install-deps" ]; then
  install
  echo "All deps are now installed"
fi

echo "All finished..."
