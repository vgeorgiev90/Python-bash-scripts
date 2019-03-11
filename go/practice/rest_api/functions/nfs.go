package functions

import (
	"fmt"
	"golang.org/x/crypto/ssh"
	"io/ioutil"
)

func Ssh_session(host, key_path string) *ssh.Client { //*ssh.Session {
	//var ssh_key ssh.PublicKey
	key, err := ioutil.ReadFile(key_path)
	if err != nil {
		fmt.Println("Unable to open private key file:", key_path)
	}

	signer, err := ssh.ParsePrivateKey(key)
	if err != nil {
		fmt.Println(err)
	}
	//ssh_key = signer.PublicKey()
	config := &ssh.ClientConfig{
        User: "root",
        Auth: []ssh.AuthMethod{
        ssh.PublicKeys(signer),
        },
        HostKeyCallback: ssh.InsecureIgnoreHostKey(), //ssh.FixedHostKey(ssh_key),
	}

	host = fmt.Sprintf("%s:22", host)
	client, err := ssh.Dial("tcp", host, config)
	if err != nil {
		fmt.Println("Unable to connect:", err)
	}
	/*defer client.Close()

	session, sess_err := client.NewSession()
	if sess_err != nil {
		client.Close()
		fmt.Println(sess_err)
	}

	return session */
	return client
}


func Provision(client *ssh.Client, dir string) {
	session, sess_err := client.NewSession()
        if sess_err != nil {
                client.Close()
                fmt.Println(sess_err)
        }
	cmd := fmt.Sprintf("mkdir %s; chown nobody: %s ;echo '%s    10.0.11.0/24(rw,sync,no_subtree_check,root_squash)' >> /etc/exports ; exportfs -arv", dir, dir, dir)
	_, err := session.CombinedOutput(cmd)
	if err != nil {
		fmt.Println(err)
	}
	defer session.Close()
	defer client.Close()
}

func Delete(client *ssh.Client, dir string) {
	session, sess_err := client.NewSession()
        if sess_err != nil {
                client.Close()
                fmt.Println(sess_err)
        }
	cmd := fmt.Sprintf("sed -i '/^\\%s/d' /etc/exports; exportfs -arv; rm -rf %s", dir, dir)
	_, err := session.CombinedOutput(cmd)
        if err != nil {
                fmt.Println(err)
        }
        defer session.Close()
	defer client.Close()
}
