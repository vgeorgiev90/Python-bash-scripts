package functions

import (
	"fmt"
	"os"
	"os/exec"
)

func Cfssl() {
	_, lookErr := exec.LookPath("cfssl")

	if lookErr != nil {
		//Get cfss binaries
		fmt.Println("cfssl and cfssljson not found in PATH downloading...")
		cmd1 := "wget https://pkg.cfssl.org/R1.2/cfssl_linux-amd64 -P /root"
		cmd2 := "wget https://pkg.cfssl.org/R1.2/cfssljson_linux-amd64 -P /root"
		cmd3 := "mv /root/cfssl_linux-amd64 /usr/local/bin/cfssl"
		cmd4 := "mv /root/cfssljson_linux-amd64 /usr/local/bin/cfssljson"
		cmd5 := "chmod +x /usr/local/bin/cfssl"
		cmd6 := "chmod +x /usr/local/bin/cfssljson"
		commands := []string{cmd1, cmd2, cmd3, cmd4, cmd5, cmd6}

		for _, cmd := range commands {
			_, err := exec.Command("bash", "-c", cmd).Output()
			if err != nil {
				fmt.Println("There was an error with command:", err)
				os.Exit(1)
			}
		}
	}
}
