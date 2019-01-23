package packages

import (
	"fmt"
	"io/ioutil"
)

func File(content, path string) {
   _ = ioutil.WriteFile(path, []byte(content), 0644)
   fmt.Println("File created: ", path)

   //Open the file
   /*
   f, err = os.OpenFile("file", os.O_WRONLY, 0644)

   if err != nill {
      fmt.Println("Unable to open file")
      os.Exit(1)
   }

   //Run the expression after all other actions are complete
   defer f.Close()

   // Some more actions

   _, err = f.Write([]byte("My Message"))

   if err != nill {
      fmt.Println("Can not write to file")
   }
   
   */
}
