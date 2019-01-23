package main

import "fmt"

func main() {
	//if/else statement
	ages := map[string]int{}
	ages["viktor"] = 28

	if ages["viktor"] < 25 {
		fmt.Println("Viktor age is less than 25")
	} else if ages["viktor"] > 30 {
		fmt.Println("Viktor age is grater than 25 ")
	} else {
		fmt.Println("Viktor age is greater than 25 and less than 30")
	}

	//switch statement
	switch {
	case ages["viktor"] < 18:
		fmt.Println("less than 18")
	case ages["viktor"] > 18:
		fmt.Println("greater than 18")
	default:
		fmt.Println("default option")
	}

	//More advanced switch statement
	switch ages["viktor"] {
	case 15, 18, 20:
		fmt.Println("Not in first case")
	case 28, 30, 35:
		fmt.Println("in the second case")
	default:
		fmt.Println("Default option")
	}

	//For loop examples

	//sequence loop
	ages2 := map[string]int{
		"viktor": 25,
		"stefan": 21,
		"ioana":  18,
	}

	// For each element asign key to name and valie to age
	for name, age := range ages2 {
		switch {
		case age < 20:
			fmt.Println(fmt.Sprintf("%s is under 20 years old", name))
		case age > 20:
			fmt.Println(fmt.Sprintf("%s is above 20 years old", name))
		default:
			fmt.Println("Just default")
		}
	}

	// Traditional for loop
	for i := 1; i <= 10; i++ {
		fmt.Println("Counting:", i)
	}

	//Conditional loop
	a := 0
	for a < 10 {
		fmt.Println("Trad loop:", a)
		a++
	}

	//Stop iterration intentionally 
	b := 0
	for b < 20 {
	  if b%2 == 0 {
	    b++
	    continue
	  } else if b == 5 {
	    break
	  }
	  fmt.Println("Count:", b)
	  b++
	}


}
