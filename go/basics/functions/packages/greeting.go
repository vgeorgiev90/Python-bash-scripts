package packages

import "fmt"

//Everything that needs to be exported must be defined with capital letter
func Greeting(name, message string) (salute string) {
	salute = fmt.Sprintf("%s %s", message, name)
	return
}
