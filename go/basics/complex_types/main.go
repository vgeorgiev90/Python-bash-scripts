package main

import "fmt"

func main() {
  //Declare array with values
  names := [3]string{"Alex", "Viktor", "Stefan"}

  //Declare array without values
  var names2 [2]int

  names2[0] = 12
  //names2[1] = 16

  fmt.Println(names)
  fmt.Println(names2)
  // Check if second element is nill (compare it with the default value "" for strings , 0 for numbers)
  fmt.Println("names2[1] os nil:", names2[1] == 0)

  //Slice with undefined number of elements
  names3 := []string{}

  names3 = append(names3, "Viktor")
  names3 = append(names3, "Rusko")
  fmt.Println(names3)

  //Maps (dictionary)   map[type-of-key]type-of-value{}
  dict := map[string]string{
    "viktor": "georgiev",
    "peter": "kossev",
  }
  fmt.Println(dict)
  fmt.Println("First key value:", dict["viktor"])
  fmt.Println("Second key value:", dict["peter"])


  //Dynamic value asigning
  dict2 := map[string]int{}
  dict2["viktor"] = 28
  dict2["stefan"] = 27
  fmt.Println(dict2)

  //Delete key from the dict
  delete(dict2, "stefan")
  fmt.Println(dict2)
}
