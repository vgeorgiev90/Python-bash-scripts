package main

import "fmt"

/*
multi line comment
*/

//single line comment

func main() {
	fmt.Println("Hello from go\n")
	fmt.Println(`multi
  line print with 
  backtick`)
	fmt.Println("\n")
	fmt.Println("Unicode string: \u2272 གྷ ᛥ")
	fmt.Println("More Unicode: Виктор на кирилица")
	// Rune characters
	fmt.Println('W')
}
