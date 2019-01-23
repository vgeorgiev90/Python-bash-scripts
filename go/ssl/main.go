package main

import (
	"flag"
	"fmt"
	"os"
	"ssl/functions"
)

func main() {
	functions.Cfssl()

	/*
	   // First value: common_name , Second value: alt_names , 1st value will be used as file name
	   // All files will be created in /root/certificates -- functions.Template("common_name", "alt_names")
	   //tempalte for certificate
	   functions.Template("viktor", "viktor")
	   //template for CA
	   functions.Template("kubernetes", "kubernetes")

	   //CA generation with provided common_name for file name -- functions.Ca("common-name-for-ca")
	   functions.Ca("kubernetes")

	   //Generate certificate -- functions.Certs("FILE-NAME", "/path/to/ca", "/path/to/ca-key", "hostnames")
	   functions.Certs("viktor", "/root/certificates/ca.pem", "/root/certificates/ca-key.pem", "master,127.0.0.1")

	*/

	//Define some flags
	var common_name string
	var alt_names string
	var ca string
	var ca_key string
	var ca_type string
	var hostnames string
	var cmd string

	//Parse the flags defined
	flag.StringVar(&common_name, "cname", "", "Common name for the certificate ,mandatory argument")
	flag.StringVar(&alt_names, "anames", "", "Alternate names for the certificate , mandatory argument")
	flag.StringVar(&ca, "ca", "", "Certificate authority to be used if ca-type set to remote")
	flag.StringVar(&ca_key, "ca-key", "", "CA key to be used if ca-type set to remote")
	flag.StringVar(&ca_type, "ca-type", "", "If set to local you need to first generate CA , if set to remote provide ca and ca-key")
	flag.StringVar(&hostnames, "hostnames", "", "Hostnames for the certificate that will be issued delimited with ,")
	flag.StringVar(&cmd, "cmd", "", "Either ca for CA generation, cert for certificate generation")
	flag.Parse()

	switch cmd {
	case "ca":
		if common_name == "" || alt_names == "" {
			fmt.Println("To generate ca you have to provide cname and anames flags")
			os.Exit(0)
		} else {
			functions.Template(common_name, alt_names)
			functions.Ca(common_name)
		}

	case "cert":
		if ca_type == "" {
			fmt.Println("Please provide ca-type flag: either local  or remote")
			os.Exit(0)
		} else if ca_type == "local" {
			if common_name == "" || alt_names == "" {
				fmt.Println("You forgot to provide cname, anames and hostnames")
				os.Exit(0)
			} else {
				functions.Template(common_name, alt_names)
				functions.Certs(common_name, "/root/certificates/ca.pem", "/root/certificates/ca-key.pem", hostnames)
			}
		} else if ca_type == "remote" {
			if common_name == "" || alt_names == "" || ca_key == "" || ca == "" {
				fmt.Println("Please provide all needed vars cname , anames, hostnames, ca, ca-key")
				os.Exit(0)
			} else {
				functions.Template(common_name, alt_names)
				functions.Certs(common_name, ca, ca_key, hostnames)
			}
		}

	default:
		flag.Usage()
	}

}
