package functions

import (
	"fmt"
	"strings"
	"os/exec"
	"os"
)

func Certs(file, ca, ca_key, hostnames string) {
	
	name := []string{"/root/certificates", file}
	path := strings.Join(name, "/")
	//Generate certificates with the ca and hostnames provided
	cmd := "cfssl gencert -ca=CA -ca-key=CA-KEY -config=/root/certificates/config.json -profile=kubernetes -hostname=HOSTS NAME | cfssljson -bare FILE"
	cmd = strings.Replace(cmd, "CA", ca, 1)
	cmd = strings.Replace(cmd, "CA-KEY", ca_key, 1)
	cmd = strings.Replace(cmd, "HOSTS", hostnames, 1)
	cmd = strings.Replace(cmd, "NAME", path, 1)
	cmd = strings.Replace(cmd, "FILE", file, 1)

	os.Chdir("/root/certificates")


	_, err := exec.Command("bash", "-c", cmd).Output()
        if err != nil {
           fmt.Println("There was an error:", err)
        }
	fmt.Println("Certificate and key generated:", path)
	
	//Some cleanup
	cmd2 := "rm -rf /root/certificates/CSR.csr && rm -rf /root/certificates/FILE"
	cmd2 = strings.Replace(cmd2, "CSR", file, 1)
	cmd2 = strings.Replace(cmd2, "FILE", file, 1)
	_, err_rm := exec.Command("bash", "-c", cmd2).Output()
	if err_rm != nil {
	   fmt.Println("Could not remove old csr and json files")
	}
}
