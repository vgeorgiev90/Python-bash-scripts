package packages

import (
	"bufio"
	"fmt"
	"os"
	"strings"
)

func Read() (value string) {
	//Define a reader for user input
	reader := bufio.NewReader(os.Stdin)
	fmt.Print("Your first message: ")
	//Read the input and separates the input with new line (return string and error)
	msg, _ := reader.ReadString('\n')

	fmt.Print("Your seconds message: ")
	msg2, _ := reader.ReadString('\n')

	//Trim spaces at begining and at the end
	msg = strings.TrimSpace(msg)
	msg2 = strings.TrimSpace(msg2)

	value = fmt.Sprintf("%s , %s", msg, msg2)
	return
}
