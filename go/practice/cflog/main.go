package main

import (
	"cflog/functions"
	"flag"
)


func main() {
	var date string
	var hour int

	flag.StringVar(&date, "d", "", "Date for the log in format: 2019-01-24")
	flag.IntVar(&hour, "h", 0, "Starting hour for the log, Only the hour: example: 12, 20, 23, 00, 1, 2 ,3.. etc  , If hour is not specified 00:00 is assumed")
	flag.Parse()


	if date != "" {
		functions.Logs(date, hour)
	} else {
		flag.Usage()
	}
}

