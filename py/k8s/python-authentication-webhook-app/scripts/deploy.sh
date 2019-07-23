#!/bin/bash



choice=${1}


case $choice in
'gen-env')
read -p "MySQL Host: " DB_HOST
read -p "MySQL Port: " DB_PORT
read -p "MySQL User: " DB_USER
read -p "MySQL Pass: " DB_PASS
read -p "MySQL DB Name: " DB_NAME
read -p "Kube Api Address with Port (localhost:6443): " K8S_API
cat << EOF > ../.env
MYSQL_HOST=${DB_HOST}
MYSQL_PORT=${DB_PORT}
MYSQL_USER=${DB_USER}
MYSQL_PASS=${DB_PASS}
MYSQL_DB=${DB_NAME}
K8S_API_ADDRESS=${K8S_API}
#K8S_CA_CRT_PATH="/etc/kubernetes/pki/ca.crt"
K8S_CA_CRT__PATH="/app/ssl/ca.crt"
K8S_ADMIN_TOKEN="DB3Mc4fpzwYMggyINo4q"
EOF
;;

'run')
read -p "Master node IP and Hostname separated with ,: " HOSTS
read -p "Path to cluster certificate authority cert: " CA_CERT
read -p "Path to cluster certificate authority key: " CA_KEY

read -n 1 -s -r -p "Press any key to continue"
clear
HOSTS=${HOSTS},127.0.0.1,localhost


echo "Building image"
docker build -t authserver:v1 ..
echo "Init database"
docker run --rm authserver:v1 /app/app/auth-server.py db-init

echo "Generating certificate for auth server"
./ssl -cmd cert --cname auth-server -anames ${HOSTS} -hostnames ${HOSTS} -ca-type remote -ca CA_CERT -ca-key CA_KEY

echo "Creating tls secret"
kubectl -n kube-system create secret tls auth-server-tls --cert=/root/certificates/auth-server.pem --key=/root/certificates/auth-server-key.pem

echo "Labeling master node"
kubectl label node $(kubectl get nodes | grep master | awk '{print $1}') app=auth-server

echo "Creating deployment"
kubectl apply -f ../deployments/auth-server.yaml
;;

*)
  echo "Either run or gen-env"
;;
esac
