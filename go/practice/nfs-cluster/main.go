package main

import (
	"nfs-cluster/functions"
	"flag"
	//"os"
	//"strings"
	"fmt"
)


func main() {


	//Define some flags
	var cmd string             //Sub command 
	var config_file string     //Load all needed values from json file

	flag.StringVar(&cmd, "cmd", "", "Sub command to be executed")
	flag.StringVar(&config_file, "config", "", "Json formated config file to be used instead of passing flags")
	flag.Parse()

	switch cmd {
		case "install":
			functions.Install()
		case "drbd/config":
				if config_file != ""{
					config := functions.LoadConfig(config_file)
					functions.ConfigureDrbd(config.Directory ,config.Resource_name, config.Device, config.Disk, config.Hostnames, config.Ips)
				} else {
					fmt.Println("Provide config file")
				}
		case "drbd/init":
                                if config_file != "" {
                                        config := functions.LoadConfig(config_file)
                                        functions.InitDrbd(config.Resource_name, config.Device, config.Fs_type)
                                } else {
					fmt.Println("Provide config file")
				}

		case "pm/setup":
				if config_file != "" {
					config := functions.LoadConfig(config_file)
					functions.PacemakerSetup(config.Ips)
				} else {
					fmt.Println("Provide config file")
				}

		case "pm/additional":
				functions.PacemakerAdditional()

		case "gen-config":
				functions.GenConfig()

		default:
			flag.Usage()
			fmt.Println("Usage soon")
	}
}
