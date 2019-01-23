package main

//import "fmt"


//Import path is relative to GOPATH/src
import (
	"fmt"
	"basics/functions/packages"
)


// Our main function
func main() {
   message := packages.Greeting("Viktor", "Hello")
   fmt.Println(message)
   message2 := packages.Fun2(23, 55)
   fmt.Println(message2)


   message3 := packages.Read()
   fmt.Println(message3)
   packages.File(message3, "./test-file")
}


// Custom function definition in format
// FUNC_NAME(var-name type, var-name type) return-value-type {}

//func greeting(name string, message string) string {
//   return  fmt.Sprintf("%s , %s", message, name)
//}

//Same function can also be declared as follows
/*

func greeting(name, message string) (salute string) {
    salute = fmt.Sprintf("%s, %s", message, name)
    return
}

*/

//Also the function can be extracted in different package localted in packages/greeting.go
