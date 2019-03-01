package functions

import (
	"fmt"
	"golang.org/x/crypto/ssh"
	"os"
	"bufio"
	"strings"
	"os/exec"
	"encoding/json"
)


func Ssh(cmd, host, auth string) {

	sshConfig := &ssh.ClientConfig{
		User: "root",
		Auth: []ssh.AuthMethod{ssh.Password(auth)},
	}
	sshConfig.HostKeyCallback = ssh.InsecureIgnoreHostKey()

	client, client_err := ssh.Dial("tcp", host, sshConfig)
	if client_err != nil {
		fmt.Println(client_err)
	}

	session, sess_err := client.NewSession()
	if sess_err != nil {
		client.Close()
		fmt.Println(sess_err)
	}

	out , cmd_err := session.CombinedOutput(cmd)
	if cmd_err != nil {
		fmt.Println(cmd_err)
	}
	fmt.Println(string(out))
	client.Close()
}

func GetPass() (password string) {
	var pass string
	reader := bufio.NewReader(os.Stdin)
	fmt.Print("Password: ")
	pass, _ = reader.ReadString('\n')
	pass = strings.TrimSpace(pass)
	return pass
}

func DecryptCmdPass (base64_hash string) (pass string) {
	cmd := fmt.Sprintf("echo '%s' | base64 -d", base64_hash)

	out, err := exec.Command("bash", "-c", cmd).Output()
	if err != nil {
		fmt.Println(err)
		os.Exit(1)
	}
	return string(out)
}


type Conf struct {
	Host string
	Pass string
	Cmd []string
}


func FromFile(path string) Conf {
	var conf Conf
	file , err := os.Open(path)
	if err != nil {
		fmt.Println(err)
		os.Exit(1)
	}

	jsonParse := json.NewDecoder(file)
    	jsonParse.Decode(&conf)
    	return conf
}

func GenConfig() {
	content := `
{
  "host": "SSH-IP:SSH-PORT",
  "pass": "base64-encoded-password",
  "cmd": [ 
      "cmd1", 
      "cmd2", 
      "cmd3", 
      "cmd4" 
  ]
}
`
	fmt.Println("")
	fmt.Println("If you want to use config instead of flags use the following content:")
	fmt.Println("---------------------------------------------------------------------")
	fmt.Println(content)
}
