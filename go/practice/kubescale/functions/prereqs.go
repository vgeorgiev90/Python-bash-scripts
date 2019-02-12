package functions

import (
	"fmt"
	"os/exec"
	"io/ioutil"
	"os"
	"bufio"
	"strings"
	//"regexp"
)


func Prereqs(key string) {

	k8s_sysctl := `
#control whether or not packets traversing the bridge are sent to iptables for processing
net.bridge.bridge-nf-call-ip6tables = 1
net.bridge.bridge-nf-call-iptables = 1
net.ipv4.conf.all.forwarding = 1
#For keepalived and haproxy
net.ipv4.ip_nonlocal_bind = 1
`

	//Write files
	if _, err := os.Stat("/root/.ssh"); os.IsNotExist(err) {
           os.Mkdir("/root/.ssh", 0700)
        }

	ioutil.WriteFile("/root/.ssh/authorized_keys", []byte(key), 0600)
	ioutil.WriteFile("/etc/sysctl.d/k8s.conf", []byte(k8s_sysctl), 0644)

	//Disable swap
	cmd1 := "swapoff -a && cp /etc/fstab /etc/fstab-backup"
	cmd2 := "sed -ie '/\bswap\b/d' /etc/fstab"
	//Add ubuntu docker repo and k8s repo keys
	cmd3 := "curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add - && curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add -"
	//Add the repositories
	cmd4 := `add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"`
	cmd5 := "echo 'deb http://apt.kubernetes.io/ kubernetes-xenial main' > /etc/apt/sources.list.d/kubernetes.list"
	//Update and install all packages
	cmd6 := "apt-get update; apt-get install docker-ce ntp kubeadm kubelet kubectl -y && systemctl enable ntp && systemctl enable docker && systemctl start ntp && systemctl start docker"

	commands := []string{cmd1, cmd2, cmd3, cmd4, cmd5, cmd6}

	for _, c := range commands {
		_, err := exec.Command("bash", "-c", c).Output()
		if err != nil {
			fmt.Println("There was error with command:", c)
			fmt.Println(err)
		}

	}

}


func Gluster() {
	cmd1 := "add-apt-repository ppa:gluster/glusterfs-4.1 -y"
	cmd2 := "apt-get update; apt-get install glusterfs-server glusterfs-client thin-provisioning-tools -y"
	cmd3 := "systemctl enable glusterd ; systemctl start glusterd"
	commands := []string{cmd1, cmd2, cmd3}

	for _, c := range commands {
                _, err := exec.Command("bash", "-c", c).Output()
                if err != nil {
                        fmt.Println("There was error with command:", c)
                        fmt.Println(err)
		}
}
}

func GetKey() (key string) {
        reader := bufio.NewReader(os.Stdin)
        fmt.Print("Public Key: ")
        //Read the input and separates the input with new line (return string and error)
        key, _ = reader.ReadString('\n')

	key = strings.TrimSpace(key)
	return key
}

func Join(apiaddress, token, hash string) {
	cmd := fmt.Sprintf("kubeadm join %s --token %s --discovery-token-ca-cert-hash %s --ignore-preflight-errors=all", apiaddress, token, hash)
	_, err := exec.Command("bash", "-c", cmd).Output()
	if err != nil {
		fmt.Println("There was a problem with cluster join")
		fmt.Println(err)
	}
}

func JoinInfo() (address, token, hash string) {
        reader := bufio.NewReader(os.Stdin)
        fmt.Print("K8s Api Address: ")
        //Read the input and separates the input with new line (return string and error)
        address, _ = reader.ReadString('\n')

	fmt.Print("K8s Join Token: ")
	token, _ = reader.ReadString('\n')

        fmt.Print("K8s Join Token hash: ")
        hash, _ = reader.ReadString('\n')


        address = strings.TrimSpace(address)
	token = strings.TrimSpace(token)
	hash = strings.TrimSpace(hash)
        return address, token, hash
}

func Help() {
	fmt.Println("")
	fmt.Println(`
	Flags usage:
	kubescale -gluster=yes/no                      ---  Install or not glusterfs
	kubescale -key="Some-long-public-key-string"   ---  Public key to be added for the root user , if empty or ommited the user will be prompted
	kubescale -join=yes/api-address,token,hash     ---  Whether to join or not node to the cluster, if empty or ommited node will not be joined, if yes is specified user will be prompted for information , else all info can be passed separated by ,  (api-address,token,hash)

	Example:
	kubescale -glusterfs=no -key="Some key" -join=10.0.11.120:6443,ogrwig.902t7lb28m72by88,sha256:ee6c7d6fc83e8c13faff5808fb2dcf9637891d14cabdc1598f52e91574b8fd97                                             ---  Install all prereqs , add key to root user , join the cluster

	kubescale -glusterf=yes -key="Some key"        ---  Install all prereqs, add key to root user

	kubescale -glustefs=no -join=yes               ---  Install all prereqs , prompt for key and join information

	`)
	os.Exit(0)
}
