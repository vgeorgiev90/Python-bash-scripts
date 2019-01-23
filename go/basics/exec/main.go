package main

import (
        "fmt"
        "os/exec"
        //"syscall"
        //"os"
)

func main() {
        cmd := "ls /etc | grep hosts"
        out, err := exec.Command("bash", "-c", cmd).Output()
        if err != nil {
           fmt.Println("There was an error:", err)
        }
        fmt.Println(string(out))


/*      out, err := exec.Command("date").Output()
        if err != nil {
           fmt.Println(err)
        }
        fmt.Println(string(out))
*/
}

