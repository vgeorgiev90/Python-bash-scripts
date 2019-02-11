package functions

import (
	"fmt"
	"net/http"
	"io/ioutil"
	"strings"
)

func Health(ip string) {

	parts := []string{"http://", ip, ":9200", "/_cat/health?v"}
	url := strings.Join(parts, "")
	response, err := http.Get(url)
	if err != nil {
	   fmt.Println("Error reading response from server:", err)
	}

	text, err := ioutil.ReadAll(response.Body)
	response.Body.Close()

	fmt.Println(string(text))
}

func Indices(ip string) {

	parts := []string{"http://", ip, ":9200", "/_cat/indices?v"}
        url := strings.Join(parts, "")
        response, err := http.Get(url)
        if err != nil {
           fmt.Println("Error reading response from server:", err)
        }

        text, err := ioutil.ReadAll(response.Body)
        response.Body.Close()

        fmt.Println(string(text))

}

func Thread_pool(ip string) {

	parts := []string{"http://", ip, ":9200", "/_nodes/stats/thread_pool?pretty=true"}
        url := strings.Join(parts, "")
        response, err := http.Get(url)
        if err != nil {
           fmt.Println("Error reading response from server:", err)
        }

        text, err := ioutil.ReadAll(response.Body)
        response.Body.Close()

        fmt.Println(string(text))
}

func Delete(ip, index string) {

	//Define client
	client := &http.Client{}

	parts := []string{"http://", ip, ":9200", "/", index}
        url := strings.Join(parts, "")

	//Create request
        request, err := http.NewRequest("DELETE", url, nil)
        if err != nil {
           fmt.Println("Error reading response from server:", err)
        }
	//fetch request
	response, err := client.Do(request)
	if err != nil {
	   fmt.Println(err)
	}
	defer response.Body.Close()
	//Read response
	text, err := ioutil.ReadAll(response.Body)
	if err != nil {
	   fmt.Println(err)
	}

	fmt.Println(string(text))
}
