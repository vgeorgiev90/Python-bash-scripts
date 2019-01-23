package main

import (
	"fmt"
	"math"
)

func main() {
	//Basic math operations in go
	//Integers
	fmt.Println("Addition: 1+3=", 1+3)
	fmt.Println("Subtraction: 23-5=", 23-5)
	fmt.Println("Multiplication: 23x5=", 23*5)
	fmt.Println("Division: 20/4=", 20/4)

	//Floats
	fmt.Println("Float division: 25/3=", 25.0/3)

	//More comples math functions
	fmt.Println("Exponents: ", math.Pow(30.0, 3))
}
