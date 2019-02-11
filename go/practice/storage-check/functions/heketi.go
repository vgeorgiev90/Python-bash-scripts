package functions

import (
	"fmt"
	"net/http"
	"io/ioutil"
	"regexp"
	"strings"
	"strconv"
)

func Heketi(address string) (data string) {
	url := fmt.Sprintf("http://%s/metrics", address)
	client := &http.Client{}
	request, _ := http.NewRequest("GET", url, nil)

	response, err := client.Do(request)
        if err != nil {
                fmt.Println(err)
        }

	defer response.Body.Close()

	text, _ := ioutil.ReadAll(response.Body)

	//fmt.Println(string(text))
	//path := "/root/heketi.metrics"
	//_ = ioutil.WriteFile(path, []byte(text), 0644)
	return string(text)
}

func Parse(data string) {
	r, _ := regexp.Compile("cluster=\"[a-zA-Z0-9]*\"")
	r3, _ := regexp.Compile("hostname=\".*\"")
	r2, _ := regexp.Compile("^heketi_device_size.*")
	r4, _ := regexp.Compile("^heketi_device_free.*")

	//Total size
	for _, row := range strings.Split(data, "\n") {
		match := r2.FindString(row)
		if match != "" {
			spl := strings.Split(match, " ")
			val, _ := strconv.ParseFloat(spl[1], 64)
			cluster := r.FindString(match)
			hostname := r3.FindString(match)

			fmt.Println("")
			fmt.Println(cluster)
			fmt.Println(hostname)
			fmt.Println("Total GB:", val/1024/1024)
		}
	}
	//Free size
	for _, row := range strings.Split(data, "\n") {
                match := r4.FindString(row)
                if match != "" {
                        spl := strings.Split(match, " ")
                        val, _ := strconv.ParseFloat(spl[1], 64)
                        cluster := r.FindString(match)
                        hostname := r3.FindString(match)

                        fmt.Println("")
                        fmt.Println(cluster)
                        fmt.Println(hostname)
                        fmt.Println("Free GB:", val/1024/1024)
                }
        }

}
