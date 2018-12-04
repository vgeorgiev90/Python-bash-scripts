#!/bin/bash


choice="${1}"

############################## Functions ###########################

master-install () {
  read -p "Kube version in format 1.*.*: " ver

  #### Get cfssl
  wget -q --show-progress --https-only --timestamping \
  https://pkg.cfssl.org/R1.2/cfssl_linux-amd64 \
  https://pkg.cfssl.org/R1.2/cfssljson_linux-amd64
  chmod +x cfssl_linux-amd64 cfssljson_linux-amd64
  mv -v cfssl_linux-amd64 /usr/local/bin/cfssl
  mv -v cfssljson_linux-amd64 /usr/local/bin/cfssljson

  #### Get k8s packages
  wget \
  https://storage.googleapis.com/kubernetes-release/release/v${ver}/bin/linux/amd64/kubectl \
  https://github.com/coreos/etcd/releases/download/v3.3.10/etcd-v3.3.10-linux-amd64.tar.gz \
  https://storage.googleapis.com/kubernetes-release/release/v${ver}/bin/linux/amd64/kube-apiserver \
  https://storage.googleapis.com/kubernetes-release/release/v${ver}/bin/linux/amd64/kube-controller-manager \
  https://storage.googleapis.com/kubernetes-release/release/v${ver}/bin/linux/amd64/kube-scheduler

  chmod +x kube-apiserver kube-controller-manager kube-scheduler kubectl
  mv -v kube-apiserver kube-controller-manager kube-scheduler kubectl /usr/local/bin
  tar -xvzf etcd-v3.3.10-linux-amd64.tar.gz && mv -v etcd-v3.3.10-linux-amd64/etcd* /usr/local/bin
  chmod +x /usr/local/bin/etcd*
}

worker-install () {
  read -p "Kube version in format 1.*.*: " ver

  #### Create working directories
  mkdir -vp \
  /etc/cni/net.d \
  /opt/cni/bin \
  /var/lib/kubelet \
  /var/lib/kube-proxy \
  /var/lib/kubernetes \
  /var/run/kubernetes \
  /etc/etcd \
  /var/lib/etcd \
  /root/files \
  /etc/kubernetes/config

  #### Docker install
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add -
  add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
  apt-get update; apt-get install docker-ce && systemctl enable docker && systemctl start docker

  #### Kubelet Kube-proxy and CNI plugins
  wget https://storage.googleapis.com/kubernetes-release/release/v${ver}/bin/linux/amd64/kube-proxy
  wget https://storage.googleapis.com/kubernetes-release/release/v${ver}/bin/linux/amd64/kubelet
  wget https://github.com/containernetworking/plugins/releases/download/v0.6.0/cni-plugins-amd64-v0.6.0.tgz

  chmod +x kubelet kube-proxy
  mv kubelet kube-proxy /usr/local/bin
  tar -xzf cni-plugins-amd64-v0.6.0.tgz -C /opt/cni/bin
}


certs-create () {

#### Create all needed PKI certificates
cd files
##### Certificate Authority
cat > ca-config.json << EOF
{
  "signing": {
    "default": {
      "expiry": "8760h"
    },
    "profiles": {
      "kubernetes": {
        "usages": ["signing", "key encipherment", "server auth", "client auth"],
        "expiry": "8760h"
      }
    }
  }
}
EOF

cat > template.json << EOF
{
  "CN": "CommonName",
  "key": {
    "algo": "rsa",
    "size": 2048
  },
  "names": [
    {
      "C": "BG",
      "L": "Sofia",
      "O": "OtherNames",
      "OU": "CA",
      "ST": "Sofia"
    }
  ]
}
EOF

cp template.json ca-csr.json
sed -i 's/CommonName/kubernetes/' ca-csr.json
sed -i 's/OtherNames/kubernetes/' ca-csr.json
cfssl gencert -initca ca-csr.json | cfssljson -bare ca

##### Admin certificates

cp template.json admin-csr.json
sed -i 's/CommonName/admin/' admin-csr.json
sed -i 's/OtherNames/system:masters/' admin-csr.json
cfssl gencert \
  -ca=ca.pem \
  -ca-key=ca-key.pem \
  -config=ca-config.json \
  -profile=kubernetes \
  admin-csr.json | cfssljson -bare admin


##### Kubelet certificates

declare -A workers
workers[$w1]=$ip1
workers[$w2]=$ip2
workers[$w3]=$ip3
workers[$w4]=$ip4

for i in "${!workers[@]}"; do
  cp template.json ${i}-csr.json
  sed -i "s/CommonName/system:node:${i}/" ${i}-csr.json
  sed -i 's/OtherNames/system:nodes/' ${i}-csr.json

  cfssl gencert \
  -ca=ca.pem \
  -ca-key=ca-key.pem \
  -config=ca-config.json \
  -hostname=${workers[$i]},${i} \
  -profile=kubernetes \
  ${i}-csr.json | cfssljson -bare ${i}
done

##### Controller manager

cp template.json kube-controller-manager-csr.json
sed -i 's/CommonName/system:kube-controller-manager/' kube-controller-manager-csr.json
sed -i 's/OtherNames/system:kube-controller-manager/' kube-controller-manager-csr.json
cfssl gencert \
  -ca=ca.pem \
  -ca-key=ca-key.pem \
  -config=ca-config.json \
  -profile=kubernetes \
  kube-controller-manager-csr.json | cfssljson -bare kube-controller-manager

#### Kube-proxy
cp template.json kube-proxy-csr.json
sed -i 's/CommonName/system:kube-proxy/' kube-proxy-csr.json
sed -i 's/OtherNames/system:node-proxier/' kube-proxy-csr.json

cfssl gencert \
  -ca=ca.pem \
  -ca-key=ca-key.pem \
  -config=ca-config.json \
  -profile=kubernetes \
  kube-proxy-csr.json | cfssljson -bare kube-proxy

### Kube scheduler
cp template.json kube-scheduler-csr.json
sed -i 's/CommonName/system:kube-scheduler/' kube-scheduler-csr.json
sed -i 's/OtherNames/system:kube-scheduler/' kube-scheduler-csr.json

cfssl gencert \
  -ca=ca.pem \
  -ca-key=ca-key.pem \
  -config=ca-config.json \
  -profile=kubernetes \
  kube-scheduler-csr.json | cfssljson -bare kube-scheduler

#### Kube api server

cp template.json kubernetes-csr.json
sed -i 's/CommonName/kubernetes/' kubernetes-csr.json
sed -i 's/OtherNames/Kubernetes/' kubernetes-csr.json

cfssl gencert \
  -ca=ca.pem \
  -ca-key=ca-key.pem \
  -config=ca-config.json \
  -hostname=${api_names} \
  -profile=kubernetes \
  kubernetes-csr.json | cfssljson -bare kubernetes

##### Service account

cp template.json service-account-csr.json
sed -i 's/CommonName/service-accounts/' service-account-csr.json
sed -i 's/OtherNames/Kubernetes/' service-account-csr.json
cfssl gencert \
  -ca=ca.pem \
  -ca-key=ca-key.pem \
  -config=ca-config.json \
  -profile=kubernetes \
  service-account-csr.json | cfssljson -bare service-account

##### ETCD api

cp template.json etcd-api-csr.json
sed -i 's/CommonName/kube-etcd/' etcd-api-csr.json
sed -i 's/OtherNames/kube-etcd/' etcd-api-csr.json


cfssl gencert \
  -ca=ca.pem \
  -ca-key=ca-key.pem \
  -config=ca-config.json \
  -hostname=${etcd_api} \
  -profile=kubernetes \
  etcd-api-csr.json | cfssljson -bare etcd-api

###### ETCD peers

cp template.json etcd-peer-csr.json
sed -i 's/CommonName/kube-etcd/' etcd-peer-csr.json
sed -i 's/OtherNames/kube-etcd/' etcd-peer-csr.json

cfssl gencert \
  -ca=ca.pem \
  -ca-key=ca-key.pem \
  -config=ca-config.json \
  -hostname=${etcd_peer} \
  -profile=kubernetes \
  etcd-peer-csr.json | cfssljson -bare etcd-peer

ENCRYPTION_KEY=$(head -c 32 /dev/urandom | base64)

cat > encryption-config.yaml << EOF
kind: EncryptionConfig
apiVersion: v1
resources:
  - resources:
      - secrets
    providers:
      - aescbc:
          keys:
            - name: key1
              secret: ${ENCRYPTION_KEY}
      - identity: {}
EOF

####### Create kubeconfigs

echo -p "kube api address: " KUBERNETES_ADDRESS

for instance in $w1 $w2 $w3 $w4; do
kubectl config set-cluster kubernetes-the-hard-way \
    --certificate-authority=ca.pem \
    --embed-certs=true \
    --server=https://${KUBERNETES_ADDRESS}:6443 \
    --kubeconfig=${instance}.kubeconfig

kubectl config set-credentials system:node:${instance} \
    --client-certificate=${instance}.pem \
    --client-key=${instance}-key.pem \
    --embed-certs=true \
    --kubeconfig=${instance}.kubeconfig

kubectl config set-context default \
    --cluster=kubernetes-the-hard-way \
    --user=system:node:${instance} \
    --kubeconfig=${instance}.kubeconfig

kubectl config use-context default --kubeconfig=${instance}.kubeconfig
done

#### Kube proxy

kubectl config set-cluster kubernetes-the-hard-way \
    --certificate-authority=ca.pem \
    --embed-certs=true \
    --server=https://${KUBERNETES_ADDRESS}:6443 \
    --kubeconfig=kube-proxy.kubeconfig

 kubectl config set-credentials system:kube-proxy \
    --client-certificate=kube-proxy.pem \
    --client-key=kube-proxy-key.pem \
    --embed-certs=true \
    --kubeconfig=kube-proxy.kubeconfig

kubectl config set-context default \
    --cluster=kubernetes-the-hard-way \
    --user=system:kube-proxy \
    --kubeconfig=kube-proxy.kubeconfig

kubectl config use-context default --kubeconfig=kube-proxy.kubeconfig

#### Kube controller-manager

kubectl config set-cluster kubernetes-the-hard-way \
    --certificate-authority=ca.pem \
    --embed-certs=true \
    --server=https://127.0.0.1:6443 \
    --kubeconfig=kube-controller-manager.kubeconfig

kubectl config set-credentials system:kube-controller-manager \
    --client-certificate=kube-controller-manager.pem \
    --client-key=kube-controller-manager-key.pem \
    --embed-certs=true \
    --kubeconfig=kube-controller-manager.kubeconfig

kubectl config set-context default \
    --cluster=kubernetes-the-hard-way \
    --user=system:kube-controller-manager \
    --kubeconfig=kube-controller-manager.kubeconfig

kubectl config use-context default --kubeconfig=kube-controller-manager.kubeconfig

#### Kube scheduler

kubectl config set-cluster kubernetes-the-hard-way \
    --certificate-authority=ca.pem \
    --embed-certs=true \
    --server=https://127.0.0.1:6443 \
    --kubeconfig=kube-scheduler.kubeconfig

kubectl config set-credentials system:kube-scheduler \
    --client-certificate=kube-scheduler.pem \
    --client-key=kube-scheduler-key.pem \
    --embed-certs=true \
    --kubeconfig=kube-scheduler.kubeconfig

kubectl config set-context default \
    --cluster=kubernetes-the-hard-way \
    --user=system:kube-scheduler \
    --kubeconfig=kube-scheduler.kubeconfig

kubectl config use-context default --kubeconfig=kube-scheduler.kubeconfig

##### Admin kubeconfig

kubectl config set-cluster kubernetes-the-hard-way \
    --certificate-authority=ca.pem \
    --embed-certs=true \
    --server=https://127.0.0.1:6443 \
    --kubeconfig=admin.kubeconfig

kubectl config set-credentials admin \
    --client-certificate=admin.pem \
    --client-key=admin-key.pem \
    --embed-certs=true \
    --kubeconfig=admin.kubeconfig

kubectl config set-context default \
    --cluster=kubernetes-the-hard-way \
    --user=admin \
    --kubeconfig=admin.kubeconfig

kubectl config use-context default --kubeconfig=admin.kubeconfig
}

print-usage () {
  clear
  echo "This script downloads and installs kubernetes binaries for systemd setup and generates the PKI certificates that will be needed"
  echo "According to kelseyhightower/kubernetes-the-hard-way guide with few little modifications. To be included - full component install"
  echo ""
  echo "Options: master-bin, worker-bin or gen-pki"
  echo ""
  echo "============== ENV VARS NEEDED, without them the certificates will not be valid ================================================================ "
  echo ""
  echo "export w1,ip1...w*,ip*  --  hostname and ip address of worker (w1=worker1,ip1=10.0.0.1, w2=worker2,ip2=10.0.0.2) , currently 4 workers hardcoded"
  echo ""
  echo "If more workers are needed add simillar entry after line: 129"
  echo "workers[\$wN]=\$ipN  , where N is the number of the worker example for worker5: workers[\$w5]=\$ip5, also w5 and ip5 ENV vars will be needed"
  echo ""
  echo "export etcd_peer        --  hostnames and ips of the etcd peers which will be used in the certificate for peer comunication"
  echo ""
  echo "export etcd_api         --  hostnames and ips of the etcd clients (kube-api servers)"
  echo ""
  echo "export api_names        --  hostnames and ips for the kuberentes api certificite (controller_node1_host,ip, 10.32.0.1,localhost... etc)"
  echo "================================================================================================================================================"
}

################################### Script start #############################

case ${choice} in
'master-bin')
  master-install
;;
'worker-bin')
  worker-install
;;
'gen-pki')
  certs-create
;;
*)
  print-usage
;;
esac
