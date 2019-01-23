package main

import "fmt"

func main() {
   // Explicit Variable declarations
   // var NAME TYPE
   var myInt int = 16
   // Multi var definition
   var var1, var2, var3 = "viktor", 12, true

   fmt.Println("myInt times two:", myInt*2)
   fmt.Println("var1:", var1)
   fmt.Println("var2:", var2)
   fmt.Println("var3:", var3)

   //Blank identifier 
   var value, _ = "ok", "not used"
   fmt.Println(value)
   //Shorthand variable syntax without declaring type
   myInt2 := 16
   fmt.Println(myInt2)
   // equivelent of:
   // myInt2 int = 16

   //Declare variable withour value
   var name string

   // Some code

   name = "Viktor"
   fmt.Println(name)
}
