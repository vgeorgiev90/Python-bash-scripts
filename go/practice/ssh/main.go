package main

import (
	"ssh/functions"
	"flag"
)

func main() {

	var host string
	var hash string
	var cmd string
	var from_file string
	var auth_type string

	flag.StringVar(&host, "host", "", "Host for ssh connection in format IP:PORT")
	flag.StringVar(&hash, "pass", "", "Base64 encoded password 'echo -n some-pass | base64', Default user that is used is root")
	flag.StringVar(&from_file, "file", "", "Path to config file")
	//flag.StringVar(&auth_type, "auth", "password", "Authentication type either password or key")
	flag.StringVar(&cmd, "cmd", "ls", "CMD to execute")
	flag.Parse()


	if from_file != "" {
		config := functions.FromFile(from_file)
		auth := functions.DecryptCmdPass(config.Pass)
		for _, c := range config.Cmd {
			functions.Ssh(c, config.Host, auth)
		}
	} else {

	if host != "" {
		if hash == "" {
			auth := functions.GetPass()
			functions.Ssh(cmd, host, auth)
		} else {
			auth := functions.DecryptCmdPass(hash)
			functions.Ssh(cmd, host, auth)
		}
	} else {
		flag.Usage()
		functions.GenConfig()
	}

	}
}
