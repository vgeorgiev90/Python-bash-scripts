package functions

import (
	"fmt"
	"os"
	"os/exec"
	"strings"
)

func Ca(name string) {
	path := []string{"/root/certificates", name}
	file := strings.Join(path, "/")

	os.Chdir("/root/certificates")
	cmd := "cfssl gencert -initca CA | cfssljson -bare ca"
	cmd = strings.Replace(cmd, "CA", file, 1)
	cmd2 := "rm -rf /root/certificates/ca.csr && rm -rf CA"
	cmd2 = strings.Replace(cmd2, "CA", file, 1)

	_, err := exec.Command("bash", "-c", cmd).Output()
	if err != nil {
		fmt.Println(err)
		os.Exit(1)
	}

	_, err_rm := exec.Command("bash", "-c", cmd2).Output()
	if err != nil {
		fmt.Println(err_rm)
		os.Exit(1)
	}
	fmt.Println("Certificate authority files generated in /root/certificates/ca.pem , ca-key.pem")

}
