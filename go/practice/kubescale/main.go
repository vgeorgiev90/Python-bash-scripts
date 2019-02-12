package main

import (
	"kubescale/functions"
	"flag"
	"strings"
)

func main() {
	var gluster string
	var key string
	var join string
	var help bool

	flag.StringVar(&gluster, "glusterfs", "no", "Install or not glusterfs")
	flag.StringVar(&key, "key", "", "Public key to be added for the root user")
	flag.StringVar(&join, "join", "", "Whether or not to join the node to the cluster")
	flag.BoolVar(&help, "help", false, "Usage help")
	flag.Parse()

	if help == true {
		flag.Usage()
		functions.Help()
	}


	if gluster == "yes" {
	if key == "" {
		key := functions.GetKey()
		functions.Prereqs(key)
		functions.Gluster()
	} else {
		functions.Prereqs(key)
		functions.Gluster()
	}
	} else {
        if key == "" {
                key := functions.GetKey()
                functions.Prereqs(key)
        } else {
                functions.Prereqs(key)
        }
	}

	if join == "yes" {
		addr, token, hash := functions.JoinInfo()
		functions.Join(addr, token, hash)
	} else if join != "" {
		info := strings.Split(join, ",")
		functions.Join(info[0], info[1], info[2])
	}
}
