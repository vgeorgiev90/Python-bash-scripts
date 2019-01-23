package main

import (
	"fmt"
	"flag"
	"os"
)

func main() {



//Define flags
var name string
var message string

//Parse flags  -- exptected values  string-pointer, name for the flag, default value, help message
flag.StringVar(&name, "name", "", "name to use")
flag.StringVar(&message, "message", "", "message to print")

flag.Parse()
//Show usage if flags are invalid

if name == "" && message == "" {
   flag.Usage()
   os.Exit(0)
}

// Print flags and exit based on DEBUG environment variable

if os.Getenv("DEBUG") != "" {
	fmt.Println("name:", name)
	fmt.Println("message:", message)
        os.Exit(0)
}


fmt.Println(name)
fmt.Println(message)


}
