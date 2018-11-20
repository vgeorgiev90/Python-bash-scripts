#!/bin/bash

website="${1}"
domain="${2}"

rm /tmp/${website}.tgz -rf
rm /usr/share/nginx/html/* -rf 
#apt-get install wget -y
wget http://10.0.11.170/${website}.tgz -P /tmp
tar -xzf /tmp/${website}.tgz -C /usr/share/nginx/html --strip-components 1 
mv /usr/share/nginx/html/${website}.sql /mnt 
cp /usr/share/nginx/html/wp-config.php /mnt/${website}.php 
sed -i 's/10\..*\..*\..*/mysql-replica-0.mysql-replica.default.svc.cluster.local"/g' /usr/share/nginx/html/wp-config.json 

cat > /usr/share/nginx/html/example-com.conf << EOF
server {
listen 80;
server_name www.${domain} ${domain};
root   /usr/share/nginx/html;
index  index.php index.html index.htm;
include /etc/nginx/wordpress.conf;
include /etc/nginx/limits.conf;
}
EOF

ln -s /usr/share/nginx/html/example-com.conf /etc/nginx/conf.d
#chown -R nginx:nginx /usr/share/nginx/html 
nginx -s reload
